from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.core.deps import CurrentUser, DbSession
from app.models.entities import Build, Deployment, DeploymentStatus, Project
from app.services.docker_service import container_logs, stop_container

router = APIRouter(tags=["operations"])

@router.get("/deployments/{deployment_id}")
def get_deployment(deployment_id: int, db: DbSession, user: CurrentUser):
    deployment = db.scalar(select(Deployment).join(Project).where(Deployment.id == deployment_id, Project.owner_id == user.id))
    if not deployment: raise HTTPException(404, "Deployment not found")
    return deployment


@router.get("/builds/{build_id}/logs")
def build_logs(build_id: int, db: DbSession, user: CurrentUser):
    build = db.scalar(select(Build).join(Project).where(Build.id == build_id, Project.owner_id == user.id))
    if not build: raise HTTPException(404, "Build not found")
    return {"build_id": build.id, "logs": build.logs}


@router.get("/deployments/{deployment_id}/logs")
def deployment_logs(deployment_id: int, db: DbSession, user: CurrentUser):
    deployment = db.scalar(select(Deployment).join(Project).where(Deployment.id == deployment_id, Project.owner_id == user.id))
    if not deployment: raise HTTPException(404, "Deployment not found")
    return {"deployment_id": deployment.id, "logs": container_logs(f"cloudforge-project-{deployment.project_id}-deployment-{deployment.id}").output}


@router.post("/deployments/{deployment_id}/stop")
def stop_deployment(deployment_id: int, db: DbSession, user: CurrentUser):
    deployment = db.scalar(select(Deployment).join(Project).where(Deployment.id == deployment_id, Project.owner_id == user.id))
    if not deployment: raise HTTPException(404, "Deployment not found")
    result = stop_container(f"cloudforge-project-{deployment.project_id}-deployment-{deployment.id}")
    if result.ok:
        deployment.status = DeploymentStatus.STOPPED
        db.commit()
    return {"status": deployment.status, "message": result.output}
