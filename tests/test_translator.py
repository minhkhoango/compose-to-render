# tests/test_translator.py
"""
Unit tests for the Translator class.

These tests ensure that the core translation logic works correctly for a
variety of Docker Compose configurations.
"""
from pathlib import Path
import pytest
from ruamel.yaml import YAML

from compose_to_render.models import DockerComposeConfig, DockerComposeService
from compose_to_render.translator import Translator

# Use a fixture to load the test docker-compose file once
@pytest.fixture(scope="module")
def simple_app_config() -> DockerComposeConfig:
    """Loads the simple-app.yml fixture and returns a DockerComposeConfig object."""
    yaml = YAML()
    path = Path(__file__).parent.parent / "fixtures" / "simple-app.yml"
    with open(path, 'r') as f:
        data = yaml.load(f)
    
    # A simplified manual deserialization for the test
    services: dict[str, DockerComposeService] = {name: DockerComposeService(**service_data) for name, service_data in data.get('services', {}).items()}
    volumes = data.get('volumes', {})
    return DockerComposeConfig(services=services, volumes=volumes)


def test_translator_initialization(simple_app_config: DockerComposeConfig) -> None:
    """Test that the Translator initializes correctly."""
    translator = Translator(simple_app_config)
    assert translator.compose_config is not None
    assert len(translator.compose_config.services) == 2


def test_translate_service_count(simple_app_config: DockerComposeConfig) -> None:
    """Test that the correct number of services are translated."""
    translator = Translator(simple_app_config)
    blueprint = translator.translate()
    assert len(blueprint.services) == 2


def test_translate_web_service(simple_app_config: DockerComposeConfig) -> None:
    """Test the translation of the 'web' service."""
    translator = Translator(simple_app_config)
    blueprint = translator.translate()
    web_service = next((s for s in blueprint.services if s.name == 'web'), None)
    
    assert web_service is not None
    assert web_service.type == 'web'
    assert web_service.ports == "5000"
    assert web_service.startCommand == "python app.py"
    
    # Check env vars
    assert len(web_service.envVars) == 2
    flask_env = next((e for e in web_service.envVars if e.key == 'FLASK_ENV'), None)
    assert flask_env is not None
    assert flask_env.value == 'development'

    # Check disks (named volume)
    assert len(web_service.disks) == 1
    disk = web_service.disks[0]
    assert disk.name == 'logvolume'
    assert disk.mountPath == '/var/log'


def test_translate_redis_service(simple_app_config: DockerComposeConfig) -> None:
    """Test the translation of the 'redis' service."""
    translator = Translator(simple_app_config)
    blueprint = translator.translate()
    redis_service = next((s for s in blueprint.services if s.name == 'redis'), None)

    assert redis_service is not None
    assert redis_service.type == 'web' # Exposed port makes it a web service
    assert redis_service.ports == "6379"
    assert redis_service.image is not None
    assert redis_service.image.url == 'redis:alpine'
    assert not redis_service.disks


def test_warnings_generation(simple_app_config: DockerComposeConfig) -> None:
    """Test that appropriate warnings are generated."""
    translator = Translator(simple_app_config)
    translator.translate() # Run translation to generate warnings

    warnings = translator.warnings
    assert len(warnings) == 1
    assert "Bind mount '.:/code' was ignored" in warnings[0]
