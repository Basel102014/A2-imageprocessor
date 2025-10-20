# Assignment 2 - Cloud Services Exercises - Response to Criteria

## Instructions

- Keep this file named A2_response_to_criteria.md, do not change the name
- Upload this file along with your code in the root directory of your project
- Upload this file in the current Markdown format (.md extension)
- Do not delete or rearrange sections.  If you did not attempt a criterion, leave it blank
- Text inside [ ] like [eg. S3 ] are examples and should be removed

## Overview

- **Name:** Bailey
- **Student number:** n11326158
- **Partner name (if applicable):** N/A
- **Application name:** Image Processor
- **Two line description:** A Flask-based web application that allows authenticated users to upload images, apply processing operations, and view/download results. Uses AWS services for persistence, authentication, and configuration.
- **EC2 instance name or ID:** n11326158-a2-instance

---

### Core - First data persistence service

- **AWS service name:** DynamoDB
- **What data is being stored?:** Metadata for uploaded images and processed results (e.g. filename, status, references to S3).
- **Why is this service suited to this data?:** DynamoDB provides fast, scalable, and serverless storage for structured metadata with low-latency access.
- **Why are the other services used not suitable for this data?:** S3 is better for object storage (large binary files), while Secrets Manager and Parameter Store are for configuration/secrets, not structured app data.
- **Bucket/instance/table name:** n11326158-Uploads, n11326158-Results
- **Video timestamp:**
- **Relevant files:**
  - app/routes/upload.py
  - app/routes/results.py
  - app/services/ddb.py

### Core - Second data persistence service

- **AWS service name:** S3
- **What data is being stored?:** Uploaded images and processed image files.
- **Why is this service suited to this data?:** S3 is highly durable and scalable object storage, ideal for binary data like images.
- **Why are the other services used not suitable for this data?:** DynamoDB is not designed for large binary storage, and other services are focused on config or authentication.
- **Bucket/instance/table name:** n11326158-assessment2
- **Video timestamp:**
- **Relevant files:**
  - app/routes/upload.py
  - app/routes/process.py
  - app/services/s3.py

### Third data service

- **AWS service name:**
- **What data is being stored?:**
- **Why is this service suited to this data?:**
- **Why are the other services used not suitable for this data?:**
- **Bucket/instance/table name:**
- **Video timestamp:**
- **Relevant files:**

### S3 Pre-signed URLs

- **S3 Bucket names:** n11326158-assessment2
- **Video timestamp:**
- **Relevant files:**
  - app/routes/upload.py
  - app/routes/results.py
  - app/services/s3.py

### In-memory cache

- **ElastiCache instance name:**
- **What data is being cached?:**
- **Why is this data likely to be accessed frequently?:**
- **Video timestamp:**
- **Relevant files:**

### Core - Statelessness

- **What data is stored within your application that is not stored in cloud data services?:** Temporary in-memory variables during request handling.
- **Why is this data not considered persistent state?:** These values only exist during a single request lifecycle and can be regenerated from persistent storage.
- **How does your application ensure data consistency if the app suddenly stops?:** All persistent state is in DynamoDB or S3. If the app crashes, no permanent data is lost and operations can be retried.
- **Relevant files:**
  - run.py

### Graceful handling of persistent connections

- **Type of persistent connection and use:**
- **Method for handling lost connections:**
- **Relevant files:**

### Core - Authentication with Cognito

- **User pool name**: cab432-userpool-n11326158
- **How are authentication tokens handled by the client?:** Tokens are received from Cognito Hosted UI and stored in the Flask session for validating user actions.
- **Video timestamp:**
- **Relevant files:**
  - app/routes/auth.py
  - app/utils/auth_helper.py
  - run.py

### Cognito multi-factor authentication

- **What factors are used for authentication:** Password and TOTP-based authenticator app code.
- **Video timestamp:**
- **Relevant files:**
  - Cognito configuration

### Cognito federated identities

- **Identity providers used:**
- **Video timestamp:**
- **Relevant files:**

### Cognito groups

- **How are groups used to set permissions?:** Users are assigned to an "admin" group in Cognito. Admins are given elevated permissions within the application
- **Video timestamp:**
- **Relevant files:**
  - app/routes/auth.py

### Core - DNS with Route53

- **Subdomain**: n11326158.cab432.com
- **Video timestamp:**

### Parameter store

- **Parameter names:**
  - /n11326158/cognito/COGNITO_USER_POOL_ID
  - /n11326158/cognito/COGNITO_CLIENT_ID
  - /n11326158/cognito/DOMAIN_URL
  - /n11326158/s3/APP_BUCKET
  - /n11326158/dynamodb/UPLOADS_TABLE
  - /n11326158/dynamodb/RESULTS_TABLE
  - /n11326158/secrets/COGNITO_SECRET_NAME
  - /n11326158/app/REDIRECT_URI_PROD
  - /n11326158/app/POST_LOGOUT_URI_PROD
  - /n11326158/cognito/HOSTED_UI_URL
  - /n11326158/REGION
- **Video timestamp:**
- **Relevant files:**
  - app/services/param_store.py
  - run.py
  - Most of my endpoints

### Secrets manager

- **Secrets names:** n11326158-secret-key (Cognito client secret)
- **Video timestamp:**
- **Relevant files:**
  - app/services/secrets.py
  - run.py

### Infrastructure as code

- **Technology used:**
- **Services deployed:**
- **Video timestamp:**
- **Relevant files:**

### Other (with prior approval only)

- **Description:**
- **Video timestamp:**
- **Relevant files:**

### Other (with prior permission only)

- **Description:**
- **Video timestamp:**
- **Relevant files:**

