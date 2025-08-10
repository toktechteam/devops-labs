# Lab 04: Docker Compose

## 🎯 Objectives
- Orchestrate multi-container applications
- Define services, networks, and volumes declaratively
- Implement microservices architecture
- Manage application lifecycle with Compose
- Use environment-specific configurations

## ⏱️ Duration: 90 minutes

## 📋 Prerequisites
- Completed Labs 01-03
- Docker and Docker Compose installed
- Understanding of YAML syntax
- Basic networking knowledge

## 🏗️ Architecture

```
Docker Compose Stack:
┌─────────────────────────────────────┐
│         docker-compose.yml          │
├─────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐          │
│  │ Frontend│──│   API   │          │
│  │  (React)│  │ (Node)  │          │
│  └─────────┘  └────┬────┘          │
│                    │                │
│  ┌─────────┐  ┌────┴────┐          │
│  │  Redis  │──│Database │          │
│  │ (Cache) │  │ (MySQL) │          │
│  └─────────┘  └─────────┘          │
├─────────────────────────────────────┤
│         Networks & Volumes          │
└─────────────────────────────────────┘
```

## 📁 Lab Structure
```
lab-04-docker-compose/
├── README.md (this file)
├── docker-compose.yml
├── docker-compose.override.yml
├── docker-compose.prod.yml
├── .env
├── .env.example
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
├── backend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
├── database/
│   └── init.sql
├── nginx/
│   └── nginx.conf
├── setup/
│   ├── setup.md
│   └── verify.md
└── solutions/
    └── microservices-compose.yml
```

## 🚀 Quick Start

```bash
# Create lab directory
mkdir -p ~/docker-labs/lab-04-docker-compose
cd ~/docker-labs/lab-04-docker-compose

# Start the stack
docker-compose up -d

# View running services
docker-compose ps

# View logs
docker-compose logs -f

# Stop the stack
docker-compose down
```

## 📝 Key Commands

### Basic Operations
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose stop

# Restart services
docker-compose restart

# Remove everything
docker-compose down -v
```

### Service Management
```bash
# Scale service
docker-compose up -d --scale backend=3

# Execute command in service
docker-compose exec backend sh

# View service logs
docker-compose logs -f backend
```

### Development Workflow
```bash
# Use override file
docker-compose -f docker-compose.yml -f docker-compose.override.yml up

# Production deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Rebuild images
docker-compose build --no-cache
```

## 📚 Key Concepts

### Compose Features
- **Services**: Container definitions
- **Networks**: Container communication
- **Volumes**: Data persistence
- **Configs**: Configuration management
- **Secrets**: Sensitive data handling

### Best Practices
1. Use specific image tags
2. Define resource limits
3. Implement health checks
4. Use .env files for configuration
5. Separate dev/prod configurations

## ✅ Exercises

### Exercise 1: Basic Multi-Container App
Create a simple web app with database.

### Exercise 2: Microservices Architecture
Build a microservices application with multiple services.

### Exercise 3: Development vs Production
Implement environment-specific configurations.

### Exercise 4: Scaling and Load Balancing
Scale services and implement load balancing.

### Exercise 5: Advanced Networking
Create multiple networks for service isolation.

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port conflicts | Change port mappings or stop conflicting services |
| Service can't connect | Check network configuration and service names |
| Volume permission issues | Set proper user/group in Dockerfile |
| Environment variables not working | Check .env file and variable substitution |

## 📚 Additional Resources
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Compose File Reference](https://docs.docker.com/compose/compose-file/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## ⏭️ Next Lab
Proceed to Lab 05: Docker Networking