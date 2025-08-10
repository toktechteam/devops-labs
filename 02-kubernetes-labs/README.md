# Kubernetes Labs

## 📚 Overview
Hands-on Kubernetes labs progressing from basic pod management to advanced Helm deployments.

## 🎯 Learning Path

| Lab | Title | Difficulty | Duration |
|-----|-------|------------|----------|
| 01 | Pods & Deployments | ⭐ Beginner | 45 mins |
| 02 | Services & Networking | ⭐ Beginner | 60 mins |
| 03 | ConfigMaps & Secrets | ⭐⭐ Intermediate | 45 mins |
| 04 | Persistent Volumes | ⭐⭐ Intermediate | 60 mins |
| 05 | Helm Charts | ⭐⭐⭐ Advanced | 90 mins |

## 🔧 Prerequisites

### Required Tools
```bash
# Check Kubernetes version (1.28+ recommended)
kubectl version --client

# Check cluster access
kubectl cluster-info

# For local development, install ONE of:
# Option 1: Minikube
minikube version

# Option 2: Kind
kind version

# Option 3: Docker Desktop with Kubernetes enabled
```

### Setup Local Cluster
```bash
# Using Minikube
minikube start --cpus=2 --memory=4096

# Using Kind
kind create cluster --name devops-labs

# Verify cluster
kubectl get nodes
```

## 📂 Lab Structure
Each lab contains:
- `README.md` - Detailed instructions
- `manifests/` - Kubernetes YAML files
- `app/` - Sample applications
- `scripts/` - Automation scripts
- `solutions/` - Complete working solutions

## 🚀 Quick Start
```bash
# Clone repository
git clone https://github.com/yourusername/devops-labs.git
cd devops-labs/02-kubernetes-labs

# Start with Lab 01
cd lab-01-pods-deployments
cat README.md
```

## 📊 Progress Tracking
- [ ] Lab 01: Pods & Deployments
- [ ] Lab 02: Services & Networking
- [ ] Lab 03: ConfigMaps & Secrets
- [ ] Lab 04: Persistent Volumes
- [ ] Lab 05: Helm Charts

## 🎓 Skills You'll Learn
- Container orchestration fundamentals
- Kubernetes resource management
- Service discovery and networking
- Configuration management
- Storage orchestration
- Package management with Helm
- Production best practices

## 📖 Additional Resources
- [Official Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kubernetes API Reference](https://kubernetes.io/docs/reference/kubernetes-api/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)