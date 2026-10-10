import shutil
import os
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.entities import Build, BuildStatus, Project
from app.services.docker_service import build_image


def run_build(db: Session, project: Project, build: Build) -> Build:
    build.status = BuildStatus.BUILDING
    build.started_at = datetime.now(UTC)
    db.commit()
    if not project.repository_url:
        return _fail(db, build, "Project has no GitHub repository configured")
    os.makedirs(get_settings().workspace_dir, exist_ok=True)
    workdir = Path(tempfile.mkdtemp(prefix="cloudforge-", dir=get_settings().workspace_dir))
    try:
        clone = subprocess.run(["git", "clone", "--depth", "1", "--branch", project.default_branch, project.repository_url, str(workdir / "repo")], capture_output=True, text=True, timeout=180, check=False)
        build.logs = (clone.stdout + "\n" + clone.stderr).strip()
        if clone.returncode != 0:
            return _fail(db, build, build.logs)
        repo = workdir / "repo"
        if not (repo / "Dockerfile").is_file():
            return _fail(db, build, "No Dockerfile found in repository")
        sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, check=False).stdout.strip()
        build.commit_sha = sha
        build.image_name = f"cloudforge/{project.name.lower().replace(' ', '-') }"
        build.image_tag = f"build-{build.id}"
        result = build_image(str(repo), f"{build.image_name}:{build.image_tag}")
        build.logs += "\n" + result.output
        if not result.ok:
            return _fail(db, build, build.logs)
        build.status = BuildStatus.SUCCESS
        build.completed_at = datetime.now(UTC)
        db.commit()
        db.refresh(build)
        return build
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def _fail(db: Session, build: Build, logs: str) -> Build:
    build.status = BuildStatus.FAILED
    build.logs = logs
    build.completed_at = datetime.now(UTC)
    db.commit()
    db.refresh(build)
    return build
