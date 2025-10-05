# Multi-stage Dockerfile for React frontend
# Stage 1: Build the React application with Node.js
# Stage 2: Serve the built application with Nginx

# Stage 1: Build stage using Node.js Alpine image
FROM node:20-alpine AS build

# Set working directory for build stage
WORKDIR /app

# Copy package files for dependency installation
# This layer will be cached if package files don't change
COPY frontend/package*.json ./

# Install dependencies
# --frozen-lockfile ensures exact versions from package-lock.json
RUN npm ci --frozen-lockfile

# Copy source code
COPY frontend/ .

# Build the React application for production
# This creates optimized, minified files in the 'dist' directory
RUN npm run build

# Stage 2: Production stage using Nginx Alpine image
FROM nginx:alpine

# Copy custom Nginx configuration
# This replaces the default nginx.conf with our custom routing rules
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Copy built React application from build stage
# The 'dist' directory contains the production build
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80 for HTTP traffic
EXPOSE 80

# Health check to ensure Nginx is serving content
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Start Nginx server
# Nginx runs in foreground mode for Docker
CMD ["nginx", "-g", "daemon off;"]
