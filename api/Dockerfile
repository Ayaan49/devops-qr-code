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

RUN apt update && apt install -y dnsutils
RUN pip install awscli

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

# Ensure apiuser can read the AWS token file
RUN mkdir -p /var/run/secrets/eks.amazonaws.com/serviceaccount && \
    chown -R apiuser:apiuser /var/run/secrets/eks.amazonaws.com/serviceaccount

# Set the AWS_WEB_IDENTITY_TOKEN_FILE environment variable
ENV AWS_WEB_IDENTITY_TOKEN_FILE=/var/run/secrets/eks.amazonaws.com/serviceaccount/token

USER apiuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
