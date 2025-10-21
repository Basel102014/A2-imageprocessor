#!/bin/bash
set -e

PROFILE="CAB432-STUDENT-901444280953"
REGION="ap-southeast-2"
ACCOUNT_ID="901444280953"
REPO="baileyr-11326158"
TAG="latest"

build_and_push() {
  local IMAGE_NAME=$1

  echo "Building image: $IMAGE_NAME"
  podman build -t $IMAGE_NAME:$TAG -f Dockerfile.$IMAGE_NAME .

  echo "Tagging image for ECR..."
  podman tag $IMAGE_NAME:$TAG \
    $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO:$IMAGE_NAME-$TAG

  echo "Pushing image to ECR..."
  podman push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO:$IMAGE_NAME-$TAG

  echo "$IMAGE_NAME pushed successfully."
}

echo "Checking AWS SSO session..."
if ! aws sts get-caller-identity --profile $PROFILE >/dev/null 2>&1; then
  echo "SSO session expired or missing. Logging in..."
  aws sso login --profile $PROFILE
fi

echo "Updating Route53 record..."
./scripts/route53-update.sh

echo "Logging into ECR..."
aws ecr get-login-password \
  --region $REGION \
  --profile $PROFILE \
| podman login \
  --username AWS \
  --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build and push both images
build_and_push "api"
build_and_push "worker"

echo "Deployment complete."
