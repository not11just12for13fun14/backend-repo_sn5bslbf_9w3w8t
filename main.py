import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Subject, Chapter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Utility to convert ObjectId to str

def serialize_doc(doc):
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["id"] = str(doc.pop("_id"))
    # Cast any ObjectId fields to string
    for k, v in list(doc.items()):
        if isinstance(v, ObjectId):
            doc[k] = str(v)
    return doc


@app.get("/")
def read_root():
    return {"message": "Maharashtra HSC Study API is running"}


@app.get("/test")
def test_database():
    resp = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": [],
    }
    try:
        if db is not None:
            resp["database"] = "✅ Available"
            resp["database_url"] = "✅ Set"
            try:
                resp["collections"] = db.list_collection_names()
                resp["database_name"] = db.name
                resp["connection_status"] = "Connected"
                resp["database"] = "✅ Connected & Working"
            except Exception as e:
                resp["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
    except Exception as e:
        resp["database"] = f"❌ Error: {str(e)[:80]}"
    return resp


# --- Seeding logic ---

class SeedResponse(BaseModel):
    subjects: int
    chapters: int


def seed_data_12_hsc_english():
    # Subjects
    subjects_list = [
        {"title": "Economics"},
        {"title": "Book-keeping & Accountancy"},
        {"title": "Secretarial Practice"},
        {"title": "Organization of Commerce & Management"},
    ]

    # Chapters per subject (latest typical HSC structure; can be updated upon confirmation)
    chapters_map = {
        "Economics": [
            "Introduction to Micro and Macro Economics",
            "Utility Analysis",
            "Demand Analysis",
            "Elasticity of Demand",
            "Production: Law of Variable Proportions and Returns to Scale",
            "Cost and Revenue Analysis",
            "Perfect Competition and Monopoly",
            "Monopolistic Competition and Oligopoly",
            "Index Numbers",
            "National Income",
            "Public Finance",
            "Money Market and Capital Market",
            "Foreign Trade",
        ],
        "Book-keeping & Accountancy": [
            "Introduction to Partnership Final Accounts",
            "Admission of Partner",
            "Retirement and Death of a Partner",
            "Dissolution of Partnership Firm",
            "Bills of Exchange",
            "Reconstitution of Partnership – Change in Profit-Sharing Ratio",
            "Single Entry System (Conversion Method)",
            "Consignment Accounts",
            "Joint Venture Accounts",
            "Accounting for Shares – Issue, Forfeiture and Reissue",
            "Company Final Accounts",
            "Analysis of Financial Statements",
        ],
        "Secretarial Practice": [
            "Introduction to Corporate Finance",
            "Sources of Corporate Finance",
            "Issue of Shares",
            "Issue of Debentures",
            "Deposits",
            "Corporate Finance – Other Sources",
            "Securities Market",
            "Stock Exchange",
            "Company Management",
            "Company Meetings – I",
            "Company Meetings – II",
            "Correspondence of Company Secretary",
        ],
        "Organization of Commerce & Management": [
            "Principles of Management",
            "Functions of Management",
            "Entrepreneurship Development",
            "Micro, Small and Medium Enterprises (MSMEs)",
            "Internal and External Trade",
            "Wholesale Trade",
            "Retail Trade",
            "International Trade",
            "Channels of Distribution",
            "Emerging Modes of Business",
            "Social Responsibilities of Business Organizations",
            "Consumer Protection",
        ],
    }

    created_subjects = 0
    created_chapters = 0

    # Ensure unique subjects (by title + std + board + medium)
    for subj in subjects_list:
        existing = db["subject"].find_one({
            "title": subj["title"],
            "std": "12",
            "board": "Maharashtra State Board",
            "medium": "English",
        })
        if existing:
            subject_id = existing["_id"]
        else:
            subject_id = ObjectId(create_document("subject", Subject(title=subj["title"]).model_dump()))
            created_subjects += 1

        chapter_titles = chapters_map[subj["title"]]
        for idx, title in enumerate(chapter_titles, start=1):
            found = db["chapter"].find_one({
                "subject_id": str(subject_id),
                "number": idx,
                "title": title,
            })
            if not found:
                create_document(
                    "chapter",
                    Chapter(
                        subject_id=str(subject_id),
                        number=idx,
                        title=title,
                        description=None,
                        syllabus_year="2024-25",
                    ),
                )
                created_chapters += 1

    return created_subjects, created_chapters


@app.post("/seed", response_model=SeedResponse)
def seed():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    s, c = seed_data_12_hsc_english()
    return SeedResponse(subjects=s, chapters=c)


# --- API endpoints ---

@app.get("/subjects")
def list_subjects(std: str = "12", board: str = "Maharashtra State Board", medium: str = "English"):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = get_documents("subject", {"std": std, "board": board, "medium": medium})
    return [serialize_doc(d) for d in docs]


@app.get("/subjects/{subject_id}/chapters")
def list_chapters(subject_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = get_documents("chapter", {"subject_id": subject_id}, limit=None)
    docs.sort(key=lambda x: x.get("number", 0))
    return [serialize_doc(d) for d in docs]


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
