# Terraform Labs

## 📚 Overview
Hands-on Infrastructure as Code labs progressing from Terraform basics to advanced state management and multi-cloud deployments.

## 🎯 Learning Path

| Lab | Title | Difficulty | Duration |
|-----|-------|------------|----------|
| 01 | Terraform Basics | ⭐ Beginner | 45 mins |
| 02 | AWS Infrastructure | ⭐ Beginner | 60 mins |
| 03 | Azure Resources | ⭐⭐ Intermediate | 60 mins |
| 04 | Modules & Workspaces | ⭐⭐ Intermediate | 75 mins |
| 05 | State Management | ⭐⭐⭐ Advanced | 90 mins |

## 🔧 Prerequisites

### Required Tools
```bash
# Terraform (1.5+ recommended)
terraform version

# AWS CLI (for Lab 02)
aws --version
aws configure

# Azure CLI (for Lab 03)
az --version
az login

# Optional: tfenv for version management
tfenv list-remote
tfenv install 1.5.0
tfenv use 1.5.0
```

### Cloud Accounts Setup
```bash
# AWS Setup
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"

# Azure Setup
az login
az account set --subscription "your-subscription-id"

# GCP Setup (optional)
gcloud auth application-default login
export GOOGLE_PROJECT="your-project-id"
```

## 📂 Lab Structure
Each lab contains:
- `README.md` - Detailed instructions
- `main.tf` - Main configuration
- `variables.tf` - Input variables
- `outputs.tf` - Output values
- `terraform.tfvars.example` - Example variable values
- `modules/` - Reusable modules (Lab 04-05)
- `scripts/` - Helper scripts

## 🚀 Quick Start
```bash
# Clone repository
git clone https://github.com/yourusername/devops-labs.git
cd devops-labs/04-terraform-labs

# Start with Lab 01
cd lab-01-terraform-basics
terraform init
terraform plan
```

## 📊 Progress Tracking
- [ ] Lab 01: Terraform Basics
- [ ] Lab 02: AWS Infrastructure
- [ ] Lab 03: Azure Resources
- [ ] Lab 04: Modules & Workspaces
- [ ] Lab 05: State Management

## 🎓 Skills You'll Learn
- Infrastructure as Code fundamentals
- Provider configuration and authentication
- Resource lifecycle management
- Module development and versioning
- Workspace management for environments
- Remote state backends and locking
- Import and migration strategies
- Security best practices

## 💰 Cost Warning
**IMPORTANT**: These labs will create real cloud resources that may incur costs. Always run `terraform destroy` after completing each lab to avoid charges.

## 📖 Additional Resources
- [Terraform Documentation](https://www.terraform.io/docs)
- [Terraform Registry](https://registry.terraform.io/)
- [Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/)