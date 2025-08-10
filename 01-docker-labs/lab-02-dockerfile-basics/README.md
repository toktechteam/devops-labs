# Lab 02: Dockerfile Basics

## 🎯 Objectives
- Write production-ready Dockerfiles
- Understand build context and layer caching
- Implement security best practices
- Optimize image size and build time

## ⏱️ Duration: 60 minutes

## 📋 Prerequisites
- Completed Lab 01
- Basic understanding of Python/Node.js
- Docker installed on EC2 Ubuntu

## 🏗️ Lab Architecture

```
Build Process Flow:
┌──────────────┐
│  Dockerfile  │
└──────┬───────┘
       ▼
┌──────────────┐     ┌──────────────┐
│ Build Context│────▶│ Docker Daemon│
└──────────────┘     └──────┬───────┘
                            ▼
                     ┌──────────────┐
                     │ Layer Cache  │
                     └──────┬───────┘
                            ▼
                     ┌──────────────┐
                     │ Base Image   │
                     ├──────────────┤
                     │ RUN commands │
                     ├──────────────┤
                     │ COPY files   │
                     ├──────────────┤
                     │ Final Image  │
                     └──────────────┘
```

## 📁 Lab Structure
```
lab-02-dockerfile-basics/
├── README.md (this file)
├── Dockerfile
├── Dockerfile.optimized
├── Dockerfile.multistage
├── app.py
├── app.js
├── requirements.txt
├── package.json
├── .dockerignore
├── setup/
│   ├── setup.md
│   └── verify.md
├── solutions/
│   ├── Dockerfile.secure
│   ├── Dockerfile.minimal
│   └── challenge-solution.md
└── config/
    └── nginx.conf
```

## 🚀 Quick Start

```bash
# Create lab directory
mkdir -p ~/docker-labs/lab-02-dockerfile-basics
cd ~/docker-labs/lab-02-dockerfile-basics

# Copy all lab files or create them from this guide
# Then follow setup/setup.md
```

## 📝 Exercises

### Exercise 1: Basic Dockerfile
Create a simple Dockerfile for a Python Flask application.

**Tasks:**
1. Use Python 3.11 as base image
2. Install dependencies
3. Copy application code
4. Expose port 5000
5. Run the application

### Exercise 2: Layer Optimization
Optimize the Dockerfile for better caching.

**Tasks:**
1. Order instructions from least to most frequently changing
2. Combine RUN commands
3. Use specific base image tags
4. Minimize layers

### Exercise 3: Security Best Practices
Implement security improvements.

**Tasks:**
1. Run as non-root user
2. Use official base images
3. Don't install unnecessary packages
4. Scan for vulnerabilities

### Exercise 4: Multi-Stage Build
Create a multi-stage build to reduce image size.

**Tasks:**
1. Separate build and runtime stages
2. Copy only necessary artifacts
3. Use minimal base image for final stage
4. Achieve <100MB final image

### Exercise 5: Build Arguments and Environment Variables
Use build-time and runtime configuration.

**Tasks:**
1. Use ARG for build-time variables
2. Use ENV for runtime variables
3. Override defaults with --build-arg
4. Use .env file for secrets

## ✅ Verification
Run the verification steps in `setup/verify.md` to ensure all exercises are completed correctly.

## 🎯 Challenge
Create an ultra-optimized Dockerfile that:
- Final image size <50MB
- Builds in <30 seconds
- Runs as non-root
- Includes health check
- Uses multi-stage build

See `solutions/challenge-solution.md` for the answer.

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | Check Dockerfile syntax, ensure all files exist |
| Large image size | Use multi-stage builds, alpine base images |
| Slow builds | Optimize layer caching, use .dockerignore |
| Permission errors | Check file ownership, USER directive |

## 📚 Additional Resources
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Multi-stage Builds](https://docs.docker.com/develop/develop-images/multistage-build/)

## ⏭️ Next Lab
Proceed to Lab 03: Multi-Stage Builds for advanced optimization techniques.
