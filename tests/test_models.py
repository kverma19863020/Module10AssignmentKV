import pytest
from app.models import User


def test_password_hashing():
    plain = "SecurePass123"
    hashed = User.hash_password(plain)
    assert hashed != plain
    assert "$2b$" in hashed


def test_password_verification():
    plain = "MyPassword9!"
    u = User(
        username="tester",
        email="tester@example.com",
        hashed_password=User.hash_password(plain),
    )
    assert u.verify_password(plain) is True
    assert u.verify_password("wrongpassword") is False


def test_unique_fields_defined():
    cols = {c.name: c for c in User.__table__.columns}
    assert cols["username"].unique is True
    assert cols["email"].unique is True


def test_default_flags():
    u = User(
        username="u1",
        email="u1@example.com",
        hashed_password=User.hash_password("Password1"),
    )
    assert u.is_active is True or u.is_active is None  # default applied on DB insert
    assert u.is_admin is False or u.is_admin is None
