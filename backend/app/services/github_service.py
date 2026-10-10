import re
from dataclasses import dataclass

import httpx

from app.core.config import get_settings

GITHUB_RE = re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$")


@dataclass(frozen=True)
class RepositoryRef:
    owner: str
    name: str


def parse_repository_url(url: str) -> RepositoryRef:
    match = GITHUB_RE.match(url)
    if not match:
        raise ValueError("Only public HTTPS GitHub repository URLs are supported for builds")
    return RepositoryRef(*match.groups())


def metadata(url: str) -> dict:
    ref = parse_repository_url(url)
    headers = {"Accept": "application/vnd.github+json"}
    if get_settings().github_token:
        headers["Authorization"] = f"Bearer {get_settings().github_token}"
    response = httpx.get(f"https://api.github.com/repos/{ref.owner}/{ref.name}", headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    return {"full_name": data["full_name"], "default_branch": data["default_branch"], "description": data.get("description")}
