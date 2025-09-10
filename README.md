# compose-to-render

Intelligently convert `docker-compose.yml` to production-ready `render.yaml` Blueprints for Render.

## Quick Start

### Installation
```bash
pip install compose-to-render
```

### Usage
```bash
compose-to-render
```
The tool will generate a render.yaml file in the same directory

## Example

This tool converts this:

`docker-compose.yml` (Your Local Dev)
```yml
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - logvolume:/var/log
  redis:
    image: redis:alpine

volumes:
  logvolume:
```

Into this:
`render.yaml` (Production on Render)
```yaml
services:
  - name: web
    type: web
    autoDeploy: true
    dockerfilePath: Dockerfile
    disks:
      - name: logvolume
        mountPath: /var/log
    buildFilter:
      paths:
        - ./**
    ports: '5000'
  - name: redis
    type: pserv
    autoDeploy: true
    image:
      url: redis:alpine
      owner: docker
```

## Features

- Intelligent service type detection (Web vs. Private Services)
- Named volume to Render Disk conversion
- Environment variable and `env_file` mapping
- Warnings for unsupported docker-compose keys

## License

**MIT License**
