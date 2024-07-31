# devops-qr-code

This is the sample application for the DevOps Capstone Project.
It generates QR Codes for the provided URL, the front-end is in NextJS and the API is written in Python using FastAPI.

## Application

**Front-End** - A web application where users can submit URLs.

**API**: API that receives URLs and generates QR codes. The API stores the QR codes in cloud storage(AWS S3 Bucket).

## Running locally

### API

The API code exists in the `api` directory. You can run the API server locally:

- Clone this repo
- Make sure you are in the `api` directory
- Create a virtualenv by typing in the following command: `python -m venv .venv`
- Install the required packages: `pip install -r requirements.txt`
- Create a `.env` file, and add you AWS Access and Secret key, check  `.env.example`
- Also, change the BUCKET_NAME to your S3 bucket name in `main.py`
- Run the API server: `uvicorn main:app --reload`
- Your API Server should be running on port `http://localhost:8000`

### Front-end

The front-end code exits in the `front-end-nextjs` directory. You can run the front-end server locally:

- Clone this repo
- Make sure you are in the `front-end-nextjs` directory
- Install the dependencies: `npm install`
- Run the NextJS Server: `npm run dev`
- Your Front-end Server should be running on `http://localhost:3000`


## Dockerize the Project

I have created multi-stage Dockerfiles to reduce the image size and have implemented all best practices for creating Dockerfiles.

1. First cd into project directory and then the `api` folder:

```
cd devops-qr-code

# Create Dockerfile for api
cd api

touch Dockerfile
```

- Dockerfile (API):

```
# Build Stage

FROM python:3.9 as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

# RUN Stage

FROM python:3.9-slim

WORKDIR /app

ARG UID=10001
RUN adduser \
	--disabled-password \
	--home "/nonexistent" \
	--shell "/sbin/nologin" \
	--no-create-home \
	--uid "${UID}" \
	apiuser

COPY --from=base /app ./

COPY --from=base /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

USER apiuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

```

- Create `.dockerignore`

```
# Include any files or directories that you don't want to be copied to your
# container here (e.g., local build artifacts, temporary files, etc.).
#
# For more help, visit the .dockerignore file reference guide at
# https://docs.docker.com/go/build-context-dockerignore/

**/.DS_Store
**/__pycache__
**/.venv
**/.classpath
**/.dockerignore
**/.git
**/.gitignore
**/.project
**/.settings
**/.toolstarget
**/.vs
**/.vscode
**/*.*proj.user
**/*.dbmdl
**/*.jfm
**/bin
**/charts
**/docker-compose*
**/compose.y*ml
**/Dockerfile*
**/node_modules
**/npm-debug.log
**/obj
**/secrets.dev.yaml
**/values.dev.yaml
LICENSE
README.md

```

- Build the image and start the api server:

```
docker build -t <Dockerhub Username>/qr-qpi:v1 .

docker run -p 8000:8000 <Dockerhub Username>/qr-qpi:v1
```

The  FastApi will start running in the port `8000` of your machine.

2. Now cd into the `front-end-nextjs` folder

```
cd ..

cd front-end-nextjs

touch Dockerfile
```

- Dockerfile (frontend):

```
# Build stage
FROM node:18-alpine as base

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN mkdir .next

# Run Stage
FROM node:18-alpine

WORKDIR /app

# Define a custom UID
ARG UID=10001

# Create a non-root user with the specified UID
RUN adduser \
    --disabled-password \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    nextjs-user

# Create the /app directory and set ownership
#RUN mkdir -p /app && chown nextjs-user:nextjs-user /app

# Copy built application from the build stage
COPY --from=base --chown=nextjs-user:nextjs-user /app /app
# Switch to the non-root user
USER nextjs-user

EXPOSE 3000

# Start the application
CMD ["npm", "run", "dev"]

```

- Create `.dockerignore`

```
# Node modules (they will be installed fresh in the container)
node_modules

# Next.js build output
.next

# Environment files
.env*

# Version control
.git
.gitignore

# Log files
*.log

# OS generated files
.DS_Store
Thumbs.db

# Editor directories and files
.idea
*.swp
*.swo
.vscode

```

- Build the image and run the application:

```
docker build -t <Dockerhub Username>/qr-frontend:v1 .

docker run -p 3000:3000 <Dockerhub Username>/qr-frontend:v1
```

The  nextjs server will start running in the port `3000` of your machine.

Your Front-end Server should be running on `http://localhost:3000`

Test the application by trying to generate `qr code` from any website `url`.

### S3 configurations:

1. Make sure to set [AmazonS3FullAccess](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonS3FullAccess.html) for your IAM user in the AWS console.
2. In the Permissions of your S3 bucket:
   - Set the *Block _all_ public access* to `off`.
   - Change the *Object Ownership* to `Bucket owner preferred`.
   - Add the following bucket policy to grant public to `qr_codes`within the S3 bucket:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadForQRCodes",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::<your-bucket-name>/qr_codes/*"
        }
    ]
}
```

## Creating CICD pipeline

 Inside the repo create `.github/workflows` folder:

```
mkdir .github

cd .github

mkdir workflows
```

1. Create a file called `cicd.yaml` inside the `workflows` and add the following code:

```
name: CICD for API and Frontend

on:
  push:
    branches:
      - main
    paths-ignore:
      - 'README.md'
      - 'LICENSE'

jobs:

  build-and-test-fastapi:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./api

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      #- name: Run Test
       # run: pytest

      #- name: Run Linter
       # run: flake8 .

  build-and-test-front-end-nextjs:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./front-end-nextjs

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Dependencies
        run: npm ci

     # - name: Run Tests
      #  run: npm test

      - name: Run Linter
        run: npm run lint

  build-and-push-images:
    needs: [build-and-test-fastapi, build-and-test-front-end-nextjs]
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and Push FastAPI image
        uses: docker/build-push-action@v5
        with:
          context: ./api
          file: ./api/Dockerfile
          push: true
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/qr-api:${{ github.sha }}

      - name: Build and Push Next.js image
        uses: docker/build-push-action@v5
        with:
          context: ./front-end-nextjs
          file: ./front-end-nextjs/Dockerfile
          push: true
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/qr-frontend:${{ github.sha }}

```

### CI/CD Pipeline for API and Frontend

This YAML file defines a GitHub Actions workflow that implements a Continuous Integration and Continuous Deployment (CI/CD) pipeline for a project consisting of a FastAPI backend and a Next.js frontend.

### Workflow Overview

- **Name**: CICD for API and Frontend
- **Trigger**: Pushes to the `main` branch, excluding changes to README.md and LICENSE files
- **Structure**: Three main jobs that run in sequence

### Job 1: Build and Test FastAPI Backend

- **Environment**: Ubuntu latest
- **Working Directory**: ./api
- **Steps**:
  1. Checkout the repository
  2. Set up Python 3.11
  3. Install Python dependencies from requirements.txt
### Job 2: Build and Test Next.js Frontend

- **Environment**: Ubuntu latest
- **Working Directory**: ./front-end-nextjs
- **Steps**:
  1. Checkout the repository
  2. Set up Node.js 20
  3. Install Node.js dependencies with `npm ci`
### Job 3: Build and Push Docker Images

- **Dependencies**: Requires successful completion of the FastAPI and Next.js jobs
- **Environment**: Ubuntu latest
- **Steps**:
  1. Checkout the repository
  2. Set up Docker Buildx for multi-platform builds
  3. Log in to DockerHub using secrets
  4. Build and push FastAPI Docker image
     - Context: ./api
     - Dockerfile: ./api/Dockerfile
     - Tag: qr-api:${github.sha}
  5. Build and push Next.js Docker image
     - Context: ./front-end-nextjs
     - Dockerfile: ./front-end-nextjs/Dockerfile
     - Tag: qr-frontend:${github.sha}


This CI/CD pipeline ensures that code changes are automatically built, and packaged into Docker images, ready for deployment.

### Environment configurations:

- Navigate to the settings of your `devops-qr-code` repo.
-  Click on `Secrets and variables` and select `Actions`
-  Create three `New Repository Secret`and the following secrets:

```
# Your Dockerhub Username
DOCKERHUB_USERNAME

# Your Dockerhub Personal Access Token which you can generate in your Dockerhub account
DOCKERHUB_TOKEN

# Your Github Personal Aceess Token which you can generate in your Github account
TOKEN
```

We create these three secrets so that we don't leak our passwords in the CICD manifest.

- Push these changes in your repo and you have automated your project.
- Now a new docker image with `github.run_id` will be pushed into your Dockerhub account when it passes all the stages in Github actions.
