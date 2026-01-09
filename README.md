# A2 Image Processor (Containerised Image Processing Service)

A containerised image processing service built for a university Cloud Computing assignment.

The original deployment target was AWS (EC2 + Amazon ECR) using **Podman** and **podman-compose**. That student AWS environment is no longer available, but this repository is kept public to showcase:

- containerised service design
- multi-container orchestration
- separation of API and background worker responsibilities
- cloud deployment and infrastructure workflows

> **Note:** Any commands or configuration referencing old AWS accounts or registries are preserved for historical context only and will no longer work.

---

## Project Overview

This project implements a simple backend image-processing system designed to run consistently across local and cloud environments using containers.

The system is split into two main services:

- **API service** – handles incoming requests and job submission
- **Worker service** – performs the image processing tasks asynchronously

This separation mirrors common real-world backend architectures where request handling and heavy processing are decoupled for scalability and reliability.

---

## Repository Structure

At a high level, the repository is organised as follows:

- `api.py` – API service entry point and request handling logic
- `worker.py` – background worker for executing image-processing jobs
- `app/` – application assets and supporting code
- `docker-compose.yml` – multi-container orchestration configuration
- `Dockerfile.api` – container definition for the API service
- `Dockerfile.worker` – container definition for the worker service
- `requirements.txt` – Python dependencies
- `scripts/` – helper scripts for build and deployment tasks
- `A2_response_to_criteria.md` – assignment criteria mapping and justification

---

## Architecture Summary

The application follows a simple cloud-native pattern:

1. The **API container** receives requests (for example, image uploads or job submissions).
2. The **worker container** processes images in the background.
3. Both services are deployed together using Compose tooling to ensure consistent runtime behaviour.

This design allows the system to scale and be deployed across different environments without changing application code.

---

## Running Locally

Although the original AWS environment is no longer available, the project can still be run locally using container tooling.

### Option 1: Docker (recommended)

```bash
docker compose up --build
```

To stop the services:

```bash
docker compose down
```

### Option 2: Podman (closer to original assignment setup)

```bash
podman-compose up --build
```

To stop the services:

```bash
podman-compose down
```

> Depending on your system, Docker may work out-of-the-box while Podman may require minor configuration changes.

---

## Building Images Manually

If you want to build the container images individually:

### Docker

```bash
docker build -f Dockerfile.api -t a2-imageprocessor-api:latest .
docker build -f Dockerfile.worker -t a2-imageprocessor-worker:latest .
```

### Podman

```bash
podman build -f Dockerfile.api -t a2-imageprocessor-api:latest .
podman build -f Dockerfile.worker -t a2-imageprocessor-worker:latest .
```

---

## Deployment Notes (Historical)

This project was originally deployed using:

- Amazon EC2
- Amazon Elastic Container Registry (ECR)
- AWS Single Sign-On (SSO)

These resources were provided through a university-managed student AWS account that has since been decommissioned. The deployment steps are retained for documentation purposes only.

To redeploy this project today, the images could be pushed to an alternative registry (Docker Hub, GHCR, or a personal AWS account) and deployed to any Linux-based virtual machine.

---

## What This Project Demonstrates

- Containerised backend application design
- Multi-container orchestration using Compose tooling
- Separation of concerns between API and worker services
- Practical experience with cloud deployment workflows
- Ability to adapt infrastructure-specific solutions to new environments

---

## Licence

MIT — see `LICENSE` for details.

