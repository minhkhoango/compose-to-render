# compose_to_render/translator.py
"""
The core translation logic.

This module contains the Translator class that takes a DockerComposeConfig
object and converts it into a RenderBlueprint object.
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple, Literal

from .models import (
    DockerComposeBuild,
    DockerComposeConfig,
    DockerComposeService,
    RenderBlueprint,
    RenderBuildFilter,
    RenderDisk,
    RenderEnvVar,
    RenderHealthCheck,
    RenderImage,
    RenderService,
)


class Translator:
    """
    Handles the conversion from Docker Compose configuration to a Render Blueprint.
    """

    def __init__(self, compose_config: DockerComposeConfig) -> None:
        self.compose_config = compose_config
        self.warnings: list[str] = []

    def translate(self) -> RenderBlueprint:
        """Executes the full translation logic."""
        blueprint = RenderBlueprint()
        for service_name, compose_service in self.compose_config.services.items():
            render_service = self._translate_service(service_name, compose_service)
            blueprint.services.append(render_service)
        
        return blueprint

    def _translate_service(
        self, name: str, service: DockerComposeService
    )-> RenderService:
        """Translates a single Docker Compose service to a Render service."""
        service_type, ports = self._determine_service_type_and_ports(service)
        image = self._translate_image(service)
        dockerfile_path, build_filter = self._translate_build_info(service, name)

        # A service must have an image OR a build context, not both.
        if image and (dockerfile_path or build_filter):
            self.warnings.append(
                f"Service '{name}' has both an image and a build context. "
                "Render will prioritize the image. The build context was ignored."
            )
            dockerfile_path = None
            build_filter = None

        return RenderService(
            name=name,
            type=service_type,
            autoDeploy=True,
            image=image,
            dockerfilePath=dockerfile_path,
            startCommand=self._translate_command(service),
            envVars=self._translate_env_vars(service, name),
            disks=self._translate_volumes(service, name),
            healthCheck=self._transfer_healthcheck(service, name),
            ports=ports
        )

    def _translate_build_info(
        self, service: DockerComposeService, service_name: str,
    )-> Tuple[Optional[str], Optional[RenderBuildFilter]]:
        """Translates the build context into a dockerfilePath and buildFilter."""
        if not service.build:
            return None, None

        build_context = ""
        dockerfile = "Dockerfile"

        if isinstance(service.build, str):
            build_context = service.build
        elif isinstance(service.build, dict):
            # This handles the object form of 'build'
            build_data = DockerComposeBuild(**service.build)
            build_context = build_data.context
            if build_data.dockerfile:
                dockerfile = build_data.dockerfile
        elif service.build:
            build_context = service.build.context
            if service.build.dockerfile:
                dockerfile = service.build.dockerfile
        else:
            self.warnings.append(f"Service '{service_name}': Invalid 'build' format encountered.")
            return None, None

        # Create a clean path for the dockerfile
        dockerfile_path = str(Path(build_context) / dockerfile)

        # Create a build filter to watch for changes in the context directory
        build_filter = RenderBuildFilter(paths=[f"{build_context}/**"])

        return dockerfile_path, build_filter
    
    def _determine_service_type_and_ports(
        self, service: DockerComposeService
    )-> Tuple[Literal['web', 'pserv', 'cron', 'static'], Optional[str]]:
        """
        Determines the Render service type based on exposed ports.
        Render classifies services with exposed ports as Web Services.
        """
        if not service.ports:
            return "pserv", None
        
        # Extract only the container port (the second part)
        container_ports: List[str] = []
        for port_mapping in service.ports:
            parts = str(port_mapping).split(":")
            container_port = parts[-1]
            if container_port.isdigit():
                container_ports.append(container_port)
        
        if container_ports:
            # We are choosing a 'web' service type.
            # It's a reasonable assumption for services that expose ports.
            return "web", ",".join(container_ports)
        
        return "pserv", None
    
    def _translate_image(self, service: DockerComposeService)-> Optional[RenderImage]:
        """Translates the image field."""
        if service.image:
            return RenderImage(url=service.image)
        return None

    def _translate_command(self, service: DockerComposeService) -> Optional[str]:
        """Translates the command field, handling both string and list formats."""
        if not service.command:
            return None
        if isinstance(service.command, list):
            # Join list into a single string, assuming shell-like execution
            return " ".join(service.command)
        return service.command

    def _translate_env_vars(self, service: DockerComposeService, service_name: str) -> List[RenderEnvVar]:
        """Translates environment variables from dict, list, and env_file."""
        env_vars: List[RenderEnvVar] = []
        if isinstance(service.environment, dict):
            for key, value in service.environment.items():
                env_vars.append(RenderEnvVar(key=key, value=str(value) if value is not None else ""))
        elif isinstance(service.environment, list):
            for item in service.environment:
                key, value = item.split("=", 1)
                env_vars.append(RenderEnvVar(key=key, value=value))

        # We don't read the env_file, just point to it. This is a design choice.
        # The user's .env file is local, but Render needs to be told to use a file.
        # We will add a warning that they need to create this file in Render.
        if service.env_file:
            files = [service.env_file] if isinstance(service.env_file, str) else service.env_file
            for file_path in files:
                self.warnings.append(
                    f"Service '{service_name}': env_file '{file_path}' is used. "
                    f"Ensure you create a corresponding secret file in Render."
                )
        return env_vars

    def _translate_volumes(self, service: DockerComposeService, service_name: str)-> List[RenderDisk]:
        """
        Translates Docker Compose volumes to Render Disks.
        - Named volumes become persistent disks.
        - Bind mounts (host paths) are ignored with a warning.
        """
        disks: List[RenderDisk] = []
        for volume in service.volumes:
            parts = volume.split(":")
            if len(parts) < 2:
                self.warnings.append(f"Volume '{volume}' has an invalid format and was ignored.")
                continue

            source, mount_path = parts[0], parts[1]

            # Check if it's a named volume defined in the top-level volumes key
            if source in self.compose_config.volumes:
                disks.append(RenderDisk(name=source, mountPath=mount_path))
            else:
                # This is likely a bind mount (e.g., './:/app'). This is a critical warning.
                self.warnings.append(
                    f"Service '{service_name}': Bind mount '{volume}' was ignored. Render does not support mounting host paths. "
                    f"Use Render Disks for persistent storage."
                )
        return disks

    def _transfer_healthcheck(self, service: DockerComposeService, service_name: str) -> Optional[RenderHealthCheck]:
        """
        Translates Docker healthcheck to a Render health check.
        Render only supports a simple path check, so we extract it with a regex.
        This is an opinionated, best-effort translation.
        """
        if not service.healthcheck:
            return None
        
        test_list = []
        if isinstance(service.healthcheck, dict):
            test_list = service.healthcheck.get("test", [])
        else: # It's a DockerComposeHealthCheck object
            test_list = service.healthcheck.test

        if not test_list:
            return None

        # Example: "CMD-SHELL", "curl -f http://localhost/health || exit 1"
        test_command = " ".join(test_list)

        # Look for a URL path in the healthcheck command.
        match = re.search(r"https?://localhost(?::\d+)?(/[\w/-]*)", test_command)
        if match:
            path = match.group(1)
            return RenderHealthCheck(path=path)

        self.warnings.append(
            f"Service '{service_name}': Could not translate complex healthcheck: '{test_command}'. "
            f"Only simple HTTP path checks are supported."
        )
        return None

    