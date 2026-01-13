# Multi-stage Dockerfile for Vite + React + TypeScript frontend
# Build stage
FROM node:18-alpine AS build
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
RUN npm ci --silent --prefer-offline

# Copy source and build
COPY . .
RUN npm run build

# Production stage: nginx to serve the built static files
FROM nginx:1.26-alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy built app from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
