"""
Pytest configuration and shared fixtures for backend tests.
"""
import os
import pytest

# Set dummy environment variables BEFORE importing anything that uses database.py
os.environ.setdefault('DB_USER', 'test_user')
os.environ.setdefault('DB_PASSWORD', 'test_password')
os.environ.setdefault('DB_HOST', 'localhost')
os.environ.setdefault('DB_PORT', '5432')
os.environ.setdefault('DB_NAME', 'test_db')

# Create in-memory SQLite database for testing BEFORE importing main
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Import database module and replace its engine BEFORE importing main
# This prevents main.py from trying to connect to a real database
import database
database.engine = test_engine
database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Now import main - it will use our test engine
from main import app
from database import get_db, Base

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# Use the test_engine we created above
engine = test_engine


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
