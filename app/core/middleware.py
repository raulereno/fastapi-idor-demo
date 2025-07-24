"""
Middleware for PostgreSQL Row-Level Security (RLS)
"""
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import text
from fastapi import Request
from app.core.database import SessionLocal


class SetAppUserMiddleware(BaseHTTPMiddleware):
    """
    Middleware to set PostgreSQL app.user_id parameter for RLS
    Mitigation #2: Database-enforced authorization
    """
    
    async def dispatch(self, request: Request, call_next):
        # Extract user_id from request state (set by authentication)
        user_id = getattr(request.state, "user_id", None)
        
        if user_id:
            # Set PostgreSQL parameter for RLS
            db = SessionLocal()
            try:
                # Set the app.user_id parameter for this session
                db.execute(text("SET app.user_id = :uid"), {"uid": user_id})
                db.commit()
            except Exception as e:
                # Log error but don't fail the request
                print(f"Error setting app.user_id: {e}")
            finally:
                db.close()
        
        response = await call_next(request)
        return response


class UserIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract user_id from JWT and set it in request state
    """
    
    async def dispatch(self, request: Request, call_next):
        # Extract user_id from Authorization header if present
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from app.core.security_enhanced import get_current_user_id
                from fastapi.security import HTTPAuthorizationCredentials
                
                # Create a mock credentials object
                creds = HTTPAuthorizationCredentials(
                    scheme="Bearer",
                    credentials=auth_header.split(" ")[1]
                )
                
                # Extract user_id
                user_id = get_current_user_id(creds)
                request.state.user_id = user_id
            except Exception:
                # Invalid token, continue without user_id
                pass
        
        response = await call_next(request)
        return response 