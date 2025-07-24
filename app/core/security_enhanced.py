"""
Enhanced security utilities with JWT authentication and user ID extraction
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.core.config import settings

# HTTP Bearer authentication
bearer = HTTPBearer()


def get_current_user_id(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> int:
    """
    Extract user ID from JWT token
    Returns user_id for route-level owner checks
    """
    try:
        payload = jwt.decode(creds.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user_id found"
            )
        return int(user_id)
    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def get_current_user_with_id(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    """
    Get both user object and user_id for comprehensive checks
    """
    from app.core.database import get_db
    from app.models.user import User
    from sqlalchemy.orm import Session
    
    user_id = get_current_user_id(creds)
    
    # Get database session
    db = next(get_db())
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user, user_id
    finally:
        db.close()


def verify_ownership(resource_owner_id: int, current_user_id: int, is_admin: bool = False) -> bool:
    """
    Verify if current user can access the resource
    """
    # User can access their own resources
    if resource_owner_id == current_user_id:
        return True
    
    # Admins can access any resource
    if is_admin:
        return True
    
    return False 