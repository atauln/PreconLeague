# Multi-stage Dockerfile for Vite + React + TypeScript frontend
# Build stage
FROM node:25-alpine AS build
WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH

# Allow passing Vite env vars at build time. Use build-args to set these.
ARG VITE_USE_LOCAL
ARG VITE_API_URL
# Ensure the env vars are available to the build step (Vite reads import.meta.env at build time)
ENV VITE_USE_LOCAL=$VITE_USE_LOCAL
ENV VITE_API_URL=$VITE_API_URL

# Install dependencies (use package-lock or yarn.lock if present)
COPY package.json package-lock.json* yarn.lock* ./
RUN if [ -f package-lock.json ]; then npm ci --prefer-offline; else npm install; fi

# Copy source and build
COPY . .
RUN npm run build

# Production stage: Use the unprivileged alpine image
# This image runs as a non-root user and listens on port 8080 by default
FROM nginxinc/nginx-unprivileged:alpine3.22-perl

# Switch to root temporarily to remove default files (if necessary)
USER root
RUN rm -rf /usr/share/nginx/html/*
# Switch back to the non-root user provided by the image
USER nginx

# Copy built app from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# EXPOSE 8080 (Standard for unprivileged Nginx)
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
