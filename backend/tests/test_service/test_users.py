import pytest
from sqlalchemy.orm import Session
from app.service import UserService
from app.auth import verify_password
from fastapi import HTTPException


class TestUserServiceCreate:
    def test_create_user_success(self, db_session: Session):
        user = UserService.create_user(db_session, "testuser", "password123")
        assert user.username == "testuser"
        assert user.is_admin is False
        assert verify_password("password123", user.password_hash)

    def test_create_user_as_admin(self, db_session: Session):
        user = UserService.create_user(db_session, "adminuser", "password123", is_admin=True)
        assert user.is_admin is True

    def test_create_duplicate_username_fails(self, db_session: Session):
        UserService.create_user(db_session, "testuser", "password123")

        with pytest.raises(HTTPException) as exc_info:
            UserService.create_user(db_session, "testuser", "password456")

        assert exc_info.value.status_code == 400
        assert "пользователь с таким username уже существует" in exc_info.value.detail.lower()

    def test_password_is_hashed(self, db_session: Session):
        user = UserService.create_user(db_session, "testuser", "plainpassword")

        assert user.password_hash != "plainpassword"
        assert len(user.password_hash) > len("plainpassword")


class TestUserServiceRetrieval:
    def test_get_user_by_username(self, db_session: Session):
        created_user = UserService.create_user(db_session, "testuser", "password123")
        retrieved_user = UserService.get_user_by_username(db_session, "testuser")

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == "testuser"

    def test_get_nonexistent_user_by_username(self, db_session: Session):
        user = UserService.get_user_by_username(db_session, "nonexistent")
        assert user is None

    def test_get_user_by_id(self, db_session: Session):
        created_user = UserService.create_user(db_session, "testuser", "password123")
        retrieved_user = UserService.get_user_by_id(db_session, created_user.id)

        assert retrieved_user is not None
        assert retrieved_user.username == "testuser"

    def test_get_nonexistent_user_by_id(self, db_session: Session):
        user = UserService.get_user_by_id(db_session, 999)
        assert user is None


class TestUserServiceAuthentication:
    def test_authenticate_user_success(self, db_session: Session):
        created_user = UserService.create_user(db_session, "testuser", "password123")
        authenticated_user = UserService.authenticate_user(db_session, "testuser", "password123")

        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id

    def test_authenticate_user_wrong_password(self, db_session: Session):
        UserService.create_user(db_session, "testuser", "password123")
        authenticated_user = UserService.authenticate_user(db_session, "testuser", "wrongpassword")

        assert authenticated_user is None

    def test_authenticate_nonexistent_user(self, db_session: Session):
        authenticated_user = UserService.authenticate_user(db_session, "nonexistent", "password123")
        assert authenticated_user is None
