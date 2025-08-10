# Lab 01: Jenkins Basics

## 🎯 Objectives
- Install and configure Jenkins server
- Create Jenkins pipelines (Declarative and Scripted)
- Implement CI/CD for a Python application
- Integrate with Docker and Git
- Set up automated testing and deployment

## ⏱️ Duration: 90 minutes

## 📋 Prerequisites
- Ubuntu EC2 instance (t2.large recommended)
- Docker installed and running
- Git installed
- Port 8080 open in security group

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│            Jenkins Master               │
│  ┌────────────────────────────────┐    │
│  │     Jenkins UI (Port 8080)     │    │
│  └────────────────────────────────┘    │
│  ┌────────────────────────────────┐    │
│  │        Pipeline Engine         │    │
│  └────────────────────────────────┘    │
│  ┌────────────────────────────────┐    │
│  │      Docker-in-Docker          │    │
│  └────────────────────────────────┘    │
└─────────────┬───────────────────────────┘
              │
    ┌─────────▼──────────┐
    │   Git Repository   │
    └────────────────────┘
              │
    ┌─────────▼──────────┐
    │  Docker Registry   │
    └────────────────────┘
              │
    ┌─────────▼──────────┐
    │   Deployment       │
    └────────────────────┘
```

## 📁 Lab Structure
```
lab-01-jenkins-basics/
├── README.md (this file)
├── Dockerfile
├── Jenkinsfile
├── Jenkinsfile.scripted
├── src/
│   ├── app.py
│   ├── requirements.txt
│   └── wsgi.py
├── tests/
│   ├── test_app.py
│   └── requirements-test.txt
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── scripts/
│   ├── docker-build.sh
│   └── deploy.sh
├── setup/
│   ├── setup.md
│   └── verify.md
└── solutions/
    ├── Jenkinsfile.complete
    └── jenkins-config.xml
```

## 🚀 Quick Start

### Step 1: Install Jenkins

```bash
# Create Jenkins directory
mkdir -p ~/jenkins-lab
cd ~/jenkins-lab

# Run Jenkins with Docker (recommended for lab)
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(which docker):/usr/bin/docker \
  --restart unless-stopped \
  jenkins/jenkins:lts

# Get initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Step 2: Configure Jenkins

1. Access Jenkins at `http://<EC2-PUBLIC-IP>:8080`
2. Enter the initial admin password
3. Install suggested plugins
4. Create admin user
5. Configure Jenkins URL

### Step 3: Install Required Plugins

Navigate to **Manage Jenkins** → **Plugin Manager** → **Available**

Install these plugins:
- Docker Pipeline
- Blue Ocean
- Pipeline
- Git
- GitHub Integration
- Credentials Binding
- Workspace Cleanup

### Step 4: Create Your First Pipeline

See exercises below for detailed instructions.

## 📝 Application Code

The lab includes a working Python Flask application with tests.
