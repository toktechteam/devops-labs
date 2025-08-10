# Lab 01 Setup Instructions

## Prerequisites Check

```bash
# 1. Check Ubuntu version (should be 20.04 or 22.04)
lsb_release -a

# 2. Check Docker installation
docker --version

# 3. If Docker not installed, install it:
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker

# 4. Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# 5. Verify Docker works without sudo
docker run hello-world
```

## Lab Setup

### Step 1: Create Lab Directory Structure

```bash
# Create main lab directory
mkdir -p ~/docker-labs/lab-01-basic-commands
cd ~/docker-labs/lab-01-basic-commands

# Create subdirectories
mkdir -p setup solutions config data
```

### Step 2: Create Lab Files

```bash
# Create all required files (copy from artifacts or use these commands)

# 1. Copy app.py from the artifact
# 2. Copy requirements.txt from the artifact
# 3. Copy index.html from the artifact
# 4. Copy Dockerfile from the artifact
```

### Step 3: Build Test Image

```bash
# Build the lab image
docker build -t lab01-app:v1 .

# Verify image was created
docker images | grep lab01-app
```

### Step 4: Create Test Network and Volume

```bash
# Create a custom network for the lab
docker network create lab01-network

# Create a volume for data persistence
docker volume create lab01-data

# Verify creation
docker network ls | grep lab01
docker volume ls | grep lab01
```

### Step 5: Run Initial Test Container

```bash
# Run the application container
docker run -d \
  --name lab01-test \
  --network lab01-network \
  -p 5000:5000 \
  -v lab01-data:/app/data \
  -e APP_ENV=development \
  lab01-app:v1

# Check if container is running
docker ps | grep lab01-test

# Check logs
docker logs lab01-test

# Test the application
curl http://localhost:5000
curl http://localhost:5000/health
```

### Step 6: Setup Additional Test Containers

```bash
# Run Redis for networking tests
docker run -d \
  --name lab01-redis \
  --network lab01-network \
  redis:alpine

# Run MySQL for volume tests
docker run -d \
  --name lab01-mysql \
  --network lab01-network \
  -e MYSQL_ROOT_PASSWORD=secret \
  -e MYSQL_DATABASE=testdb \
  -v lab01-mysql-data:/var/lib/mysql \
  mysql:8.0

# Run Nginx for port mapping tests
docker run -d \
  --name lab01-nginx \
  --network lab01-network \
  -p 8080:80 \
  -v $(pwd)/index.html:/usr/share/nginx/html/index.html:ro \
  nginx:alpine
```

### Step 7: Verify Setup

```bash
# Check all containers are running
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test connectivity between containers
docker exec lab01-test ping -c 2 lab01-redis
docker exec lab01-test ping -c 2 lab01-mysql

# Test web access
curl http://localhost:5000/
curl http://localhost:8080/

# Test volume persistence
curl http://localhost:5000/counter
curl http://localhost:5000/counter
curl http://localhost:5000/counter
# Should see incrementing counter

# Check volume data
docker exec lab01-test ls -la /app/data/
```

## Common Issues and Solutions

### Issue 1: Port Already in Use
```bash
# Find what's using the port
sudo lsof -i :5000

# Kill the process or use different port
docker run -p 5001:5000 ...
```

### Issue 2: Permission Denied
```bash
# Ensure user is in docker group
groups
# If docker not listed:
sudo usermod -aG docker $USER
# Log out and back in, or:
newgrp docker
```

### Issue 3: Cannot Connect to Container
```bash
# Check container is running
docker ps

# Check container logs
docker logs lab01-test

# Check network
docker network inspect lab01-network

# Check firewall (if applicable)
sudo ufw status
```

### Issue 4: Build Fails
```bash
# Check Dockerfile syntax
docker build --no-cache -t lab01-app:v1 .

# Check all files exist
ls -la

# Check file permissions
chmod 644 Dockerfile app.py requirements.txt index.html
```

## Ready to Start!

Once all setup steps complete successfully, you're ready to begin the lab exercises. The setup creates:

- ✅ A working Python Flask application
- ✅ Custom Docker network (lab01-network)
- ✅ Persistent volume (lab01-data)
- ✅ Multiple test containers (app, redis, mysql, nginx)
- ✅ Exposed ports for testing (5000, 8080)

Proceed to the main README.md for lab exercises.
