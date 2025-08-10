# CI/CD Labs

## 📚 Overview
Comprehensive hands-on labs for mastering CI/CD pipelines, from basic automation to advanced GitOps practices.

## 🎯 Learning Path

| Lab | Title | Difficulty | Duration | Prerequisites |
|-----|-------|------------|----------|---------------|
| 01 | Jenkins Basics | 🟢 Beginner | 90 mins | Docker, Git basics |
| 02 | GitHub Actions | 🟢 Beginner | 75 mins | GitHub account, YAML |
| 03 | GitLab CI | 🟡 Intermediate | 90 mins | GitLab account, Docker |
| 04 | ArgoCD GitOps | 🟡 Intermediate | 120 mins | Kubernetes basics |
| 05 | Pipeline Best Practices | 🔴 Advanced | 120 mins | Complete labs 01-04 |

## 🔧 Prerequisites

### System Requirements (EC2 Ubuntu)
- Ubuntu 20.04/22.04 LTS
- Minimum t2.large instance (8GB RAM)
- 30GB storage
- Open ports: 8080, 9000, 3000, 80, 443

### Software Installation
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker

# Install Git
sudo apt-get install -y git

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install k3s (lightweight Kubernetes)
curl -sfL https://get.k3s.io | sh -
sudo chmod 644 /etc/rancher/k3s/k3s.yaml
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installations
docker --version
git --version
kubectl version --client
helm version
```

## 📈 Skills You'll Learn

### Core CI/CD Concepts
- **Continuous Integration**: Automated building and testing
- **Continuous Delivery**: Automated deployment preparation
- **Continuous Deployment**: Automated production deployment
- **Pipeline as Code**: Version-controlled pipeline definitions
- **GitOps**: Git as single source of truth

### Tools & Technologies
- **Jenkins**: Traditional CI/CD server
- **GitHub Actions**: Cloud-native CI/CD
- **GitLab CI**: Integrated DevOps platform
- **ArgoCD**: Kubernetes-native GitOps
- **Container Registry**: Image management
- **Security Scanning**: SAST, DAST, dependency scanning

### Best Practices
- Branch protection and PR workflows
- Automated testing strategies
- Secret management
- Pipeline optimization
- Monitoring and observability

## 🚀 Getting Started

```bash
# Clone the labs repository (or create structure)
mkdir -p ~/devops-labs/03-cicd-labs
cd ~/devops-labs/03-cicd-labs

# Create lab directories
for i in {01..05}; do
  mkdir -p lab-0$i-*/setup
done

# Start with Lab 01
cd lab-01-jenkins-basics
```

## 📝 Lab Structure

Each lab follows this structure:
```
lab-XX-name/
├── README.md           # Lab instructions
├── Dockerfile         # Application container
├── Jenkinsfile        # Pipeline definition
├── .github/           # GitHub Actions workflows
│   └── workflows/
├── .gitlab-ci.yml     # GitLab CI configuration
├── k8s/               # Kubernetes manifests
│   ├── deployment.yaml
│   └── service.yaml
├── src/               # Application source code
│   ├── app.py
│   └── requirements.txt
├── tests/             # Test files
│   └── test_app.py
├── setup/             # Setup instructions
│   ├── setup.md
│   └── verify.md
└── solutions/         # Complete solutions
    └── pipeline-complete.yaml
```

## 🏆 Challenges

After completing all labs, you'll be able to:
- Build a complete CI/CD pipeline from scratch
- Implement GitOps for Kubernetes deployments
- Set up multi-environment deployments
- Integrate security scanning into pipelines
- Implement blue-green and canary deployments

## 📊 Progress Tracking

- [ ] Lab 01: Set up Jenkins and create first pipeline
- [ ] Lab 02: Build GitHub Actions workflow
- [ ] Lab 03: Create GitLab CI pipeline
- [ ] Lab 04: Deploy with ArgoCD
- [ ] Lab 05: Implement advanced patterns

## 🔐 Security Considerations

All labs implement security best practices:
- No hardcoded secrets
- Least privilege access
- Container image scanning
- SAST/DAST integration
- Supply chain security

## 📖 Additional Resources

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [GitLab CI/CD Docs](https://docs.gitlab.com/ee/ci/)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [The DevOps Handbook](https://www.amazon.com/DevOps-Handbook-World-Class-Reliability-Organizations/dp/1942788002)

## ⚠️ Important Notes

1. **Costs**: Some labs may incur AWS costs (EC2, storage)
2. **Cleanup**: Always clean up resources after completing labs
3. **Security**: Never commit real secrets to repositories
4. **Versions**: Labs tested with specific tool versions (see each lab's README)

## 🤝 Contributing

Found an issue or want to improve the labs?
1. Test your changes thoroughly
2. Ensure all code works on Ubuntu 22.04
3. Document any new dependencies
4. Include verification steps

## 📧 Support

For issues or questions:
- Check the troubleshooting section in each lab
- Review the solutions directory
- Consult the official documentation

---
Ready to master CI/CD? Start with [Lab 01: Jenkins Basics](03-cicd-labs/lab-01-jenkins-basics/README.md) →
