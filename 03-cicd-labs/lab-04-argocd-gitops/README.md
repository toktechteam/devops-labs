# Lab 04: ArgoCD GitOps

## 🎯 Objectives
- Install and configure ArgoCD
- Implement GitOps workflow
- Create ArgoCD Applications
- Set up automated sync policies
- Implement progressive delivery
- Configure RBAC and multi-tenancy

## ⏱️ Duration: 120 minutes

## 📋 Prerequisites
- Kubernetes cluster (k3s/minikube/EKS)
- kubectl configured
- Helm installed
- Git repository access
- Basic Kubernetes knowledge

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│            Git Repository               │
│  ┌───────────────────────────────────┐ │
│  │  Application Manifests            │ │
│  │  ├── base/                       │ │
│  │  ├── overlays/dev/              │ │
│  │  ├── overlays/staging/          │ │
│  │  └── overlays/production/       │ │
│  └───────────────────────────────────┘ │
└────────────┬────────────────────────────┘
             │ Pull
    ┌────────▼────────────┐
    │      ArgoCD         │
    │  ┌────────────────┐ │
    │  │  Application   │ │
    │  │  Controller    │ │
    │  └────────────────┘ │
    │  ┌────────────────┐ │
    │  │     Repo       │ │
    │  │    Server      │ │
    │  └────────────────┘ │
    └────────┬────────────┘
             │ Deploy
    ┌────────▼────────────┐
    │   Kubernetes        │
    │  ┌────────────────┐ │
    │  │  Development   │ │
    │  ├────────────────┤ │
    │  │    Staging     │ │
    │  ├────────────────┤ │
    │  │  Production    │ │
    │  └────────────────┘ │
    └─────────────────────┘
```

## 📁 Lab Structure
```
lab-04-argocd-gitops/
├── README.md (this file)
├── argocd/
│   ├── install/
│   │   ├── namespace.yaml
│   │   ├── argocd-install.yaml
│   │   └── values.yaml
│   ├── applications/
│   │   ├── app-of-apps.yaml
│   │   ├── development.yaml
│   │   ├── staging.yaml
│   │   └── production.yaml
│   └── projects/
│       ├── default.yaml
│       └── production.yaml
├── applications/
│   ├── demo-app/
│   │   ├── base/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   ├── configmap.yaml
│   │   │   └── kustomization.yaml
│   │   └── overlays/
│   │       ├── development/
│   │       ├── staging/
│   │       └── production/
│   └── monitoring/
│       ├── prometheus/
│       └── grafana/
├── scripts/
│   ├── install-argocd.sh
│   ├── configure-repos.sh
│   └── sync-apps.sh
├── setup/
│   ├── setup.md
│   └── verify.md
└── solutions/
    └── advanced-gitops.yaml
```

## 🚀 Quick Start

### Step 1: Install ArgoCD

```bash
# Create namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for pods to be ready
kubectl wait --for=condition=Ready pods --all -n argocd --timeout=300s

# Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### Step 2: Access ArgoCD UI

```bash
# Port forward
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Or expose via LoadBalancer/Ingress
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
```

Access UI at: https://localhost:8080
- Username: `admin`
- Password: (from Step 1)

### Step 3: Install ArgoCD CLI

```bash
# Download CLI
curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
chmod +x /usr/local/bin/argocd

# Login
argocd login localhost:8080
```

### Step 4: Create First Application

See application manifests in the lab files.

## 📝 Key Concepts

### GitOps Principles
1. **Declarative**: Entire system described declaratively
2. **Versioned**: Desired system state versioned in Git
3. **Automated**: Approved changes automatically applied
4. **Observable**: Easy to observe system state

### ArgoCD Components
- **Application**: K8s resources defined by a Git repo
- **Project**: Logical grouping of applications
- **Repository**: Git repository containing manifests
- **Cluster**: Target Kubernetes cluster

### Sync Strategies
- **Manual**: Require manual intervention
- **Automatic**: Auto-sync when Git changes
- **Self-Heal**: Auto-correct drift
- **Prune**: Remove resources not in Git

## 🔒 Security & RBAC

Configure RBAC for teams:
- Read-only access for developers
- Write access for DevOps
- Admin access for platform team

## 🎯 Exercises

1. Deploy application using ArgoCD
2. Implement Kustomize overlays
3. Set up automated sync
4. Configure progressive delivery
5. Implement RBAC

## 📚 Additional Resources
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [GitOps Working Group](https://github.com/gitops-working-group/gitops-working-group)
- [Kustomize Documentation](https://kustomize.io/)
