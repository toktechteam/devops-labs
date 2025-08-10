# Jenkins Lab Verification Guide

## Verification Checklist

### 1. Jenkins Installation

```bash
# Check Jenkins is running
docker ps | grep jenkins

# Check Jenkins version
docker exec jenkins jenkins --version

# Check Jenkins URL is accessible
curl -I http://localhost:8080

# Check Jenkins logs
docker logs jenkins --tail 50
```

### 2. Plugin Installation

```bash
# List installed plugins
docker exec jenkins jenkins-cli.sh list-plugins | grep -E "docker|pipeline|git"

# Expected plugins:
# - docker-workflow
# - pipeline
# - git
# - github
# - blueocean
```

### 3. Pipeline Configuration

```bash
# Check if pipeline job exists
curl -u admin:admin123 http://localhost:8080/job/demo-pipeline/api/json | jq .

# Trigger a build
curl -X POST -u admin:admin123 http://localhost:8080/job/demo-pipeline/build

# Check build status
curl -u admin:admin123 http://localhost:8080/job/demo-pipeline/lastBuild/api/json | jq .result
```

### 4. Application Testing

```bash
# Check if application is running
docker ps | grep demo-app

# Test application endpoints
curl http://localhost:5000/
curl http://localhost:5000/health
curl http://localhost:5000/metrics

# Check application logs
docker logs $(docker ps -q -f name=demo-app)
```

### 5. Docker Registry

```bash
# Check if image was built
docker images | grep jenkins-demo-app

# Check image tags
docker images jenkins-demo-app --format "table {{.Tag}}\t{{.Size}}\t{{.Created}}"
```

## Success Criteria

- [ ] Jenkins is accessible at http://localhost:8080
- [ ] Admin user can login
- [ ] Required plugins are installed
- [ ] Pipeline job is created
- [ ] Pipeline runs successfully
- [ ] Application is deployed
- [ ] Health checks pass
- [ ] Docker image is built and tagged

## Troubleshooting

### Jenkins won't start
```bash
# Check logs
docker logs jenkins

# Check disk space
df -h

# Restart Jenkins
docker restart jenkins
```

### Pipeline fails
```bash
# Check pipeline syntax
curl -X POST -u admin:admin123 \
  -F "jenkinsfile=<Jenkinsfile" \
  http://localhost:8080/pipeline-model-converter/validate

# Check workspace
docker exec jenkins ls -la /var/jenkins_home/workspace/
```

### Application won't deploy
```bash
# Check Docker daemon
docker exec jenkins docker version

# Check permissions
docker exec jenkins ls -la /var/run/docker.sock
```

## Clean Verification

```bash
# Run complete verification script
cat > verify.sh << 'EOF'
#!/bin/bash
echo "=== Jenkins Lab Verification ==="

# Check Jenkins
if docker ps | grep -q jenkins; then
  echo "✓ Jenkins is running"
else
  echo "✗ Jenkins is not running"
  exit 1
fi

# Check application
if curl -f http://localhost:5000/health 2>/dev/null | grep -q healthy; then
  echo "✓ Application is healthy"
else
  echo "✗ Application health check failed"
fi

# Check images
if docker images | grep -q jenkins-demo-app; then
  echo "✓ Docker image exists"
else
  echo "✗ Docker image not found"
fi

echo "=== Verification Complete ==="
EOF

bash verify.sh
```