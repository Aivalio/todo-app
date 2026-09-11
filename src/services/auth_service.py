"""Authentication service: password hashing, registration and login."""
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.models import User


# bcrypt context: handles hashing & verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- Validation constants ---
MIN_USERNAME_LENGTH = 3
MIN_PASSWORD_LENGTH = 6


# --- Password utilities ---

def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt.

    Args:
        password: The plain-text password.

    Returns:
        The bcrypt hash.
    """
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plain-text password against a bcrypt hash.

    Args:
        password: The plain-text password to check.
        password_hash: The stored bcrypt hash.

    Returns:
        True if the password matches, False otherwise.
    """
    return pwd_context.verify(password, password_hash)


# --- Validation helpers ---

def _validate_registration(username: str, email: str, password: str) -> None:
    """Validate registration fields. Raises ValueError on failure."""
    if len(username) < MIN_USERNAME_LENGTH:
        raise ValueError(f"Username must be at least {MIN_USERNAME_LENGTH} characters.")
    if "@" not in email or "." not in email:
        raise ValueError("Please enter a valid email address.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")


# --- User lookup ---

def get_user_by_username(session: Session, username: str) -> User | None:
    """Fetch a user by username.

    Args:
        session: Database session.
        username: The username to look up.

    Returns:
        The User instance, or None if not found.
    """
    return session.query(User).filter(User.username == username).first()


def get_user_by_email(session: Session, email: str) -> User | None:
    """Fetch a user by email.

    Args:
        session: Database session.
        email: The email to look up.

    Returns:
        The User instance, or None if not found.
    """
    return session.query(User).filter(User.email == email).first()


# --- Registration & login ---

def register_user(session: Session, username: str, email: str, password: str) -> User:
    """Register a new user.

    Args:
        session: Database session.
        username: Desired username.
        email: User's email.
        password: Plain-text password.

    Returns:
        The newly created User.

    Raises:
        ValueError: On validation failure or duplicate username/email.
    """
    username = username.strip()
    email = email.strip().lower()

    _validate_registration(username, email, password)

    if get_user_by_username(session, username):
        raise ValueError(f"Username '{username}' is already taken.")
    if get_user_by_email(session, email):
        raise ValueError(f"Email '{email}' is already registered.")

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate(session: Session, username: str, password: str) -> User | None:
    """Authenticate a user by username and password.

    Args:
        session: Database session.
        username: The username.
        password: Plain-text password.

    Returns:
        The User if credentials are valid, None otherwise.
    """
    user = get_user_by_username(session, username)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user