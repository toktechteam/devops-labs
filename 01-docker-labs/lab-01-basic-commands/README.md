# Lab 01: Docker Basic Commands

## 🎯 Objectives
- Master essential Docker CLI commands
- Understand container lifecycle
- Work with Docker images and registries
- Manage container resources and volumes

## ⏱️ Duration: 45 minutes

## 📋 Prerequisites
- EC2 Ubuntu instance (t2.medium or larger)
- Docker installed
- Internet connection

## 🏗️ Lab Architecture

```
┌─────────────────────────────────┐
│     Docker Host (EC2 Ubuntu)    │
├─────────────────────────────────┤
│         Docker Engine           │
├─────────────────────────────────┤
│  ┌─────────────────────────┐   │
│  │    nginx:alpine         │   │
│  │    Port: 8080→80       │   │
│  └─────────────────────────┘   │
│  ┌─────────────────────────┐   │
│  │    mysql:8.0           │   │
│  │    Port: 3306          │   │
│  │    Volume: db-data     │   │
│  └─────────────────────────┘   │
│  ┌─────────────────────────┐   │
│  │    redis:alpine        │   │
│  │    Port: 6379          │   │
│  └─────────────────────────┘   │
└─────────────────────────────────┘
```

## 📁 Lab Structure
```
lab-01-basic-commands/
├── README.md (this file)
├── Dockerfile
├── app.py
├── requirements.txt
├── index.html
├── setup/
│   ├── setup.md
│   └── verify.md
├── solutions/
│   ├── solution-commands.md
│   └── challenge-solution.md
└── config/
    └── nginx.conf
```

## 🚀 Quick Start

1. **Clone or create the lab directory:**
```bash
mkdir -p ~/docker-labs/lab-01-basic-commands
cd ~/docker-labs/lab-01-basic-commands
```

2. **Copy all lab files to your directory**

3. **Run the setup:**
```bash
# Follow instructions in setup/setup.md
```

4. **Complete the exercises below**

## 📝 Exercises

### Exercise 1: Image Management
Learn to search, pull, and manage Docker images.

**Tasks:**
1. Search for official Python images
2. Pull Python 3.11-slim image
3. List all images on your system
4. Remove an unused image

**Commands:**
```bash
# Your commands here - see solutions/challenge-solution.md for answers
```

### Exercise 2: Container Lifecycle
Create and manage container lifecycle.

**Tasks:**
1. Run an nginx container in detached mode
2. Stop and restart the container
3. View container logs
4. Remove the container

### Exercise 3: Data Persistence
Work with volumes and bind mounts.

**Tasks:**
1. Create a named volume
2. Mount volume to a container
3. Verify data persistence after container removal

### Exercise 4: Container Networking
Connect containers using Docker networks.

**Tasks:**
1. Create a custom bridge network
2. Run multiple containers on the network
3. Test connectivity between containers

### Exercise 5: Resource Management
Limit and monitor container resources.

**Tasks:**
1. Run container with memory limit (256MB)
2. Run container with CPU limit (0.5 cores)
3. Monitor resource usage

## ✅ Verification
After completing all exercises, run the verification script:
```bash
# See setup/verify.md for verification steps
```

## 🎯 Challenge
Complete the challenge in `solutions/challenge-solution.md`:
- Deploy a 3-tier application (frontend, backend, database)
- Ensure all containers can communicate
- Implement proper resource limits
- Use volumes for data persistence

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Permission denied | `sudo usermod -aG docker $USER && newgrp docker` |
| Port already in use | `sudo lsof -i :PORT` to find process |
| Cannot connect to Docker | `sudo systemctl restart docker` |
| Out of disk space | `docker system prune -af` |

## 📚 Additional Resources
- [Docker CLI Reference](https://docs.docker.com/engine/reference/commandline/cli/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## ⏭️ Next Lab
After mastering these basics, proceed to Lab 02: Dockerfile Basics
