# compose-to-render

Intelligently convert `docker-compose.yml` to production-ready `render.yaml` Blueprints for Render.

## Problem & Solution

Docker Compose is great for local development, but Render requires `render.yaml` for Infrastructure as Code. Manually syncing these files is tedious and error-prone. `compose-to-render` bridges this gap by automatically generating best-practice `render.yaml` files from your `docker-compose.yml`.

## Quick Start

### Installation
```bash
pip install compose-to-render
```

### Usage
```bash
compose-to-render --input docker-compose.yml --output render.yaml
```

## Features

- Intelligent service type detection (Web vs. Private Services)
- Named volume to Render Disk conversion
- Environment variable and `env_file` mapping
- Warnings for unsupported docker-compose keys

## Limitations

Handles 80% of common use cases with opinionated choices. Review generated `render.yaml` for complex configurations.

## License

MIT License
