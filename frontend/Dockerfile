# Multi-stage build: build with Node, serve with nginx

# 1) Builder image (install deps and build static assets)
FROM node:18-alpine AS builder

# set working directory
WORKDIR /app

# During the build stage we need devDependencies (tsc, vite) available
# so we do not set NODE_ENV=production here which would skip devDependencies.

# copy package manifests first to leverage Docker cache
COPY package*.json ./

# install dependencies (npm ci will be used if lockfile present)
RUN if [ -f package-lock.json ]; then npm ci --silent; else npm install --silent; fi

# copy source
COPY . .

# build static assets
RUN npm run build


# 2) Production image (nginx serves built assets)
FROM nginx:stable-alpine

# expose port 8080 (non-privileged, safe for OpenShift/OKD arbitrary UID)
EXPOSE 8080

# copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# copy a custom nginx config that listens on 8080 (non-privileged port)
COPY default.conf /etc/nginx/conf.d/default.conf

# Ensure runtime directories are writable by an arbitrary UID (OpenShift/OKD)
# OpenShift runs containers with a random non-root UID. Create the
# nginx runtime/cache directories at build time and make them world-writable
# so the container process can create temp files there.
RUN mkdir -p /var/cache/nginx/client_temp \
 && mkdir -p /var/run \
 && mkdir -p /var/log/nginx \
 && chmod -R 0777 /var/cache/nginx /var/run /var/log/nginx /usr/share/nginx/html

# recommended: disable nginx default logs to reduce image noise
# (optional) set a lightweight healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
	CMD ["/bin/sh", "-c", "wget -qO- --spider http://localhost:8080/ || exit 1"]

# default command
CMD ["nginx", "-g", "daemon off;"]
