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

# expose port 80
EXPOSE 80

# copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# recommended: disable nginx default logs to reduce image noise
# (optional) set a lightweight healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD ["/bin/sh", "-c", "wget -qO- --spider http://localhost/ || exit 1"]

# default command
CMD ["nginx", "-g", "daemon off;"]
