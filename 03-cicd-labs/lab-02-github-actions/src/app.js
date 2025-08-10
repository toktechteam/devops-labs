# Lab 02: GitHub Actions

## 🎯 Objectives
- Create GitHub Actions workflows
- Implement CI/CD pipelines with Actions
- Use Actions marketplace
- Build and push Docker images
- Deploy to multiple environments
- Implement security scanning and testing

## ⏱️ Duration: 75 minutes

## 📋 Prerequisites
- GitHub account (free)
- Git installed locally
- Docker Hub account (for image registry)
- Basic YAML knowledge

## 🏗️ Architecture

```
┌────────────────────────────────────────┐
│           GitHub Repository            │
│  ┌──────────────────────────────────┐ │
│  │     .github/workflows/           │ │
│  │  ├── ci.yml                     │ │
│  │  ├── cd.yml                     │ │
│  │  └── security.yml               │ │
│  └──────────────────────────────────┘ │
└────────────┬───────────────────────────┘
             │ Trigger
    ┌────────▼────────┐
    │  GitHub Actions │
    │     Runner      │
    └────────┬────────┘
             │
    ┌────────▼────────────┐
    │   Build & Test      │
    └────────┬────────────┘
             │
    ┌────────▼────────────┐
    │   Security Scan     │
    └────────┬────────────┘
             │
    ┌────────▼────────────┐
    │   Push to Registry  │
    └────────┬────────────┘
             │
    ┌────────▼────────────┐
    │     Deploy          │
    └─────────────────────┘
```

## 📁 Lab Structure
```
lab-02-github-actions/
├── README.md (this file)
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── cd.yml
│       ├── security.yml
│       ├── docker-build.yml
│       └── release.yml
├── src/
│   ├── app.js
│   └── package.json
├── tests/
│   └── app.test.js
├── Dockerfile
├── docker-compose.yml
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── scripts/
│   └── deploy.sh
├── setup/
│   ├── setup.md
│   └── verify.md
└── solutions/
    └── complete-workflow.yml
```

## 🚀 Quick Start

### Step 1: Fork/Create Repository

1. Create a new GitHub repository
2. Clone it locally:
```bash
git clone https://github.com/<your-username>/github-actions-demo
cd github-actions-demo
```

### Step 2: Create Application

Create a Node.js application for the demo.

### Step 3: Create Workflow

Create `.github/workflows/ci.yml` for continuous integration.

### Step 4: Push and Watch

```bash
git add .
git commit -m "Add CI workflow"
git push origin main
```

Go to Actions tab in GitHub to see workflow running.

## 📝 Key Concepts

### Workflow Triggers
- `push`: On code push
- `pull_request`: On PR events
- `schedule`: Cron-based triggers
- `workflow_dispatch`: Manual triggers
- `release`: On release events

### Job Configuration
- `runs-on`: Specify runner OS
- `strategy`: Matrix builds
- `needs`: Job dependencies
- `if`: Conditional execution

### Actions Marketplace
- Pre-built actions for common tasks
- Community and official actions
- Custom actions development

## 🔒 Secrets Management

Configure secrets in repository settings:
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
- `DEPLOY_TOKEN`
- `SONAR_TOKEN`

## ⚡ Exercises

See the workflow files for hands-on exercises.

## 📚 Additional Resources
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Actions Marketplace](https://github.com/marketplace)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
