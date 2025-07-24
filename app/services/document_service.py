"""
Document service with ownership checks and RLS support
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.core.security_enhanced import verify_ownership


class DocumentService:
    """Service for document operations with ownership verification"""
    
    @staticmethod
    def create_document(db: Session, document_data: DocumentCreate, owner_id: int) -> Document:
        """Create a new document"""
        db_document = Document(
            title=document_data.title,
            content=document_data.content,
            owner_id=owner_id
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document
    
    @staticmethod
    def get_document_by_id(db: Session, document_id: int) -> Optional[Document]:
        """Get document by ID (for RLS demonstration)"""
        return db.query(Document).filter(Document.id == document_id).first()
    
    @staticmethod
    def get_document_with_ownership_check(
        db: Session, 
        document_id: int, 
        current_user_id: int, 
        is_admin: bool = False
    ) -> Optional[Document]:
        """
        Get document with ownership verification
        Mitigation #1: Route-level owner check
        """
        document = DocumentService.get_document_by_id(db, document_id)
        if not document:
            return None
        
        # Check ownership
        if not verify_ownership(document.owner_id, current_user_id, is_admin):
            return None
        
        return document
    
    @staticmethod
    def get_user_documents(db: Session, user_id: int) -> List[Document]:
        """Get all documents owned by a user"""
        return db.query(Document).filter(Document.owner_id == user_id).all()
    
    @staticmethod
    def update_document(
        db: Session, 
        document_id: int, 
        document_data: DocumentUpdate, 
        current_user_id: int,
        is_admin: bool = False
    ) -> Optional[Document]:
        """Update document with ownership check"""
        document = DocumentService.get_document_with_ownership_check(
            db, document_id, current_user_id, is_admin
        )
        if not document:
            return None
        
        # Update fields
        if document_data.title is not None:
            document.title = document_data.title
        if document_data.content is not None:
            document.content = document_data.content
        
        db.commit()
        db.refresh(document)
        return document
    
    @staticmethod
    def delete_document(
        db: Session, 
        document_id: int, 
        current_user_id: int,
        is_admin: bool = False
    ) -> bool:
        """Delete document with ownership check"""
        document = DocumentService.get_document_with_ownership_check(
            db, document_id, current_user_id, is_admin
        )
        if not document:
            return False
        
        db.delete(document)
        db.commit()
        return True
    
    @staticmethod
    def create_demo_documents(db: Session) -> List[str]:
        """Create demo documents for testing"""
        demo_documents = [
            {"id": 1, "title": "Alice's Secret Document", "content": "This is Alice's private content", "owner_id": 1},
            {"id": 2, "title": "Bob's Work Notes", "content": "Bob's confidential work notes", "owner_id": 2},
            {"id": 3, "title": "Charlie's Personal Diary", "content": "Charlie's personal thoughts", "owner_id": 3},
            {"id": 4, "title": "Diana's Project Plan", "content": "Diana's project planning", "owner_id": 4},
            {"id": 5, "title": "Admin's System Notes", "content": "System administration notes", "owner_id": 5},
        ]
        
        created_docs = []
        for doc_data in demo_documents:
            existing_doc = DocumentService.get_document_by_id(db, doc_data["id"])
            if not existing_doc:
                new_doc = Document(
                    id=doc_data["id"],
                    title=doc_data["title"],
                    content=doc_data["content"],
                    owner_id=doc_data["owner_id"]
                )
                db.add(new_doc)
                created_docs.append(doc_data["title"])
            else:
                created_docs.append(f"{doc_data['title']} (already exists)")
        
        db.commit()
        return created_docs 