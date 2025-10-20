#!/bin/bash
set -e

PROFILE="CAB432-STUDENT-901444280953"
REGION="ap-southeast-2"
ACCOUNT_ID="901444280953"
REPO="baileyr-11326158"
IMAGE_NAME="image-processor"
TAG="latest"

echo "Checking AWS SSO session..."
if ! aws sts get-caller-identity --profile $PROFILE >/dev/null 2>&1; then
  echo "SSO session expired or missing. Logging in..."
  aws sso login --profile $PROFILE
fi

echo "Updating domain..."
./scripts/route53-update.sh

echo "Logging into ECR..."
aws ecr get-login-password \
  --region $REGION \
  --profile $PROFILE \
| podman login \
  --username AWS \
  --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

echo "Building image..."
podman build -t $IMAGE_NAME:$TAG .

echo "Tagging image for ECR..."
podman tag $IMAGE_NAME:$TAG \
  $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO:$TAG

echo "Pushing to ECR..."
podman push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO:$TAG

echo "Push complete!"
