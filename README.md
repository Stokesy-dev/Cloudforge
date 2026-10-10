# CloudForge

CloudForge is a lightweight developer PaaS for trusted local development. It registers users, manages owned projects, connects GitHub repositories, builds Docker images, starts local containers, and records build/deployment logs.

## Architecture

```text
React Dashboard
       |
       v
FastAPI REST API ---- MySQL
       |
  +----+-----+
  |          |
 GitHub    Docker Engine
```

Builds use the host Docker socket and should only target repositories trusted by the operator. This project tracks local Docker deployments; it does not claim Kubernetes or cloud deployment.

## Features

- JWT authentication with bcrypt password hashing
- Per-user project ownership enforcement
- GitHub HTTPS URL validation and metadata service
- Git clone and Dockerfile detection
- Docker image build output persisted to MySQL
- Local container deployment, stop, and logs
- Alembic migration and CI workflows
- Responsive React dashboard

## Tech stack and structure

Python 3.12, FastAPI, SQLAlchemy 2, MySQL 8, Alembic, React, Vite, Docker Compose, Pytest. `backend/app/` is split into core configuration/security, ORM models, Pydantic schemas, routes, and services. `frontend/src/` contains the dashboard.

## Setup

Prerequisites: Docker Desktop/Engine with Compose, Git, and a GitHub repository containing a Dockerfile for real builds.

```bash
cd cloudforge
cp .env.example .env
# Set a long JWT_SECRET_KEY in .env
docker compose up --build
```

Open http://localhost:5173. API docs are at http://localhost:8000/docs and health is at http://localhost:8000/health.

For local backend tests without Compose:

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

The test suite uses an isolated SQLite database and never touches the Compose MySQL instance.

## Example workflow

Register → create a project with an HTTPS GitHub URL → run Build → inspect image tag and logs → Deploy a successful build → inspect local container logs → Stop deployment.

## Future improvements

Kubernetes/cloud deployment, a container registry, WebSocket log streaming, GitHub webhooks, horizontal workers, and role-based access control.

## Resume bullets

- Built CloudForge, a FastAPI and React developer PaaS with JWT auth, per-user project isolation, GitHub repository integration, and a MySQL-backed deployment model.
- Implemented safe Git/Docker build orchestration with persisted status, commit SHA, image tags, captured logs, and deterministic cleanup of temporary workspaces.
- Added local Docker deployment lifecycle management, Alembic schema migrations, isolated Pytest API coverage, Docker Compose, and GitHub Actions CI.

## Interview questions

1. Why use JWTs and how would you revoke them?
2. How are project ownership checks enforced?
3. What are the risks of mounting the Docker socket?
4. How would you isolate builds from untrusted repositories?
5. Why use SQLAlchemy sessions per request?
6. How would you move builds to asynchronous workers?
7. How would GitHub webhooks trigger builds securely?
8. What happens if a Docker build times out?
9. How would you stream logs over WebSockets?
10. How would this evolve toward Kubernetes without changing the API contract?
