# GitHub Actions Lab Setup

## Prerequisites

1. **GitHub Account**
    - Sign up at https://github.com if you don't have one
    - Verify your email

2. **Docker Hub Account**
    - Sign up at https://hub.docker.com
    - Note your username and password

3. **Local Environment**
   ```bash
   # Install Git
   sudo apt-get update
   sudo apt-get install -y git
   
   # Configure Git
   git config --global user.name "Your Name"
   git config --global user.email "your-email@example.com"
   
   # Install Node.js (for local testing)
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `github-actions-demo`
3. Description: "CI/CD with GitHub Actions"
4. Public repository
5. Initialize with README
6. Click "Create repository"

## Step 2: Clone Repository

```bash
# Clone your repository
git clone https://github.com/<your-username>/github-actions-demo
cd github-actions-demo

# Create project structure
mkdir -p .github/workflows src tests k8s scripts
```

## Step 3: Add Application Code

```bash
# Copy application files from lab
cp ~/devops-labs/03-cicd-labs/lab-02-github-actions/src/* ./src/
cp ~/devops-labs/03-cicd-labs/lab-02-github-actions/tests/* ./tests/
cp ~/devops-labs/03-cicd-labs/lab-02-github-actions/Dockerfile ./
cp ~/devops-labs/03-cicd-labs/lab-02-github-actions/k8s/* ./k8s/

# Or create them manually from the artifacts
```

## Step 4: Configure Secrets

1. Go to repository Settings → Secrets and variables → Actions
2. Add the following secrets:

```yaml
DOCKER_USERNAME: your-dockerhub-username
DOCKER_PASSWORD: your-dockerhub-password
SLACK_WEBHOOK: your-slack-webhook-url (optional)
SONAR_TOKEN: your-sonarcloud-token (optional)
AWS_ACCESS_KEY_ID: your-aws-key (optional)
AWS_SECRET_ACCESS_KEY: your-aws-secret (optional)
```

## Step 5: Create Workflow

```bash
# Create main CI workflow
cp ~/devops-labs/03-cicd-labs/lab-02-github-actions/.github/workflows/ci.yml \
   ./.github/workflows/

# Create CD workflow
cp ~/devops-labs/03-cicd-labs/lab-02-github-actions/.github/workflows/cd.yml \
   ./.github/workflows/
```

## Step 6: Push to GitHub

```bash
# Add all files
git add .

# Commit
git commit -m "Initial CI/CD setup with GitHub Actions"

# Push to GitHub
git push origin main
```

## Step 7: Watch Pipeline

1. Go to your repository on GitHub
2. Click on "Actions" tab
3. You should see your workflow running
4. Click on the workflow to see details

## Step 8: Enable GitHub Pages (Optional)

1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: main
4. Folder: /docs
5. Save

## Step 9: Set Up Environments

1. Go to Settings → Environments
2. Create environments:
    - `development`
    - `staging`
    - `production` (with required reviewers)

## Step 10: Test Local Development

```bash
# Install dependencies
cd src
npm install

# Run tests
npm test

# Run application
npm start

# Test endpoints
curl http://localhost:3000
curl http://localhost:3000/health
```

## Verification

```bash
# Check GitHub Actions status
gh workflow list
gh run list

# Check Docker image
docker pull <your-dockerhub-username>/github-actions-demo:latest

# Run container locally
docker run -d -p 3000:3000 <your-dockerhub-username>/github-actions-demo:latest
```

## Troubleshooting

### Workflow not triggering
- Check branch name (main vs master)
- Check workflow syntax
- Check permissions

### Docker push failing
- Verify Docker Hub credentials
- Check repository name
- Ensure secrets are set correctly

### Tests failing
- Run tests locally first
- Check Node.js version
- Verify all dependencies installed

## Next Steps

1. Create a pull request to test PR workflows
2. Add more complex workflows
3. Implement deployment to cloud providers
4. Add security scanning
5. Set up monitoring and alerts