"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Core app schemas

class Subject(BaseModel):
    """
    Collection: subject
    Represents an academic subject (e.g., Economics, Book-keeping & Accountancy)
    """
    title: str = Field(..., description="Subject name")
    code: Optional[str] = Field(None, description="Optional board code for the subject")
    std: str = Field("12", description="Standard/grade, e.g., '12'")
    board: str = Field("Maharashtra State Board", description="Education board")
    medium: str = Field("English", description="Medium of instruction")

class Chapter(BaseModel):
    """
    Collection: chapter
    Represents a chapter within a subject
    """
    subject_id: str = Field(..., description="Reference to Subject document _id as string")
    number: int = Field(..., ge=1, description="Chapter number")
    title: str = Field(..., description="Chapter title")
    description: Optional[str] = Field(None, description="Short summary or notes")
    syllabus_year: Optional[str] = Field("2024-25", description="Syllabus academic year")

# Example schemas kept for reference (not used by the app but harmless)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
