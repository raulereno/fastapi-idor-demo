"""
User endpoints for authentication and basic user management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.user_service import UserService

router = APIRouter()


# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.get("/", response_model=List[UserResponse])
async def list_all_users(db: Session = Depends(get_db)):
    """List all users (for demonstration only)"""
    return UserService.get_all_users(db)


# ============================================================================
# DEMO ENDPOINTS
# ============================================================================

@router.get("/demo/setup")
async def setup_demo_data(db: Session = Depends(get_db)):
    """Create demo data"""
    created_users = UserService.create_demo_users(db)
    return {
        "message": "Demo data created",
        "users": created_users,
        "user_ids": [1, 2, 3, 4, 5],
        "note": "Users created for testing document endpoints"
    } 