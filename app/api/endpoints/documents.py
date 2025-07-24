"""
Document endpoints demonstrating IDOR mitigations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security_enhanced import get_current_user_id, get_current_user_with_id
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentUpdate
from app.services.document_service import DocumentService

router = APIRouter()


# ============================================================================
# VULNERABLE ENDPOINTS (for comparison)
# ============================================================================

@router.get("/vulnerable/{document_id}", response_model=DocumentResponse)
async def get_document_vulnerable(document_id: int, db: Session = Depends(get_db)):
    """
    VULNERABLE ENDPOINT - No ownership check
    Any user can access any document by changing the document_id
    """
    document = DocumentService.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


# ============================================================================
# MITIGATION #1: Route-level owner check
# ============================================================================

@router.get("/secure/{document_id}", response_model=DocumentResponse)
async def get_document_secure(
    document_id: int, 
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    SECURE ENDPOINT - Mitigation #1: Route-level owner check
    Explicit ownership verification in the route handler
    """
    # Get current user to check admin status
    current_user = db.query(User).filter(User.id == current_user_id).first()
    is_admin = current_user.role == "admin" if current_user else False
    
    document = DocumentService.get_document_with_ownership_check(
        db, document_id, current_user_id, is_admin
    )
    
    if not document:
        # Unified 404 prevents user enumeration
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.get("/secure/me", response_model=List[DocumentResponse])
async def get_my_documents(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get current user's documents"""
    documents = DocumentService.get_user_documents(db, current_user_id)
    return documents


# ============================================================================
# MITIGATION #2: PostgreSQL RLS (demonstration)
# ============================================================================

@router.get("/rls/{document_id}", response_model=DocumentResponse)
async def get_document_rls(
    document_id: int, 
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    RLS ENDPOINT - Mitigation #2: PostgreSQL Row-Level Security
    Database-enforced authorization (requires PostgreSQL with RLS enabled)
    
    Note: This is a demonstration. In a real PostgreSQL setup, you would:
    1. Enable RLS: ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
    2. Create policy: CREATE POLICY doc_owner_select ON documents FOR SELECT USING (owner_id = current_setting('app.user_id')::int);
    3. Use the middleware to set app.user_id parameter
    """
    # For SQLite demonstration, we still use application-level checks
    # In PostgreSQL, RLS would handle this automatically
    current_user = db.query(User).filter(User.id == current_user_id).first()
    is_admin = current_user.role == "admin" if current_user else False
    
    document = DocumentService.get_document_with_ownership_check(
        db, document_id, current_user_id, is_admin
    )
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


# ============================================================================
# DOCUMENT MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/", response_model=DocumentResponse)
async def create_document(
    document_data: DocumentCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new document"""
    document = DocumentService.create_document(db, document_data, current_user_id)
    return document


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update a document with ownership check"""
    current_user = db.query(User).filter(User.id == current_user_id).first()
    is_admin = current_user.role == "admin" if current_user else False
    
    document = DocumentService.update_document(
        db, document_id, document_data, current_user_id, is_admin
    )
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a document with ownership check"""
    current_user = db.query(User).filter(User.id == current_user_id).first()
    is_admin = current_user.role == "admin" if current_user else False
    
    success = DocumentService.delete_document(
        db, document_id, current_user_id, is_admin
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": "Document deleted successfully"}


# ============================================================================
# DEMO ENDPOINTS
# ============================================================================

@router.get("/demo/setup")
async def setup_demo_documents(db: Session = Depends(get_db)):
    """Create demo documents for testing"""
    created_docs = DocumentService.create_demo_documents(db)
    return {
        "message": "Demo documents created",
        "documents": created_docs,
        "document_ids": [1, 2, 3, 4, 5],
        "note": "Use these IDs to test IDOR vulnerability: /vulnerable/1, /vulnerable/2, etc."
    } 