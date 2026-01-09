# A2 Image Processor

This project is a containerised image processing service developed as part of a university cloud computing assignment.  
The application was designed to run as a containerised workload deployed to AWS infrastructure using Podman and Amazon ECR.

The original AWS environment was provided through a student account and is no longer accessible, but the source code and container configuration remain as a demonstration of system design, containerisation, and deployment workflows.

---

## Project Overview

The Image Processor is a backend service that processes image inputs inside a containerised environment.  
It was designed to be deployed as part of a cloud-based system and run consistently across local and remote environments using containers.

Key goals of the project included:
- Building a reproducible containerised application
- Pushing and pulling container images via Amazon ECR
- Running services using Podman and Podman Compose
- Demonstrating cloud deployment and infrastructure workflows

---

## Technologies Used

- **Podman** – Container runtime and image management  
- **Podman Compose** – Multi-container orchestration  
- **AWS ECR (Elastic Container Registry)** – Container image hosting  
- **AWS SSO** – Authentication for cloud resources  
- **Linux** – Target deployment environment  

---

## Architecture Summary

- The application is packaged as a container image
- Images were built locally and pushed to Amazon ECR
- The service was deployed and run on an EC2 instance using Podman Compose
- Infrastructure access was handled via AWS SSO (student account)

---

## Current Status

⚠️ **AWS deployment is no longer active**

The AWS account used for this project was a university-provided student environment and has since been decommissioned.  
As a result:
- The original ECR repository is no longer accessible
- Deployment commands referencing AWS credentials are retained for documentation purposes only

The repository is preserved to showcase:
- Containerisation workflow
- Cloud deployment practices
- Infrastructure-as-code style thinking

---

## Local Development Notes

The container build configuration remains intact and can be adapted for:
- Local-only container execution
- Deployment to an alternative container registry
- Migration to Docker or another container runtime

---

## What This Project Demonstrates

- Practical containerisation skills
- Understanding of cloud-native deployment workflows
- Ability to work with managed cloud services
- Experience with Linux-based deployment environments
- Clear separation between application logic and infrastructure

---

## Disclaimer

This project was developed for academic purposes.  
Infrastructure credentials and cloud resources referenced in historical commands are no longer valid.
