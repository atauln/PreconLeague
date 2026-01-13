FROM node:18-alpine AS builder
WORKDIR /app
ARG VITE_API_URL=""
# Ensure build-time Vite env is available to the bundler so import.meta.env.VITE_API_URL is inlined
ENV VITE_API_URL=$VITE_API_URL
COPY package*.json ./
RUN if [ -f package-lock.json ]; then npm ci --silent; else npm install --silent; fi
COPY . .
RUN npm run build

# Production image: nginx serves built assets
FROM nginx:stable-alpine
EXPOSE 8080

# Copy built artifacts into the container webroot
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy our nginx config which maps /PreconLeague/ to the built files
COPY default.conf /etc/nginx/conf.d/default.conf

# Ensure runtime directories are writable by an arbitrary UID (OpenShift/OKD)
RUN mkdir -p /var/cache/nginx/client_temp \
 && mkdir -p /var/run \
 && mkdir -p /var/log/nginx \
 && chmod -R 0777 /var/cache/nginx /var/run /var/log/nginx /usr/share/nginx/html

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
	CMD ["/bin/sh", "-c", "wget -qO- --spider http://localhost:8080/PreconLeague/ || exit 1"]

CMD ["nginx", "-g", "daemon off;"]