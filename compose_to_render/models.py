# compose_to_render/models.py
"""
Pydantic-style data classes for representing the structure of
docker-compose.yml and render.yaml files.

These models provide type safety, validation, and a clear schema for the
translation logic. Using dataclasses with strict type hints is non-negotiable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Union


# --------------------------------------------------------------------------
# Render Blueprint Models
# --------------------------------------------------------------------------

@dataclass
class RenderImage:
    """Defines the container image for a Render service."""
    url: str
    owner: str = "docker"


@dataclass
class RenderEnvVar:
    """Defines an environment variable for a Render service."""
    key: str
    value: Optional[str] = None
    fromEnvGroup: Optional[str] = None
    sync: Optional[bool] = None


@dataclass
class RenderDisk:
    """Defines a persistent disk for a Render service."""
    name: str
    mountPath:str
    sizeGB: Optional[int] = None


@dataclass
class RenderBuildFilter:
    """Defines paths to watch for auto-deploys."""
    paths: List[str] = field(default_factory=list)
    ignoredPaths: List[str] = field(default_factory=list)


@dataclass
class RenderHealthCheck:
    """Defines a TCP or HTTP health check for a Render service."""
    path: str
    initialDelaySEconds: int = 5


@dataclass
class RenderService:
    """Represents a single service in a render.yaml blueprint."""
    name: str
    type: Literal["web", "pserv", "cron", "static"]
    autoDeploy: bool = True
    image: Optional[RenderImage] = None
    start_command: str | None = None
    envVars: List[RenderEnvVar] = field(default_factory=list)
    disks: List[RenderDisk] = field(default_factory=list)
    buildFilter: Optional[RenderBuildFilter] = None
    healthCheck: Optional[RenderHealthCheck] = None
    # For web services
    ports: Optional[str] = None


@dataclass
class RenderBlueprint:
    """Represents the top-level structure of a render.yaml file."""
    services: List[RenderService] = field(default_factory=list)


# --------------------------------------------------------------------------
# Docker Compose Models
# --------------------------------------------------------------------------

@dataclass
class DockerComposeBuild:
    """Represents the 'build' context in a docker-compose service."""
    context: str
    dockerfile: Optional[str] = None


@dataclass
class DockerComposeHealthCheck:
    """Represents the 'healthcheck' in a docker-compose service."""
    test: List[str]
    interval: Optional[str] = None
    timeout: Optional[str] = None
    retries: Optional[int] = None
    start_period: Optional[str] = None


@dataclass
class DockerComposeService:
    """Represents a single service in a docker-compose.yml file."""
    image: Optional[str] = None
    build: Union[str, DockerComposeBuild, None] = None
    command: Union[str, List[str], None] = None
    ports: List[str] = field(default_factory=list)
    environment: Union[Dict[str, Optional[str]], List[str], None] = None
    env_file: Union[str, List[str], None] = None
    volumes: List[str] = field(default_factory=list)
    healthcheck: Optional[DockerComposeHealthCheck] = None
    depends_on: Union[List[str], Dict[str, Any], None] = None


@dataclass
class DockerComposeConfig:
    """Represents the top-level structure of a docker-compose.yml file."""
    services: Dict[str, DockerComposeService] = field(default_factory=dict)
    volumes: Dict[str, Any] = field(default_factory=dict)