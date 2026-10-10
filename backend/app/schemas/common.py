from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    repository_url: str | None = None
    default_branch: str = Field(default="main", min_length=1, max_length=120)

    @field_validator("repository_url")
    @classmethod
    def validate_repo(cls, value: str | None) -> str | None:
        if value and not (value.startswith("https://github.com/") or value.startswith("git@github.com:")):
            raise ValueError("repository_url must be a GitHub URL")
        return value


class ProjectUpdate(ProjectCreate):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    default_branch: str | None = Field(default=None, min_length=1, max_length=120)


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None
    repository_url: str | None
    default_branch: str
    created_at: datetime
    updated_at: datetime


class BuildRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    status: str
    image_name: str | None
    image_tag: str | None
    commit_sha: str | None
    logs: str
    started_at: datetime | None
    completed_at: datetime | None


class DeploymentCreate(BaseModel):
    build_id: int
    environment: str = Field(default="local", min_length=1, max_length=50)


class DeploymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    build_id: int
    status: str
    environment: str
    image_name: str
    container_id: str | None
    created_at: datetime
    started_at: datetime | None
    stopped_at: datetime | None
