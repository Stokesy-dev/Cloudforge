from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import Base, engine
from app.routes import auth, operations, projects

Base.metadata.create_all(bind=engine)
app = FastAPI(title="CloudForge API", description="A lightweight local developer PaaS", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://frontend:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(operations.router, prefix="/api")


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}
