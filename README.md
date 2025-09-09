# compose-to-render

Bridge the gap between local development and production. Intelligently convert `docker-compose.yml` to production-ready `render.yaml` Blueprints.

## The Problem

Developers love `docker-compose.yml` for its simplicity in local development. Render uses a powerful `render.yaml` for defining Infrastructure as Code. Manually keeping these two files in sync is tedious, error-prone, and adds friction to the deployment process—the exact opposite of the Render developer experience.

## The Solution

`compose-to-render` is a standalone CLI tool that acts as an intelligent bridge. It parses your `docker-compose.yml` and generates a best-practice `render.yaml`, handling service types, environment variables, persistent disks, and more.

It's designed to be a seamless part of your workflow, saving you time and eliminating configuration drift.

## Quick Start

### Installation
```bash
pip install compose-to-render
```

### Usage
```bash
compose-to-render --input docker-compose.yml --output render.yaml
```

## Features (Planned)

- Intelligent service type detection (Web Service vs. Private Service).
- Conversion of named volumes to Render Disks.
- Mapping of environment variables and `env_file` directives.
- Graceful warnings for unsupported docker-compose keys (e.g., `depends_on`).

## Limitations

This tool is designed to handle the 80% use case. It makes opinionated choices to generate a production-ready blueprint. For complex or edge-case configurations, the generated `render.yaml` should be treated as a starting point and reviewed carefully.

## License

This project is licensed under the MIT License.