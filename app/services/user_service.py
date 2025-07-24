"""
User service with business logic
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


class UserService:
    """Service for user operations"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if user already exists
        if UserService.get_user_by_username(db, user_data.username):
            raise ValueError("Username already registered")
        
        if UserService.get_user_by_email(db, user_data.email):
            raise ValueError("Email already registered")
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_all_users(db: Session) -> List[User]:
        """Get all users"""
        return db.query(User).all()
    
    @staticmethod
    def can_access_user(current_user: User, target_user_id: int, db: Session) -> bool:
        """Check if a user can access another user's data"""
        # User can access their own data
        if current_user.id == target_user_id:
            return True
        
        # Admins can access any user
        if current_user.role == "admin":
            return True
        
        return False
    
    @staticmethod
    def create_demo_users(db: Session) -> List[str]:
        """Create demo users"""
        demo_users = [
            {"id": 1, "username": "alice", "email": "alice@example.com", "password": "password123", "role": "user"},
            {"id": 2, "username": "bob", "email": "bob@example.com", "password": "password123", "role": "user"},
            {"id": 3, "username": "charlie", "email": "charlie@example.com", "password": "password123", "role": "user"},
            {"id": 4, "username": "diana", "email": "diana@example.com", "password": "password123", "role": "user"},
            {"id": 5, "username": "admin", "email": "admin@example.com", "password": "admin123", "role": "admin"},
        ]
        
        created_users = []
        for user_data in demo_users:
            existing_user = UserService.get_user_by_username(db, user_data["username"])
            if not existing_user:
                hashed_password = get_password_hash(user_data["password"])
                new_user = User(
                    id=user_data["id"],
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=hashed_password,
                    role=user_data["role"]
                )
                db.add(new_user)
                created_users.append(user_data["username"])
            else:
                created_users.append(f"{user_data['username']} (already exists)")
        
        db.commit()
        return created_users 