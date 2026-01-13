docker build -t preconleague-frontend:latest --build-arg VITE_USE_LOCAL=true .
docker run --rm -p 8080:80 --add-host=host.docker.internal:host-gateway preconleague-frontend:latest