from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from app.database import get_db, User
import bcrypt

security = HTTPBasic()


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def verify_credentials(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Verify user credentials and return the user object."""
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Неверные данные для авторизации",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return user


def verify_admin(user: User = Depends(verify_credentials)) -> User:
    """Verify that the authenticated user is an admin."""
    if not user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Требуются права администратора",
        )
    return user
