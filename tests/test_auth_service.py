"""Tests for the authentication service."""
import pytest

from src.services.auth_service import (
    authenticate,
    get_user_by_email,
    get_user_by_username,
    hash_password,
    register_user,
    verify_password,
)


# --- Password hashing ---

def test_hash_password_returns_bcrypt_hash():
    h = hash_password("secret")
    assert h.startswith("$2b$")


def test_hash_password_is_not_plaintext():
    h = hash_password("secret")
    assert h != "secret"


def test_verify_password_correct():
    h = hash_password("secret")
    assert verify_password("secret", h) is True


def test_verify_password_wrong():
    h = hash_password("secret")
    assert verify_password("wrong", h) is False


# --- Registration ---

def test_register_user_success(session):
    user = register_user(session, "alice", "alice@example.com", "secret123")
    assert user.id is not None
    assert user.username == "alice"
    assert user.email == "alice@example.com"
    assert user.password_hash != "secret123"


def test_register_user_trims_whitespace(session):
    user = register_user(session, "  alice  ", "  alice@example.com  ", "secret123")
    assert user.username == "alice"
    assert user.email == "alice@example.com"


def test_register_user_lowercases_email(session):
    user = register_user(session, "alice", "ALICE@Example.COM", "secret123")
    assert user.email == "alice@example.com"


def test_register_duplicate_username_raises(session):
    register_user(session, "alice", "alice@example.com", "secret123")
    with pytest.raises(ValueError, match="already taken"):
        register_user(session, "alice", "other@example.com", "secret456")


def test_register_duplicate_email_raises(session):
    register_user(session, "alice", "alice@example.com", "secret123")
    with pytest.raises(ValueError, match="already registered"):
        register_user(session, "bob", "alice@example.com", "secret456")


def test_register_short_username_raises(session):
    with pytest.raises(ValueError, match="at least 3"):
        register_user(session, "ab", "ab@example.com", "secret123")


def test_register_short_password_raises(session):
    with pytest.raises(ValueError, match="at least 6"):
        register_user(session, "alice", "alice@example.com", "abc")


def test_register_invalid_email_raises(session):
    with pytest.raises(ValueError, match="valid email"):
        register_user(session, "alice", "not-an-email", "secret123")


# --- Lookup ---

def test_get_user_by_username_found(session, sample_user):
    found = get_user_by_username(session, "alice")
    assert found is not None
    assert found.id == sample_user.id


def test_get_user_by_username_not_found(session):
    assert get_user_by_username(session, "nobody") is None


def test_get_user_by_email_found(session, sample_user):
    found = get_user_by_email(session, "alice@example.com")
    assert found is not None


# --- Authentication ---

def test_authenticate_success(session, sample_user):
    user = authenticate(session, "alice", "secret123")
    assert user is not None
    assert user.id == sample_user.id


def test_authenticate_wrong_password(session, sample_user):
    assert authenticate(session, "alice", "wrong") is None


def test_authenticate_unknown_user(session):
    assert authenticate(session, "nobody", "any") is None