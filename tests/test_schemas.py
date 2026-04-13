import pytest
from pydantic import ValidationError
from app.schemas import UserCreate


def test_valid_user_create():
    u = UserCreate(
        username="valid_user",
        email="valid@example.com",
        password="StrongPass1",
    )
    assert u.username == "valid_user"


def test_short_username_rejected():
    with pytest.raises(ValidationError):
        UserCreate(username="ab", email="e@e.com", password="StrongPass1")


def test_invalid_email_rejected():
    with pytest.raises(ValidationError):
        UserCreate(username="validuser", email="not-an-email", password="StrongPass1")


def test_weak_password_no_uppercase():
    with pytest.raises(ValidationError):
        UserCreate(username="validuser", email="e@e.com", password="weakpassword1")


def test_weak_password_no_digit():
    with pytest.raises(ValidationError):
        UserCreate(username="validuser", email="e@e.com", password="WeakPassword")


def test_weak_password_too_short():
    with pytest.raises(ValidationError):
        UserCreate(username="validuser", email="e@e.com", password="Sh1")
