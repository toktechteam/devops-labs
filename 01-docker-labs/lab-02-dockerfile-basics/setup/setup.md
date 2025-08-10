# Lab 02 Setup Instructions

## Prerequisites Check

```bash
# 1. Ensure Docker is installed and running
docker --version
docker info

# 2. Check available disk space (need at least 2GB)
df -h /var/lib/docker

# 3. Clean up any previous lab artifacts
docker system prune -f
```

## Lab Setup

### Step 1: Create Lab Directory

```bash
# Create lab directory structure
mkdir -p ~/docker-labs/lab-02-dockerfile-basics/{setup,solutions,config}
cd ~/docker-labs/lab-02-dockerfile-basics

# Verify you're in the correct directory
pwd
# Should show: /home/ubuntu/docker-labs/lab-02-dockerfile-basics
```

### Step 2: Create Application Files

```bash
# Create Python application (copy from artifacts or use these commands)
# The app.py file should be copied from the artifact

# Create requirements.txt
cat > requirements.txt << 'EOF'
Flask==2.3.3
Werkzeug==2.3.7
gunicorn==21.2.0
EOF

# Create Node.js application
# The app.js file should be copied from the artifact

# Create package.json
# The package.json file should be copied from the artifact

# Create .dockerignore
# The .dockerignore file should be copied from the artifact
```

### Step 3: Create Basic Dockerfile

```bash
# Create the basic Dockerfile (with intentional issues)
cat > Dockerfile << 'EOF'
# Basic Dockerfile - Starting point for Lab 02
# This Dockerfile has intentional issues for learning purposes

FROM python:3.11

# Set working directory
WORKDIR /app

# Copy everything (inefficient)
COPY . .

# Install dependencies (not cached properly)
RUN pip install Flask==2.3.3
RUN pip install Werkzeug==2.3.7

# Expose port
EXPOSE 5000

# Run as root (security issue)
CMD ["python", "app.py"]
EOF
```

### Step 4: Test Basic Build

```bash
# Build the basic image
docker build -t lab02-basic:v1 .

# Check build time and size
docker images lab02-basic:v1

# Run container from basic image
docker run -d --name lab02-test-basic -p 5000:5000 lab02-basic:v1

# Test the application
curl http://localhost:5000
curl http://localhost:5000/health
curl http://localhost:5000/build-info

# Check container is running as root (security issue)
docker exec lab02-test-basic whoami
# Output: root (this is bad!)

# Stop and remove test container
docker stop lab02-test-basic
docker rm lab02-test-basic
```

### Step 5: Create Optimized Dockerfile

```bash
# Copy the Dockerfile.optimized from the artifact
# This shows best practices

# Build optimized version
docker build -f Dockerfile.optimized \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --build-arg VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "no-git") \
  --build-arg VERSION=1.0.0 \
  -t lab02-optimized:v1 .

# Compare image sizes
docker images | grep lab02

# Run optimized container
docker run -d --name lab02-test-optimized -p 5001:5000 lab02-optimized:v1

# Test optimized version
curl http://localhost:5001
curl http://localhost:5001/build-info

# Check it's running as non-root (good!)
docker exec lab02-test-optimized whoami
# Output: appuser (this is good!)
```

### Step 6: Create Multi-Stage Build

```bash
# Copy the Dockerfile.multistage from the artifact

# Build multi-stage version
docker build -f Dockerfile.multistage \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --build-arg VERSION=2.0.0 \
  -t lab02-multistage:v1 .

# Compare all image sizes
docker images | grep lab02
echo "Notice the size difference!"

# Run multi-stage container
docker run -d --name lab02-test-multistage -p 5002:5000 lab02-multistage:v1

# Test multi-stage version
curl http://localhost:5002
curl http://localhost:5002/health
```

### Step 7: Node.js Multi-Stage Build

```bash
# Create Node.js Dockerfile
cat > Dockerfile.node << 'EOF'
# Multi-stage build for Node.js
FROM node:18-alpine AS builder

WORKDIR /build

# Copy package files
COPY package*.json ./

# Install all dependencies
RUN npm ci

# Final stage
FROM node:18-alpine

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /build/node_modules ./node_modules

# Copy application
COPY --chown=nodejs:nodejs package*.json ./
COPY --chown=nodejs:nodejs app.js ./

# Use non-root user
USER nodejs

# Environment
ENV NODE_ENV=production \
    PORT=3000

EXPOSE 3000

# Proper signal handling with dumb-init
ENTRYPOINT ["dumb-init", "--"]

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => {r.statusCode === 200 ? process.exit(0) : process.exit(1)})"

CMD ["node", "app.js"]
EOF

# Build Node.js image
docker build -f Dockerfile.node -t lab02-node:v1 .

# Run Node.js container
docker run -d --name lab02-test-node -p 3000:3000 lab02-node:v1

# Test Node.js application
curl http://localhost:3000
curl http://localhost:3000/health
curl http://localhost:3000/metrics
```

### Step 8: Test Build Cache

```bash
# Make a small change to app.py
echo "# Small change" >> app.py

# Rebuild and notice cache usage
docker build -f Dockerfile.optimized -t lab02-cache-test:v1 .
# Notice: uses cache for layers before COPY app.py

# Restore original app.py
sed -i '$ d' app.py

# Change requirements.txt
echo "requests==2.31.0" >> requirements.txt

# Rebuild and notice cache invalidation
docker build -f Dockerfile.optimized -t lab02-cache-test:v2 .
# Notice: cache invalidated from requirements.txt layer onward

# Restore requirements.txt
sed -i '$ d' requirements.txt
```

## Common Issues and Solutions

### Issue 1: Build Context Too Large
```bash
# Check build context size
du -sh .

# Solution: Use .dockerignore
echo "node_modules/" >> .dockerignore
echo "__pycache__/" >> .dockerignore
echo ".git/" >> .dockerignore
```

### Issue 2: Permission Denied in Container
```bash
# Check file ownership
docker exec lab02-test-optimized ls -la /app

# Solution: Use COPY --chown
# COPY --chown=appuser:appuser app.py .
```

### Issue 3: Health Check Failing
```bash
# Debug health check
docker inspect lab02-test-optimized --format='{{json .State.Health}}'

# Check logs
docker logs lab02-test-optimized

# Test health endpoint manually
docker exec lab02-test-optimized curl http://localhost:5000/health
```

### Issue 4: Slow Builds
```bash
# Use build cache effectively
# Order Dockerfile instructions from least to most frequently changing

# Use BuildKit for better performance
DOCKER_BUILDKIT=1 docker build -t test:latest .

# Use multi-stage builds to parallelize
```

## Verification Checklist

- [ ] Basic Dockerfile builds successfully
- [ ] Optimized Dockerfile reduces image size
- [ ] Multi-stage build creates smallest image
- [ ] Containers run as non-root user
- [ ] Health checks pass
- [ ] Build cache works efficiently
- [ ] .dockerignore reduces context size
- [ ] Node.js application works
- [ ] All endpoints respond correctly

## Ready to Continue

Once all setup steps complete successfully:
- Basic image: ~1GB (intentionally large)
- Optimized image: ~150MB
- Multi-stage image: ~150MB
- Node.js image: ~180MB

Proceed to the exercises in the main README.md!
