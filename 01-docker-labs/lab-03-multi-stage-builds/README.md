# Lab 03: Multi-Stage Builds

## 🎯 Objectives
- Master multi-stage Docker builds
- Optimize image size to production standards
- Implement build-time vs runtime separation
- Create minimal secure containers
- Build for multiple programming languages

## ⏱️ Duration: 75 minutes

## 📋 Prerequisites
- Completed Labs 01 and 02
- Understanding of basic Dockerfile concepts
- EC2 Ubuntu instance with Docker
- Go, Python, and Node.js basics

## 🏗️ Architecture

```
Multi-Stage Build Process:
┌────────────────┐
│ Stage 1: Build │
│   - Compiler   │
│   - Build deps │
│   - Source     │
└───────┬────────┘
        │ COPY artifacts
        ▼
┌────────────────┐
│ Stage 2: Test  │
│   - Test deps  │
│   - Run tests  │
└───────┬────────┘
        │ COPY binaries
        ▼
┌────────────────┐
│ Stage 3: Final │
│   - Minimal OS │
│   - Runtime    │
│   - Binary     │
└────────────────┘
     Size: <50MB
```

## 📁 Lab Structure
```
lab-03-multi-stage-builds/
├── README.md (this file)
├── go-app/
│   ├── main.go
│   ├── go.mod
│   └── Dockerfile
├── python-app/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── node-app/
│   ├── app.js
│   ├── package.json
│   └── Dockerfile
├── java-app/
│   ├── App.java
│   └── Dockerfile
├── rust-app/
│   ├── Cargo.toml
│   ├── src/main.rs
│   └── Dockerfile
├── setup/
│   ├── setup.md
│   └── verify.md
└── solutions/
    └── ultra-minimal.md
```

## 🚀 Quick Start

```bash
# Create lab directory
mkdir -p ~/docker-labs/lab-03-multi-stage-builds
cd ~/docker-labs/lab-03-multi-stage-builds

# Create subdirectories
mkdir -p {go-app,python-app,node-app,java-app,rust-app,setup,solutions}
```

## 📝 Exercises

### Exercise 1: Go Application (Smallest Image)

Build a Go web server with multi-stage build achieving <10MB image size.

### Exercise 2: Python Application

Optimize Python Flask app using multi-stage build.

### Exercise 3: Node.js Application

Create production-ready Node.js image with proper signal handling.

### Exercise 4: Java Application

Build Spring Boot app with JRE-only runtime image.

### Exercise 5: Rust Application

Compile Rust application to minimal static binary.

## ✅ Verification

Run verification steps in `setup/verify.md`.

## 🎯 Challenge

Create an image that:
- Final size <5MB
- Includes health check
- Runs as non-root
- Handles signals properly
- Zero CVE vulnerabilities

## 📚 Key Concepts

### Multi-Stage Benefits
- **Smaller Images**: Only runtime dependencies in final image
- **Better Security**: No build tools in production
- **Faster Deployments**: Smaller images = faster pulls
- **Clean Separation**: Build vs runtime environments

### Best Practices
1. Order stages from least to most frequently changing
2. Use specific tags for base images
3. Leverage build cache with proper layering
4. Copy only necessary artifacts between stages
5. Use scratch or distroless for ultimate minimalism

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Large final image | Check what's being copied from build stage |
| Missing dependencies | Static linking or copy runtime libs |
| Permission errors | Set proper ownership in COPY --chown |
| Signal handling issues | Use proper init system (tini, dumb-init) |

## 📚 Additional Resources
- [Docker Multi-stage Builds](https://docs.docker.com/develop/develop-images/multistage-build/)
- [Distroless Images](https://github.com/GoogleContainerTools/distroless)
- [Best Practices Guide](https://docs.docker.com/develop/dev-best-practices/)

## ⏭️ Next Lab
Proceed to Lab 04: Docker Compose