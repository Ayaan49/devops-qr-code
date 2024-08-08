# Stage 1: Build the Next.js application
FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./
RUN \
  if [ -f yarn.lock ]; then yarn -frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm i --frozen-lockfile; \
  else echo "Lockfile not found." && exit 1; \
  fi
COPY . .
RUN npm run build

# Stage 2: Create the production image
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next /app/.next
COPY --from=builder /app/package.json /app/package.json
COPY --from=builder /app/node_modules /app/node_modules
ENV BACKEND_URL=$BACKEND_URL
EXPOSE 3000
CMD ["npm", "start"]
