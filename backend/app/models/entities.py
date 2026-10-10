from datetime import datetime
from enum import StrEnum
from typing import List

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class BuildStatus(StrEnum):
    QUEUED = "QUEUED"
    BUILDING = "BUILDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class DeploymentStatus(StrEnum):
    PENDING = "PENDING"
    DEPLOYING = "DEPLOYING"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    STOPPED = "STOPPED"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    projects: Mapped[List["Project"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    repository_url: Mapped[str] = mapped_column(String(500), nullable=True)
    default_branch: Mapped[str] = mapped_column(String(120), default="main")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    owner: Mapped[User] = relationship(back_populates="projects")
    builds: Mapped[List["Build"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    deployments: Mapped[List["Deployment"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Build(Base):
    __tablename__ = "builds"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(20), default=BuildStatus.QUEUED)
    image_name: Mapped[str] = mapped_column(String(255), nullable=True)
    image_tag: Mapped[str] = mapped_column(String(120), nullable=True)
    commit_sha: Mapped[str] = mapped_column(String(64), nullable=True)
    logs: Mapped[str] = mapped_column(Text, default="")
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    project: Mapped[Project] = relationship(back_populates="builds")
    deployments: Mapped[List["Deployment"]] = relationship(back_populates="build")


class Deployment(Base):
    __tablename__ = "deployments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    build_id: Mapped[int] = mapped_column(ForeignKey("builds.id", ondelete="RESTRICT"))
    status: Mapped[str] = mapped_column(String(20), default=DeploymentStatus.PENDING)
    environment: Mapped[str] = mapped_column(String(50), default="local")
    image_name: Mapped[str] = mapped_column(String(255))
    container_id: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    stopped_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    project: Mapped[Project] = relationship(back_populates="deployments")
    build: Mapped[Build] = relationship(back_populates="deployments")
