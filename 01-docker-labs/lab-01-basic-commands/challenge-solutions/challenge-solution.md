# Lab 01 - Solution Commands

## Exercise 1: Image Management

### Search for official Python images
```bash
docker search python --limit 5
docker search python --filter is-official=true
```

### Pull Python 3.11-slim image
```bash
docker pull python:3.11-slim
```

### List all images on your system
```bash
docker images
# Or with formatting
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

### Remove an unused image
```bash
# Remove specific image
docker rmi python:3.11-slim

# Remove all unused images
docker image prune -f
```

## Exercise 2: Container Lifecycle

### Run an nginx container in detached mode
```bash
docker run -d --name my-nginx -p 8080:80 nginx:alpine
```

### Stop the container
```bash
docker stop my-nginx
```

### Restart the container
```bash
docker restart my-nginx
# Or stop then start
docker stop my-nginx
docker start my-nginx
```

### View container logs
```bash
docker logs my-nginx
docker logs -f my-nginx  # Follow logs
docker logs --tail 10 my-nginx  # Last 10 lines
```

### Remove the container
```bash
docker rm -f my-nginx
# Or stop first then remove
docker stop my-nginx
docker rm my-nginx
```

## Exercise 3: Data Persistence

### Create a named volume
```bash
docker volume create mydata
```

### Mount volume to a container
```bash
docker run -d \
  --name data-test \
  -v mydata:/data \
  alpine:latest \
  sh -c 'echo "Hello from container" > /data/test.txt && sleep 3600'
```

### Verify data persistence
```bash
# Check data in first container
docker exec data-test cat /data/test.txt

# Remove first container
docker rm -f data-test

# Create new container with same volume
docker run -d \
  --name data-test-2 \
  -v mydata:/data \
  alpine:latest \
  sleep 3600

# Verify data still exists
docker exec data-test-2 cat /data/test.txt
# Should show: "Hello from container"

# Cleanup
docker rm -f data-test-2
docker volume rm mydata
```

## Exercise 4: Container Networking

### Create a custom bridge network
```bash
docker network create myapp-network --driver bridge
```

### Run multiple containers on the network
```bash
# Run web server
docker run -d \
  --name web \
  --network myapp-network \
  -p 8000:80 \
  nginx:alpine

# Run database
docker run -d \
  --name database \
  --network myapp-network \
  -e POSTGRES_PASSWORD=secret \
  postgres:alpine

# Run cache
docker run -d \
  --name cache \
  --network myapp-network \
  redis:alpine
```

### Test connectivity between containers
```bash
# Test web can reach database
docker exec web ping -c 3 database

# Test web can reach cache
docker exec web ping -c 3 cache

# Test DNS resolution
docker exec web nslookup database
docker exec web nslookup cache

# Test actual service connectivity
docker exec web nc -zv database 5432
docker exec web nc -zv cache 6379

# Cleanup
docker rm -f web database cache
docker network rm myapp-network
```

## Exercise 5: Resource Management

### Run container with memory limit (256MB)
```bash
docker run -d \
  --name limited-memory \
  --memory="256m" \
  --memory-swap="256m" \
  nginx:alpine
```

### Run container with CPU limit (0.5 cores)
```bash
docker run -d \
  --name limited-cpu \
  --cpus="0.5" \
  nginx:alpine
```

### Monitor resource usage
```bash
# View current usage
docker stats --no-stream

# Monitor continuously
docker stats limited-memory limited-cpu

# View specific container
docker stats limited-memory --no-stream

# Update limits on running container
docker update --memory="512m" --cpus="1.0" limited-memory

# Verify new limits
docker inspect limited-memory | grep -A 5 "Memory\|Cpu"

# Cleanup
docker rm -f limited-memory limited-cpu
```

## Complete Exercise Solution Script

```bash
#!/bin/bash
# Complete solution script for all exercises

echo "Starting Lab 01 Exercise Solutions..."

# Exercise 1: Image Management
echo -e "\n=== Exercise 1: Image Management ==="
docker search python --limit 5
docker pull python:3.11-slim
docker images
docker rmi python:3.11-slim

# Exercise 2: Container Lifecycle
echo -e "\n=== Exercise 2: Container Lifecycle ==="
docker run -d --name my-nginx -p 8080:80 nginx:alpine
sleep 2
docker stop my-nginx
docker start my-nginx
docker logs --tail 5 my-nginx
docker rm -f my-nginx

# Exercise 3: Data Persistence
echo -e "\n=== Exercise 3: Data Persistence ==="
docker volume create mydata
docker run -d --name data-test -v mydata:/data alpine:latest \
  sh -c 'echo "Persistent data" > /data/test.txt && sleep 10'
sleep 2
docker exec data-test cat /data/test.txt
docker rm -f data-test
docker run --rm -v mydata:/data alpine:latest cat /data/test.txt
docker volume rm mydata

# Exercise 4: Container Networking
echo -e "\n=== Exercise 4: Container Networking ==="
docker network create myapp-network
docker run -d --name web --network myapp-network nginx:alpine
docker run -d --name cache --network myapp-network redis:alpine
sleep 2
docker exec web ping -c 2 cache
docker rm -f web cache
docker network rm myapp-network

# Exercise 5: Resource Management
echo -e "\n=== Exercise 5: Resource Management ==="
docker run -d --name limited --memory="256m" --cpus="0.5" nginx:alpine
docker stats --no-stream limited
docker update --memory="512m" limited
docker rm -f limited

echo -e "\n=== All exercises completed! ==="
```

## Key Learnings

1. **Image Management**
   - Images are templates for containers
   - Use tags for version control
   - Remove unused images to save space

2. **Container Lifecycle**
   - Containers can be started, stopped, restarted
   - Logs persist even after container stops
   - Use `-d` for detached mode

3. **Data Persistence**
   - Volumes persist data beyond container lifecycle
   - Named volumes are easier to manage
   - Bind mounts connect host directories

4. **Container Networking**
   - Custom networks enable container communication
   - Containers can reach each other by name
   - Bridge networks are isolated from host

5. **Resource Management**
   - Limit CPU and memory to prevent resource exhaustion
   - Monitor usage with `docker stats`
   - Update limits on running containers
