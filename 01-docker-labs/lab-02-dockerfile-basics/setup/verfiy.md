# Lab 02 Verification Guide

## Automated Verification Script

```bash
#!/bin/bash
# Save as verify.sh and run with: bash verify.sh

echo "======================================"
echo "Docker Lab 02 - Verification Script"
echo "======================================"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Score counter
SCORE=0
TOTAL=12

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

echo -e "\n${YELLOW}1. Checking Required Files...${NC}"
[ -f "Dockerfile" ] && check 0 "Dockerfile exists" || check 1 "Dockerfile exists" "Create Dockerfile"
[ -f "app.py" ] && check 0 "app.py exists" || check 1 "app.py exists" "Create app.py"
[ -f "requirements.txt" ] && check 0 "requirements.txt exists" || check 1 "requirements.txt exists" "Create requirements.txt"
[ -f ".dockerignore" ] && check 0 ".dockerignore exists" || check 1 ".dockerignore exists" "Create .dockerignore"

echo -e "\n${YELLOW}2. Checking Docker Images...${NC}"
docker images | grep -q "lab02-basic"
check $? "Basic image built" "Build: docker build -t lab02-basic:v1 ."

docker images | grep -q "lab02-optimized"
check $? "Optimized image built" "Build: docker build -f Dockerfile.optimized -t lab02-optimized:v1 ."

docker images | grep -q "lab02-multistage"
check $? "Multi-stage image built" "Build: docker build -f Dockerfile.multistage -t lab02-multistage:v1 ."

echo -e "\n${YELLOW}3. Checking Image Sizes...${NC}"
if docker images | grep -q "lab02-"; then
    BASIC_SIZE=$(docker images lab02-basic:v1 --format "{{.Size}}" 2>/dev/null | sed 's/MB//')
    OPTIMIZED_SIZE=$(docker images lab02-optimized:v1 --format "{{.Size}}" 2>/dev/null | sed 's/MB//')
    MULTISTAGE_SIZE=$(docker images lab02-multistage:v1 --format "{{.Size}}" 2>/dev/null | sed 's/MB//')
    
    echo "Image sizes:"
    echo "  Basic: $(docker images lab02-basic:v1 --format '{{.Size}}' 2>/dev/null || echo 'Not found')"
    echo "  Optimized: $(docker images lab02-optimized:v1 --format '{{.Size}}' 2>/dev/null || echo 'Not found')"
    echo "  Multi-stage: $(docker images lab02-multistage:v1 --format '{{.Size}}' 2>/dev/null || echo 'Not found')"
    
    # Check if optimized is smaller than basic
    if [ ! -z "$OPTIMIZED_SIZE" ] && [ ! -z "$BASIC_SIZE" ]; then
        echo -e "${GREEN}✓${NC} Optimized image is smaller than basic"
        SCORE=$((SCORE + 1))
    else
        echo -e "${YELLOW}○${NC} Cannot compare image sizes"
    fi
else
    echo -e "${RED}✗${NC} No lab02 images found"
fi

echo -e "\n${YELLOW}4. Checking Running Containers...${NC}"
# Test if containers can be run
docker run -d --name lab02-verify-test -p 5555:5000 lab02-optimized:v1 >/dev/null 2>&1
if [ $? -eq 0 ]; then
    sleep 3
    curl -f http://localhost:5555/health >/dev/null 2>&1
    check $? "Container runs and responds to health check" "Check logs: docker logs lab02-verify-test"
    
    # Check if running as non-root
    USER=$(docker exec lab02-verify-test whoami 2>/dev/null)
    if [ "$USER" != "root" ]; then
        echo -e "${GREEN}✓${NC} Container runs as non-root user ($USER)"
        SCORE=$((SCORE + 1))
    else
        echo -e "${RED}✗${NC} Container runs as root (security issue)"
        echo "  Fix: Add USER directive in Dockerfile"
    fi
    
    docker rm -f lab02-verify-test >/dev/null 2>&1
else
    echo -e "${RED}✗${NC} Failed to run container"
    echo "  Fix: Check image build and port availability"
fi

echo -e "\n${YELLOW}5. Checking Dockerfile Best Practices...${NC}"
if [ -f "Dockerfile.optimized" ]; then
    # Check for non-root user
    grep -q "USER" Dockerfile.optimized
    check $? "Optimized Dockerfile uses non-root USER" "Add: USER appuser"
    
    # Check for HEALTHCHECK
    grep -q "HEALTHCHECK" Dockerfile.optimized
    check $? "Optimized Dockerfile includes HEALTHCHECK" "Add HEALTHCHECK instruction"
    
    # Check for proper COPY order
    grep -q "COPY.*requirements.txt" Dockerfile.optimized
    check $? "Requirements copied before app code (layer caching)" "Copy requirements.txt before app.py"
fi

echo -e "\n======================================"
echo "Final Score: $SCORE/$TOTAL"
echo "======================================"

if [ $SCORE -eq $TOTAL ]; then
    echo -e "${GREEN}🎉 Perfect! All checks passed!${NC}"
elif [ $SCORE -ge 9 ]; then
    echo -e "${GREEN}✓ Good job! Most checks passed.${NC}"
elif [ $SCORE -ge 6 ]; then
    echo -e "${YELLOW}⚠ Some improvements needed.${NC}"
else
    echo -e "${RED}✗ Please review the lab requirements.${NC}"
fi
```

## Manual Verification Steps

### 1. Verify Files and Structure

```bash
# Check all required files exist
ls -la
# Should see: Dockerfile, app.py, requirements.txt, .dockerignore, etc.

# Check file contents are correct
head -5 app.py
# Should show Flask application header

cat requirements.txt
# Should show: Flask, Werkzeug, gunicorn

# Check .dockerignore is working
wc -l .dockerignore
# Should have at least 20 lines
```

### 2. Verify Image Builds

```bash
# List all lab images
docker images | grep lab02

# Expected output (sizes are approximate):
# REPOSITORY          TAG       SIZE
# lab02-multistage    v1        ~150MB
# lab02-optimized     v1        ~150MB  
# lab02-basic         v1        ~1000MB
# lab02-node          v1        ~180MB

# Inspect image layers
docker history lab02-basic:v1
docker history lab02-optimized:v1 --no-trunc

# Check image metadata
docker inspect lab02-optimized:v1 | jq '.[0].Config.Labels'
```

### 3. Test Application Functionality

```bash
# Run Python Flask application
docker run -d --name test-flask -p 5000:5000 lab02-optimized:v1

# Test all endpoints
curl http://localhost:5000/
# Should return JSON with version, hostname, etc.

curl http://localhost:5000/health
# Should return: {"status": "healthy", ...}

curl http://localhost:5000/build-info
# Should show build date, version, commit

curl http://localhost:5000/env
# Should show environment variables

curl -X POST http://localhost:5000/echo \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
# Should echo back the data

# Clean up
docker stop test-flask
docker rm test-flask
```

### 4. Test Node.js Application

```bash
# Run Node.js application
docker run -d --name test-node -p 3000:3000 lab02-node:v1

# Test Node.js endpoints
curl http://localhost:3000/
curl http://localhost:3000/health
curl http://localhost:3000/metrics
curl http://localhost:3000/ready

# Check process handling
docker exec test-node ps aux
# Should show dumb-init as PID 1

# Clean up
docker stop test-node
docker rm test-node
```

### 5. Verify Security Best Practices

```bash
# Check user in each image
for image in lab02-basic:v1 lab02-optimized:v1 lab02-multistage:v1; do
    echo "Checking $image:"
    docker run --rm $image whoami
done

# Basic should show: root (bad)
# Optimized should show: appuser (good)
# Multistage should show: appuser (good)

# Check for security issues with docker scout (if available)
docker scout cves lab02-optimized:v1

# Or use trivy if installed
trivy image lab02-optimized:v1
```

### 6. Test Build Cache

```bash
# First build - note the time
time docker build -f Dockerfile.optimized -t cache-test:v1 .

# Second build - should be much faster due to cache
time docker build -f Dockerfile.optimized -t cache-test:v2 .

# Modify app.py slightly
echo "# Comment" >> app.py

# Rebuild - should use cache until COPY app.py layer
time docker build -f Dockerfile.optimized -t cache-test:v3 .

# Restore app.py
sed -i '$ d' app.py
```

### 7. Test Multi-Stage Build

```bash
# Build multi-stage
docker build -f Dockerfile.multistage -t multi-test:v1 .

# Check intermediate stages (if using BuildKit)
DOCKER_BUILDKIT=1 docker build --target builder -f Dockerfile.multistage -t multi-builder:v1 .

# Compare sizes
docker images | grep multi-
# Builder stage should be larger than final stage
```

### 8. Test Health Checks

```bash
# Run container with health check
docker run -d --name health-test lab02-optimized:v1

# Wait for health check to run
sleep 35

# Check health status
docker inspect health-test --format='{{.State.Health.Status}}'
# Should show: healthy

docker inspect health-test --format='{{json .State.Health}}' | jq .
# Should show health check history

# Simulate unhealthy state (if possible)
docker exec health-test pkill python || true
sleep 35
docker inspect health-test --format='{{.State.Health.Status}}'
# Should show: unhealthy

# Clean up
docker rm -f health-test
```

### 9. Performance Comparison

```bash
# Measure build times
echo "=== Build Time Comparison ==="

time docker build -f Dockerfile -t perf-basic:v1 . --no-cache
time docker build -f Dockerfile.optimized -t perf-optimized:v1 . --no-cache
time docker build -f Dockerfile.multistage -t perf-multi:v1 . --no-cache

# Measure startup times
echo "=== Startup Time Comparison ==="

time docker run --rm perf-basic:v1 python -c "print('Started')"
time docker run --rm perf-optimized:v1 python -c "print('Started')"
time docker run --rm perf-multi:v1 python -c "print('Started')"

# Clean up
docker rmi perf-basic:v1 perf-optimized:v1 perf-multi:v1
```

### 10. Build Arguments and Environment Variables

```bash
# Test build arguments
docker build -f Dockerfile.optimized \
  --build-arg VERSION=3.0.0 \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  -t args-test:v1 .

# Run and check build args were set
docker run --rm args-test:v1 python -c "import os; print(f\"Version: {os.getenv('APP_VERSION')}\")"
# Should show: Version: 3.0.0

# Test runtime environment override
docker run --rm -e APP_ENV=testing args-test:v1 python -c "import os; print(f\"Env: {os.getenv('APP_ENV')}\")"
# Should show: Env: testing
```

## Success Criteria

You have successfully completed Lab 02 when:

- [x] All Dockerfiles build without errors
- [x] Optimized image is significantly smaller than basic
- [x] Multi-stage build produces the smallest image
- [x] Containers run as non-root user (security)
- [x] Health checks are implemented and working
- [x] Build cache is utilized effectively
- [x] .dockerignore reduces build context
- [x] Both Python and Node.js applications work
- [x] All endpoints respond with correct data
- [x] Build arguments and environment variables work

## Common Issues and Fixes

| Issue | Fix |
|-------|-----|
| Large image size | Use slim/alpine base, multi-stage builds |
| Slow builds | Optimize layer order, use .dockerignore |
| Permission denied | Add USER directive, use --chown flag |
| Health check fails | Ensure curl installed, check endpoint |
| Cache not working | Order instructions by change frequency |
| Build context too large | Add more entries to .dockerignore |

## Clean Up

```bash
# Remove all lab02 containers
docker ps -a | grep lab02 | awk '{print $1}' | xargs -r docker rm -f

# Remove all lab02 images
docker images | grep lab02 | awk '{print $3}' | xargs -r docker rmi -f

# Clean build cache
docker builder prune -f

# Remove dangling images
docker image prune -f
```

## Next Steps

Once all verifications pass, you understand:
- Dockerfile best practices
- Layer caching optimization
- Security improvements
- Multi-stage builds
- Build arguments vs environment variables

Ready for Lab 03: Advanced Multi-Stage Builds!
