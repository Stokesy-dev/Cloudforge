import os
os.environ["DATABASE_URL"] = "sqlite:///./test_cloudforge.db"
os.environ["JWT_SECRET_KEY"] = "test-secret"
import pytest
from fastapi.testclient import TestClient
from app.db.session import Base, engine
from app.main import app

@pytest.fixture(autouse=True)
def db():
    Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def client(): return TestClient(app)

@pytest.fixture
def auth_headers(client):
    client.post("/api/auth/register", json={"name":"Test User","email":"test@example.com","password":"password123"})
    token = client.post("/api/auth/login", json={"email":"test@example.com","password":"password123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
