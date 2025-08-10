# Lab 01 Verification Guide

## Automated Verification Script

Run these commands to verify your lab completion:

```bash
#!/bin/bash
# Save as verify.sh and run with: bash verify.sh

echo "======================================"
echo "Docker Lab 01 - Verification Script"
echo "======================================"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Score counter
SCORE=0
TOTAL=10

# Function to check and report
check() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
        SCORE=$((SCORE + 1))
    else
        echo -e "${RED}✗${NC} $2"
        echo "  Fix: $3"
    fi
}

echo -e "\n1. Checking Docker Installation..."
docker --version > /dev/null 2>&1
check $? "Docker is installed" "Install Docker: sudo apt-get install docker.io"

echo -e "\n2. Checking Docker Service..."
docker ps > /dev/null 2>&1
check $? "Docker daemon is running" "Start Docker: sudo systemctl start docker"

echo -e "\n3. Checking Lab Image..."
docker images | grep -q "lab01-app"
check $? "Lab image (lab01-app) exists" "Build image: docker build -t lab01-app:v1 ."

echo -e "\n4. Checking Network..."
docker network ls | grep -q "lab01-network"
check $? "Custom network (lab01-network) exists" "Create network: docker network create lab01-network"

echo -e "\n5. Checking Volume..."
docker volume ls | grep -q "lab01-data"
check $? "Data volume (lab01-data) exists" "Create volume: docker volume create lab01-data"

echo -e "\n6. Checking Running Containers..."
docker ps | grep -q "lab01-test"
check $? "Application container is running" "Start container: docker run -d --name lab01-test -p 5000:5000 lab01-app:v1"

echo -e "\n7. Checking Application Health..."
curl -f http://localhost:5000/health > /dev/null 2>&1
check $? "Application responds to health check" "Check logs: docker logs lab01-test"

echo -e "\n8. Checking Volume Persistence..."
# Test counter endpoint twice
COUNTER1=$(curl -s http://localhost:5000/counter | grep -o '"count":[0-9]*' | grep -o '[0-9]*')
sleep 1
COUNTER2=$(curl -s http://localhost:5000/counter | grep -o '"count":[0-9]*' | grep -o '[0-9]*')
if [ ! -z "$COUNTER2" ] && [ "$COUNTER2" -gt "$COUNTER1" ]; then
    echo -e "${GREEN}✓${NC} Volume persistence is working"
    SCORE=$((SCORE + 1))
else
    echo -e "${RED}✗${NC} Volume persistence not working"
    echo "  Fix: Check volume mount: -v lab01-data:/app/data"
fi

echo -e "\n9. Checking Container Networking..."
docker exec lab01-test ping -c 1 lab01-redis > /dev/null 2>&1
check $? "Container networking is working" "Check network: docker network inspect lab01-network"

echo -e "\n10. Checking Port Mapping..."
curl -f http://localhost:8080 > /dev/null 2>&1
check $? "Nginx port mapping (8080:80) works" "Check nginx: docker ps | grep nginx"

echo -e "\n======================================"
echo "Final Score: $SCORE/$TOTAL"
echo "======================================"

if [ $SCORE -eq $TOTAL ]; then
    echo -e "${GREEN}🎉 Congratulations! All checks passed!${NC}"
    echo "You have successfully completed Lab 01!"
else
    echo -e "${RED}Some checks failed. Please review and fix the issues above.${NC}"
fi
```

## Manual Verification Steps

### 1. Verify Docker Installation
```bash
docker version
# Should show both Client and Server versions
```

### 2. Verify Images
```bash
docker images

# Expected output should include:
# REPOSITORY      TAG       IMAGE ID       CREATED         SIZE
# lab01-app       v1        xxxxx          x minutes ago   xxx MB
# nginx           alpine    xxxxx          x days ago      xxx MB
# redis           alpine    xxxxx          x days ago      xxx MB
# mysql           8.0       xxxxx          x days ago      xxx MB
```

### 3. Verify Running Containers
```bash
docker ps

# Should show at least:
# - lab01-test (port 5000)
# - lab01-nginx (port 8080)
# - lab01-redis
# - lab01-mysql
```

### 4. Verify Networks
```bash
docker network ls
# Should include: lab01-network

docker network inspect lab01-network
# Should show all containers connected
```

### 5. Verify Volumes
```bash
docker volume ls
# Should include: lab01-data, lab01-mysql-data

docker volume inspect lab01-data
# Should show mount point and usage
```

### 6. Test Application Endpoints
```bash
# Main endpoint
curl http://localhost:5000/
# Should return JSON with hostname, ip_address, etc.

# Health check
curl http://localhost:5000/health
# Should return: {"status": "healthy", ...}

# Counter (test persistence)
curl http://localhost:5000/counter
curl http://localhost:5000/counter
curl http://localhost:5000/counter
# Counter should increment each time

# Environment variables
curl http://localhost:5000/env
# Should show container environment

# Write test
curl -X POST http://localhost:5000/write \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
# Should return success

# Read test
curl http://localhost:5000/read
# Should list files in data directory
```

### 7. Test Container Connectivity
```bash
# Test app can reach Redis
docker exec lab01-test ping -c 3 lab01-redis

# Test app can reach MySQL
docker exec lab01-test ping -c 3 lab01-mysql

# Test DNS resolution
docker exec lab01-test nslookup lab01-redis
```

### 8. Test Resource Limits
```bash
# Check container stats
docker stats --no-stream

# Should show CPU and memory usage for all containers
```

### 9. Test Data Persistence
```bash
# Stop and remove the app container
docker stop lab01-test
docker rm lab01-test

# Recreate with same volume
docker run -d \
  --name lab01-test \
  --network lab01-network \
  -p 5000:5000 \
  -v lab01-data:/app/data \
  lab01-app:v1

# Check counter - should maintain previous value
curl http://localhost:5000/counter
```

### 10. Check Logs
```bash
# Application logs
docker logs lab01-test

# Last 50 lines
docker logs --tail 50 lab01-test

# Follow logs
docker logs -f lab01-test
# Press Ctrl+C to exit
```

## Expected Results

### ✅ All Tests Pass When:

1. **Docker is properly installed and running**
   - `docker version` shows both client and server

2. **All images are present**
   - lab01-app:v1
   - nginx:alpine
   - redis:alpine
   - mysql:8.0

3. **All containers are running**
   - lab01-test (Flask app)
   - lab01-nginx
   - lab01-redis
   - lab01-mysql

4. **Network connectivity works**
   - Containers can ping each other by name
   - DNS resolution works within the network

5. **Volumes persist data**
   - Counter increments persist across container restarts
   - Files written to /app/data are preserved

6. **Port mappings work**
   - http://localhost:5000 → Flask app
   - http://localhost:8080 → Nginx

7. **Application endpoints respond**
   - All API endpoints return valid JSON
   - Health check returns status: healthy

## Troubleshooting Failed Checks

### If Docker not installed:
```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker
```

### If image not built:
```bash
cd ~/docker-labs/lab-01-basic-commands
docker build -t lab01-app:v1 .
```

### If containers not running:
```bash
# Check what's wrong
docker ps -a  # Shows all containers including stopped
docker logs <container-name>  # Check error messages

# Restart containers
docker start lab01-test
docker start lab01-nginx
docker start lab01-redis
docker start lab01-mysql
```

### If network issues:
```bash
# Recreate network
docker network rm lab01-network
docker network create lab01-network

# Reconnect containers
docker network connect lab01-network lab01-test
docker network connect lab01-network lab01-redis
docker network connect lab01-network lab01-mysql
docker network connect lab01-network lab01-nginx
```

### If volume issues:
```bash
# Check volume exists
docker volume ls | grep lab01-data

# Inspect volume
docker volume inspect lab01-data

# Check mount in container
docker exec lab01-test ls -la /app/data/
```

### If port conflicts:
```bash
# Find what's using the port
sudo lsof -i :5000
sudo lsof -i :8080

# Stop conflicting service or use different ports
docker run -p 5001:5000 ...  # Use 5001 instead
```

## Clean Verification

After completing all exercises, run this to ensure everything works from scratch:

```bash
# Stop all lab containers
docker stop lab01-test lab01-nginx lab01-redis lab01-mysql

# Remove all lab containers
docker rm lab01-test lab01-nginx lab01-redis lab01-mysql

# Start everything fresh
docker run -d --name lab01-test --network lab01-network -p 5000:5000 -v lab01-data:/app/data lab01-app:v1
docker run -d --name lab01-redis --network lab01-network redis:alpine
docker run -d --name lab01-mysql --network lab01-network -e MYSQL_ROOT_PASSWORD=secret mysql:8.0
docker run -d --name lab01-nginx --network lab01-network -p 8080:80 nginx:alpine

# Run verification
curl http://localhost:5000/health
curl http://localhost:8080
docker exec lab01-test ping -c 1 lab01-redis
```

## Success Criteria

You have successfully completed Lab 01 when:

- [x] All 10 verification checks pass
- [x] You can explain what each Docker command does
- [x] You understand container lifecycle (create, start, stop, remove)
- [x] You can work with images, containers, networks, and volumes
- [x] You can troubleshoot common Docker issues

## Next Steps

Once verification passes, you're ready for Lab 02: Dockerfile Basics!
