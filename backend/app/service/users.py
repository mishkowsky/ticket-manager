from sqlalchemy.orm import Session
from app.database import User
from app.auth import hash_password, verify_password
from fastapi import HTTPException
from typing import Optional


class UserService:
    @staticmethod
    def create_user(db: Session, username: str, password: str, is_admin: bool = False) -> User:
        if db.query(User).filter(User.username == username).first():
            raise HTTPException(status_code=400, detail="Пользователь с таким username уже существует")

        user = User(username=username, password_hash=hash_password(password), is_admin=is_admin)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        user = UserService.get_user_by_username(db, username)
        if user and verify_password(password, user.password_hash):
            return user
        return None
