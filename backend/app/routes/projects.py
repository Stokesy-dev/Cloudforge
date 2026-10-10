from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import CurrentUser, DbSession
from app.models.entities import Build, BuildStatus, Deployment, DeploymentStatus, Project
from app.schemas import BuildRead, DeploymentCreate, DeploymentRead, ProjectCreate, ProjectRead, ProjectUpdate
from app.services.build_service import run_build
from app.services.docker_service import start_container, stop_container

router = APIRouter(prefix="/projects", tags=["projects"])


def owned(db: DbSession, project_id: int, user_id: int) -> Project:
    project = db.scalar(select(Project).where(Project.id == project_id, Project.owner_id == user_id))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=ProjectRead, status_code=201)
def create(payload: ProjectCreate, db: DbSession, user: CurrentUser):
    project = Project(**payload.model_dump(), owner_id=user.id)
    db.add(project); db.commit(); db.refresh(project)
    return project


@router.get("", response_model=list[ProjectRead])
def list_projects(db: DbSession, user: CurrentUser):
    return db.scalars(select(Project).where(Project.owner_id == user.id).order_by(Project.created_at.desc())).all()


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: DbSession, user: CurrentUser):
    return owned(db, project_id, user.id)


@router.patch("/{project_id}", response_model=ProjectRead)
def update(project_id: int, payload: ProjectUpdate, db: DbSession, user: CurrentUser):
    project = owned(db, project_id, user.id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(project, key, value)
    db.commit(); db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete(project_id: int, db: DbSession, user: CurrentUser):
    project = owned(db, project_id, user.id); db.delete(project); db.commit()


@router.post("/{project_id}/builds", response_model=BuildRead, status_code=201)
def build(project_id: int, db: DbSession, user: CurrentUser):
    project = owned(db, project_id, user.id)
    record = Build(project_id=project.id, status=BuildStatus.QUEUED)
    db.add(record); db.commit(); db.refresh(record)
    return run_build(db, project, record)


@router.get("/{project_id}/builds", response_model=list[BuildRead])
def builds(project_id: int, db: DbSession, user: CurrentUser):
    owned(db, project_id, user.id)
    return db.scalars(select(Build).where(Build.project_id == project_id).order_by(Build.id.desc())).all()


@router.get("/{project_id}/deployments", response_model=list[DeploymentRead])
def deployments(project_id: int, db: DbSession, user: CurrentUser):
    owned(db, project_id, user.id)
    return db.scalars(select(Deployment).where(Deployment.project_id == project_id).order_by(Deployment.id.desc())).all()


@router.post("/{project_id}/deploy", response_model=DeploymentRead, status_code=201)
def deploy(project_id: int, payload: DeploymentCreate, db: DbSession, user: CurrentUser):
    project = owned(db, project_id, user.id)
    build_record = db.scalar(select(Build).where(Build.id == payload.build_id, Build.project_id == project.id))
    if not build_record or build_record.status != BuildStatus.SUCCESS or not build_record.image_name or not build_record.image_tag:
        raise HTTPException(status_code=400, detail="A successful project build is required")
    image = f"{build_record.image_name}:{build_record.image_tag}"
    deployment = Deployment(project_id=project.id, build_id=build_record.id, environment=payload.environment, image_name=image, status=DeploymentStatus.DEPLOYING)
    db.add(deployment); db.commit(); db.refresh(deployment)
    result = start_container(image, f"cloudforge-project-{project.id}-deployment-{deployment.id}")
    if result.ok:
        deployment.status = DeploymentStatus.RUNNING; deployment.container_id = result.value
    else:
        deployment.status = DeploymentStatus.FAILED
    db.commit(); db.refresh(deployment)
    return deployment
