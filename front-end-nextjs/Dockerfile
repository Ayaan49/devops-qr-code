# Build stage
FROM node:18-alpine AS base

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

COPY .env .env

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
