# Lab 03: GitLab CI/CD

## 🎯 Objectives
- Set up GitLab CI/CD pipelines
- Implement GitLab-specific features (Auto DevOps, Review Apps)
- Use GitLab Container Registry
- Implement security scanning (SAST, DAST, Container Scanning)
- Deploy with GitLab Environments
- Set up GitLab Pages for documentation

## ⏱️ Duration: 90 minutes

## 📋 Prerequisites
- GitLab account (free tier works)
- Docker installed locally
- Basic YAML knowledge
- Git configured

## 🏗️ Architecture

```
┌────────────────────────────────────────┐
│         GitLab Repository              │
│  ┌──────────────────────────────────┐ │
│  │      .gitlab-ci.yml              │ │
│  └──────────────────────────────────┘ │
└────────────┬───────────────────────────┘
             │
    ┌────────▼────────────┐
    │   GitLab Runner     │
    │  (Shared/Specific)  │
    └────────┬────────────┘
             │
    ┌────────▼────────────────────────┐
    │          Pipeline Stages         │
    │  ┌────────────────────────────┐ │
    │  │ Build → Test → Security    │ │
    │  │   ↓      ↓        ↓        │ │
    │  │ Package → Deploy → Monitor │ │
    │  └────────────────────────────┘ │
    └──────────────────────────────────┘
             │
    ┌────────▼────────────┐
    │  GitLab Registry    │
    └────────┬────────────┘
             │
    ┌────────▼────────────┐
    │    Environments      │
    │  • Review Apps       │
    │  • Staging          │
    │  • Production        │
    └─────────────────────┘
```

## 📁 Lab Structure
```
lab-03-gitlab-ci/
├── README.md (this file)
├── .gitlab-ci.yml
├── .gitlab/
│   ├── ci/
│   │   ├── build.gitlab-ci.yml
│   │   ├── test.gitlab-ci.yml
│   │   ├── security.gitlab-ci.yml
│   │   └── deploy.gitlab-ci.yml
│   └── agents/
│       └── k8s-agent/
│           └── config.yaml
├── src/
│   ├── app.rb
│   ├── Gemfile
│   └── config.ru
├── tests/
│   └── app_test.rb
├── Dockerfile
├── docker-compose.yml
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
├── docs/
│   └── index.html
├── setup/
│   ├── setup.md
│   └── verify.md
└── solutions/
    └── advanced-pipeline.yml
```

## 🚀 Quick Start

### Step 1: Create GitLab Project

1. Log in to GitLab (gitlab.com or self-hosted)
2. Create new project
3. Clone locally:
```bash
git clone https://gitlab.com/<username>/gitlab-ci-demo
cd gitlab-ci-demo
```

### Step 2: Enable GitLab Features

1. **Container Registry**: Settings → General → Visibility → Container Registry (Enable)
2. **CI/CD**: Settings → CI/CD → General pipelines (Expand)
3. **Environments**: Deployments → Environments
4. **Pages**: Settings → Pages

### Step 3: Create Pipeline

Create `.gitlab-ci.yml` in repository root.

### Step 4: Configure Variables

Settings → CI/CD → Variables:
- `DOCKER_AUTH_CONFIG`
- `DEPLOY_TOKEN`
- `PRODUCTION_URL`
- `STAGING_URL`

## 📝 Key GitLab CI Features

### Pipeline Features
- **Stages**: Sequential execution
- **Jobs**: Parallel execution within stages
- **Dependencies**: Artifact passing
- **Rules**: Conditional execution
- **Extends**: Template inheritance

### GitLab-Specific
- **Auto DevOps**: Automatic CI/CD
- **Review Apps**: Dynamic environments
- **GitLab Pages**: Static site hosting
- **Container Registry**: Built-in Docker registry
- **Security Dashboard**: Vulnerability management

## 🔒 Security Features
- SAST (Static Application Security Testing)
- DAST (Dynamic Application Security Testing)
- Container Scanning
- Dependency Scanning
- License Compliance
- Secret Detection

## 📚 Additional Resources
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [GitLab CI/CD Examples](https://gitlab.com/gitlab-org/gitlab/-/tree/master/lib/gitlab/ci/templates)
- [GitLab Runner Documentation](https://docs.gitlab.com/runner/)
