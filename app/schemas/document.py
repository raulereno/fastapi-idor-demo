"""
Pydantic schemas for Document validation
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DocumentBase(BaseModel):
    """Base schema for documents"""
    title: str
    content: str


class DocumentCreate(DocumentBase):
    """Schema for creating a document"""
    pass


class DocumentResponse(DocumentBase):
    """Schema for document response"""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentUpdate(BaseModel):
    """Schema for updating a document"""
    title: Optional[str] = None
    content: Optional[str] = None 