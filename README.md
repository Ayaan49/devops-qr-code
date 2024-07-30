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
