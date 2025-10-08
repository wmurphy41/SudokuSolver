# Multi-stage Dockerfile for React frontend build
# 
# This Dockerfile builds the React application and prepares build artifacts.
# The dist contents will be mounted into a separate Nginx container via docker-compose.
# This separation allows for easier updates and more flexible deployment strategies.

# Stage 1: Build the React application with Node.js
FROM node:20-alpine AS build

# Set working directory for build stage
WORKDIR /app

# Copy package files for dependency installation
# This layer will be cached if package files don't change
COPY package*.json ./

# Install dependencies with npm ci for reproducible builds
# npm ci is faster and more reliable than npm install for CI/CD
RUN npm ci

# Copy all source code and configuration files
COPY . .

# Build the React application for production
# This creates optimized, minified files in the 'dist' directory
RUN npm run build

# Stage 2: Prepare distribution artifacts
# This stage contains only the built static files
# The dist contents will be volume-mounted into the Nginx container
# via docker-compose, allowing the Nginx container to serve the files
FROM alpine:3.20 AS dist

# Set working directory for distribution files
WORKDIR /dist

# Copy built application from build stage
# These static files will be served by Nginx in the runtime container
COPY --from=build /app/dist ./

# Note: No CMD or ENTRYPOINT needed here
# This image is used only to provide build artifacts to be mounted as a volume
# The actual serving is done by a separate Nginx container defined in docker-compose.yml
