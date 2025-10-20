### A2-imageprocessor

## Push Image to Amazon ECR (from local machine)

### Login to AWS SSO
```bash
aws sso login --profile CAB432-STUDENT-901444280953
```
Opens browser to authenticate your student account. Must be run once per session.

### Authenticate Podman with ECR
```bash
aws ecr get-login-password --region ap-southeast-2 | sudo podman login --username AWS --password-stdin 901444280953.dkr.ecr.ap-southeast-2.amazonaws.com
```

### Build your image
```bash
podman build -t image-processor:latest .
```

### Tag the image for ECR
```bash
podman tag image-processor:latest \
  901444280953.dkr.ecr.ap-southeast-2.amazonaws.com/baileyr-11326158:latest
```

### Push to ECR
```bash
podman push \
  901444280953.dkr.ecr.ap-southeast-2.amazonaws.com/baileyr-11326158:latest
```

## Pull Image & Run with Podman Compose (on EC2)

### Authenticate Podman with ECR
```bash
aws ecr get-login-password --region ap-southeast-2 | sudo podman login --username AWS --password-stdin 901444280953.dkr.ecr.ap-southeast-2.amazonaws.com
```

### Pull your image
```bash
sudo podman pull 901444280953.dkr.ecr.ap-southeast-2.amazonaws.com/baileyr-11326158:latest
```

### Run with Podman Compose
```bash
sudo podman-compose up -d
```

## Common Commands

```bash
sudo podman ps -a
```
Check all containers (running and stopped)

```bash
sudo podman stop <container_id_or_name>
```
Stops container with id

```bash
sudo podman rm <container_id_or_name>
```
Deletes container with id

```bash
sudo podman rmi -f $(sudo podman images -aq)
```
Deletes all images