# Jenkins Lab Setup Instructions

## Prerequisites Check

```bash
# Check system requirements
free -h  # Should have at least 4GB RAM
df -h    # Should have at least 10GB free space

# Check Docker
docker --version
docker ps

# Check Git
git --version

# Check ports
sudo netstat -tlpn | grep -E '8080|50000'
# Should be empty (ports available)
```

## Step 1: Install Jenkins with Docker

### Option A: Docker Compose (Recommended)

```bash
# Create Jenkins directory
mkdir -p ~/jenkins-lab
cd ~/jenkins-lab

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  jenkins:
    image: jenkins/jenkins:lts-jdk11
    container_name: jenkins
    user: root
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
      - /usr/bin/docker:/usr/bin/docker
    environment:
      - JENKINS_OPTS=--prefix=/
    restart: unless-stopped
    networks:
      - jenkins-net

  jenkins-agent:
    image: jenkins/inbound-agent
    container_name: jenkins-agent
    environment:
      - JENKINS_URL=http://jenkins:8080
      - JENKINS_AGENT_NAME=docker-agent
      - JENKINS_AGENT_WORKDIR=/home/jenkins/agent
    networks:
      - jenkins-net
    depends_on:
      - jenkins

volumes:
  jenkins_home:

networks:
  jenkins-net:
    driver: bridge
EOF

# Start Jenkins
docker-compose up -d

# Wait for Jenkins to start
echo "Waiting for Jenkins to start..."
sleep 30
```

### Option B: Docker Run Command

```bash
# Run Jenkins container
docker run -d \
  --name jenkins \
  --user root \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(which docker):/usr/bin/docker \
  --restart unless-stopped \
  jenkins/jenkins:lts-jdk11
```

## Step 2: Initial Jenkins Configuration

```bash
# Get initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# Copy the password and save it
echo "Initial Admin Password: $(docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword)"
```

### Web UI Setup:

1. Open browser: `http://<EC2-PUBLIC-IP>:8080`
2. Enter the initial admin password
3. Click "Install suggested plugins"
4. Wait for plugins to install (5-10 minutes)
5. Create admin user:
   - Username: `admin`
   - Password: `admin123` (change in production!)
   - Full name: `Administrator`
   - Email: `admin@example.com`
6. Configure Jenkins URL: `http://<EC2-PUBLIC-IP>:8080/`
7. Click "Start using Jenkins"

## Step 3: Install Required Plugins

```bash
# Install plugins via CLI (optional)
docker exec jenkins jenkins-cli.sh install-plugin \
  docker-workflow \
  blueocean \
  pipeline-stage-view \
  git \
  github \
  credentials-binding \
  ws-cleanup \
  htmlpublisher \
  junit
  
# Restart Jenkins
docker restart jenkins
```

Or via Web UI:
1. Go to **Manage Jenkins** → **Plugin Manager**
2. Click **Available** tab
3. Search and select:
   - Docker Pipeline
   - Blue Ocean
   - Pipeline: Stage View
   - Git
   - GitHub Integration
   - Credentials Binding
   - Workspace Cleanup
   - HTML Publisher
4. Click "Install without restart"
5. Check "Restart Jenkins when installation is complete"

## Step 4: Configure Docker in Jenkins

```bash
# Fix Docker permissions
docker exec -u root jenkins sh -c '
  apt-get update && \
  apt-get install -y docker.io && \
  usermod -aG docker jenkins
'

# Restart Jenkins
docker restart jenkins
```

## Step 5: Create Credentials

### Docker Hub Credentials:
1. Go to **Manage Jenkins** → **Credentials**
2. Click **System** → **Global credentials**
3. Click **Add Credentials**
4. Select **Username with password**
5. Enter:
   - Username: `your-dockerhub-username`
   - Password: `your-dockerhub-password`
   - ID: `docker-hub-credentials`
   - Description: `Docker Hub Credentials`

### GitHub Credentials:
1. Click **Add Credentials** again
2. Select **Username with password** or **Secret text** (for token)
3. Enter:
   - Username: `your-github-username`
   - Password/Token: `your-github-token`
   - ID: `github-credentials`
   - Description: `GitHub Credentials`

## Step 6: Configure Global Tools

1. Go to **Manage Jenkins** → **Global Tool Configuration**

### Git Configuration:
- Name: `Default`
- Path: `git` (auto-detected)

### Docker Configuration:
- Name: `docker`
- Installation directory: `/usr/bin/docker`

## Step 7: Create Application Repository

```bash
# Create project directory
mkdir -p ~/jenkins-demo-app
cd ~/jenkins-demo-app

# Copy application files from lab
cp -r ~/devops-labs/03-cicd-labs/lab-01-jenkins-basics/* .

# Initialize Git repository
git init
git add .
git commit -m "Initial commit"

# Create GitHub repository (if using GitHub)
# gh repo create jenkins-demo-app --public
# git remote add origin https://github.com/<username>/jenkins-demo-app.git
# git push -u origin main
```

## Step 8: Create First Pipeline Job

### Via Web UI:
1. Click **New Item**
2. Enter name: `demo-pipeline`
3. Select **Pipeline**
4. Click **OK**

### Configure Pipeline:
1. In **General** section:
   - Check **GitHub project**
   - Project url: `https://github.com/<username>/jenkins-demo-app`

2. In **Build Triggers** section:
   - Check **Poll SCM**
   - Schedule: `H/5 * * * *` (every 5 minutes)

3. In **Pipeline** section:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/<username>/jenkins-demo-app.git`
   - Credentials: Select your GitHub credentials
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`

4. Click **Save**

## Step 9: Test the Pipeline

```bash
# Trigger build manually
# Click "Build Now" in Jenkins UI

# Or trigger via CLI
docker exec jenkins jenkins-cli.sh build demo-pipeline

# Check build logs
docker exec jenkins cat /var/jenkins_home/jobs/demo-pipeline/builds/1/log
```

## Step 10: Verify Installation

```bash
# Check Jenkins is running
docker ps | grep jenkins

# Check Jenkins logs
docker logs jenkins --tail 50

# Test Jenkins CLI
docker exec jenkins jenkins-cli.sh version

# Check installed plugins
docker exec jenkins jenkins-cli.sh list-plugins

# Test application endpoints
curl http://localhost:8080/api/json?pretty=true
```

## Common Issues and Solutions

### Issue 1: Cannot connect to Docker daemon
```bash
# Fix Docker socket permissions
docker exec -u root jenkins chmod 666 /var/run/docker.sock
```

### Issue 2: Jenkins is slow
```bash
# Increase memory
docker update jenkins --memory="4g" --memory-swap="4g"
```

### Issue 3: Plugin installation fails
```bash
# Update plugin center
docker exec jenkins jenkins-cli.sh reload-configuration
```

### Issue 4: Cannot access Jenkins UI
```bash
# Check firewall/security group
# Ensure port 8080 is open in AWS Security Group
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 8080 \
  --cidr 0.0.0.0/0
```

## Blue Ocean Setup (Optional)

1. Access Blue Ocean: `http://<EC2-PUBLIC-IP>:8080/blue`
2. Click **Create a new Pipeline**
3. Select **GitHub**
4. Enter access token
5. Select organization and repository
6. Blue Ocean will auto-detect Jenkinsfile

## Monitoring Setup

```bash
# Install monitoring plugin
docker exec jenkins jenkins-cli.sh install-plugin monitoring

# Access monitoring
# http://<EC2-PUBLIC-IP>:8080/monitoring
```

## Backup Jenkins

```bash
# Backup Jenkins home
docker run --rm \
  -v jenkins_home:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/jenkins-backup-$(date +%Y%m%d).tar.gz -C /data .

# Restore from backup
docker run --rm \
  -v jenkins_home:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/jenkins-backup.tar.gz -C /data
```

## Ready to Use!

Your Jenkins server is now ready with:
- ✅ Jenkins LTS installed
- ✅ Docker integration configured
- ✅ Required plugins installed
- ✅ Credentials configured
- ✅ Sample pipeline ready
- ✅ Blue Ocean UI available

Access Jenkins at: `http://<EC2-PUBLIC-IP>:8080`

Proceed to create and run pipelines!
