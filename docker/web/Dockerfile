# Web Frontend Dockerfile
# Multi-stage build for minimal image size

# Build stage
FROM node:20-slim AS build

WORKDIR /app

ENV VITE_KEEP_OWN_DOMAIN=true
# Copy package files and install dependencies
COPY web/package.json web/package-lock.json ./
RUN npm ci

COPY web/ ./

RUN npm run build

# Production stage
FROM node:20-slim AS production

WORKDIR /app

ENV VITE_KEEP_OWN_DOMAIN=true
# Install a lightweight HTTP server
RUN npm install -g serve

# Copy built files from build stage
COPY --from=build /app/dist /app/dist

# Expose port for the application
EXPOSE 3000

# Set environment variables
ENV NODE_ENV=production

# Start the server
CMD ["serve", "-s", "dist", "-l", "3000"]