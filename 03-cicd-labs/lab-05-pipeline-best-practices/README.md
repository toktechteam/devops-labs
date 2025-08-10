# Lab 05: Pipeline Best Practices

## 🎯 Objectives
- Implement CI/CD best practices across different platforms
- Create reusable pipeline components
- Implement advanced deployment strategies
- Set up comprehensive testing pyramid
- Configure monitoring and observability
- Implement security throughout the pipeline

## ⏱️ Duration: 120 minutes

## 📋 Prerequisites
- Completed Labs 01-04
- Understanding of CI/CD concepts
- Access to CI/CD platform (Jenkins/GitHub Actions/GitLab)
- Kubernetes cluster
- Monitoring stack (Prometheus/Grafana)

## 🏗️ Architecture

```
┌────────────────────────────────────────────┐
│           Best Practices Pipeline          │
├────────────────────────────────────────────┤
│                                            │
│  ┌──────────┐     ┌──────────┐           │
│  │  Commit  │────▶│  Build   │           │
│  └──────────┘     └────┬─────┘           │
│                        │                   │
│  ┌──────────────────────▼─────────────┐   │
│  │            Quality Gates           │   │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ │   │
│  │  │Lint │ │Test │ │SAST │ │Deps │ │   │
│  │  └─────┘ └─────┘ └─────┘ └─────┘ │   │
│  └──────────────────┬─────────────────┘   │
│                     │                      │
│  ┌──────────────────▼─────────────────┐   │
│  │         Artifact Management        │   │
│  │  ┌─────────┐  ┌──────────┐       │   │
│  │  │Container│  │Helm Chart│       │   │
│  │  └─────────┘  └──────────┘       │   │
│  └──────────────────┬─────────────────┘   │
│                     │                      │
│  ┌──────────────────▼─────────────────┐   │
│  │       Deployment Strategies        │   │
│  │  ┌─────────┐  ┌──────────┐       │   │
│  │  │Blue-Green│  │  Canary  │       │   │
│  │  └─────────┘  └──────────┘       │   │
│  └──────────────────┬─────────────────┘   │
│                     │                      │
│  ┌──────────────────▼─────────────────┐   │
│  │      Monitoring & Feedback         │   │
│  │  ┌─────────┐  ┌──────────┐       │   │
│  │  │ Metrics │  │  Alerts  │       │   │
│  │  └─────────┘  └──────────┘       │   │
│  └────────────────────────────────────┘   │
└────────────────────────────────────────────┘
```

## 📁 Lab Structure
```
lab-05-pipeline-best-practices/
├── README.md (this file)
├── jenkins/
│   ├── Jenkinsfile.best-practices
│   └── shared-library/
│       ├── vars/
│       │   ├── deployToKubernetes.groovy
│       │   ├── runSecurityScan.groovy
│       │   └── notifySlack.groovy
│       └── src/
│           └── com/company/Pipeline.groovy
├── github-actions/
│   ├── .github/
│   │   └── workflows/
│   │       ├── reusable-workflow.yml
│   │       ├── matrix-build.yml
│   │       └── deployment.yml
│   └── composite-actions/
│       ├── security-scan/action.yml
│       └── deploy/action.yml
├── gitlab-ci/
│   ├── .gitlab-ci.best-practices.yml
│   └── templates/
│       ├── security.gitlab-ci.yml
│       ├── deploy.gitlab-ci.yml
│       └── notify.gitlab-ci.yml
├── deployment-strategies/
│   ├── blue-green/
│   │   ├── deploy.sh
│   │   └── rollback.sh
│   ├── canary/
│   │   ├── deploy.yaml
│   │   └── analysis.yaml
│   └── rolling/
│       └── deployment.yaml
├── monitoring/
│   ├── prometheus/
│   │   └── alerts.yml
│   ├── grafana/
│   │   └── dashboard.json
│   └── datadog/
│       └── monitors.tf
├── security/
│   ├── scanning/
│   │   ├── trivy.yaml
│   │   ├── sonarqube.properties
│   │   └── snyk.config
│   ├── policies/
│   │   └── opa-policies.rego
│   └── compliance/
│       └── cis-benchmark.yaml
├── testing/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── performance/
│       └── k6-load-test.js
├── scripts/
│   ├── quality-gate.sh
│   ├── deploy.sh
│   └── rollback.sh
├── setup/
│   ├── setup.md
│   └── verify.md
└── solutions/
    ├── complete-pipeline.yml
    └── best-practices-checklist.md
```

## 🚀 Quick Start

```bash
# Create lab directory
mkdir -p ~/devops-labs/03-cicd-labs/lab-05-pipeline-best-practices
cd ~/devops-labs/03-cicd-labs/lab-05-pipeline-best-practices

# Choose your platform
# Jenkins / GitHub Actions / GitLab CI
```

## 📝 Best Practices Implementation

### 1. Pipeline as Code

**Principles:**
- Version control all pipeline definitions
- Use declarative syntax where possible
- Implement code review for pipeline changes
- Maintain pipeline documentation

**Example:**
```yaml
# All pipeline configuration in code
version: '1.0'
pipeline:
  stages:
    - build
    - test
    - deploy
```

### 2. Reusable Components

**Jenkins Shared Libraries:**
```groovy
@Library('pipeline-library') _

pipeline {
    stages {
        stage('Deploy') {
            steps {
                deployToKubernetes(
                    namespace: 'production',
                    manifest: 'k8s/deployment.yaml'
                )
            }
        }
    }
}
```

**GitHub Actions Composite:**
```yaml
- uses: ./.github/actions/deploy
  with:
    environment: production
    version: ${{ github.sha }}
```

**GitLab CI Templates:**
```yaml
include:
  - project: 'company/ci-templates'
    file: '/templates/deploy.yml'
```

### 3. Testing Pyramid

```
         /\
        /  \  E2E Tests (5%)
       /────\
      /      \  Integration Tests (15%)
     /────────\
    /          \  Unit Tests (80%)
   /────────────\
```

**Implementation:**
```yaml
test:
  parallel:
    - unit:
        script: npm run test:unit
        coverage: 80%
    - integration:
        script: npm run test:integration
        dependencies: [build]
    - e2e:
        script: npm run test:e2e
        when: manual
```

### 4. Security Integration

**Security Stages:**
```yaml
security:
  stages:
    - sast:
        tool: sonarqube
        gate: quality-gate
    - dependency-scan:
        tool: snyk
        severity: high
    - container-scan:
        tool: trivy
        fail-on: critical
    - dast:
        tool: zap
        target: staging-url
```

### 5. Deployment Strategies

#### Blue-Green Deployment
```bash
# Deploy to blue environment
kubectl set image deployment/app-blue app=myapp:v2

# Run tests
./test-deployment.sh blue

# Switch traffic
kubectl patch service app -p '{"spec":{"selector":{"version":"blue"}}}'

# Keep green as backup
kubectl annotate deployment/app-green backup=true
```

#### Canary Deployment
```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: app
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  progressDeadlineSeconds: 60
  service:
    port: 80
  analysis:
    interval: 1m
    threshold: 10
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      threshold: 99
```

#### Progressive Deployment
```yaml
stages:
  - deploy: 10%
    verify: metrics
    duration: 10m
  - deploy: 50%
    verify: metrics
    duration: 10m
  - deploy: 100%
    verify: metrics
```

### 6. Monitoring & Observability

**Pipeline Metrics:**
```yaml
metrics:
  - build_duration
  - test_coverage
  - deployment_frequency
  - lead_time
  - mttr
  - change_failure_rate
```

**Application Monitoring:**
```yaml
monitoring:
  prometheus:
    scrape_interval: 30s
    metrics:
      - http_requests_total
      - http_request_duration_seconds
      - error_rate
  grafana:
    dashboards:
      - pipeline-metrics
      - application-performance
  alerts:
    - name: high-error-rate
      threshold: 5%
    - name: slow-response
      threshold: 1s
```

## 📚 Key Concepts

### Quality Gates

**Definition:**
```yaml
quality-gates:
  - code-coverage:
      minimum: 80%
      fail-build: true
  - vulnerabilities:
      critical: 0
      high: 3
  - code-smells:
      maximum: 10
  - duplicated-lines:
      maximum: 5%
  - performance:
      response-time: <200ms
      throughput: >1000rps
```

### GitOps Principles

1. **Declarative Configuration**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  environment: production
  version: 1.0.0
```

2. **Version Controlled**
```bash
git add .
git commit -m "Update production config"
git push origin main
```

3. **Automated Deployment**
```yaml
sync:
  automated:
    prune: true
    selfHeal: true
```

4. **Continuous Reconciliation**
```yaml
reconciliation:
  interval: 5m
  retries: 3
```

### Pipeline Optimization

**Parallel Execution:**
```yaml
stages:
  - test:
      parallel:
        - unit-tests
        - integration-tests
        - security-scan
```

**Caching Strategies:**
```yaml
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - node_modules/
    - .m2/repository/
  policy: pull-push
```

**Incremental Builds:**
```groovy
changes = sh(
  script: "git diff --name-only HEAD~1",
  returnStdout: true
)
if (changes.contains('src/')) {
  sh 'make build'
}
```

## ✅ Exercises

### Exercise 1: Implement Reusable Pipeline

Create a shared library/action/template that can be used across multiple projects.

### Exercise 2: Multi-Environment Deployment

Set up a pipeline that deploys to dev → staging → production with appropriate gates.

### Exercise 3: Advanced Testing Strategy

Implement comprehensive testing with:
- Unit tests with 80% coverage
- Integration tests
- Contract tests
- Performance tests
- Security tests

### Exercise 4: Security Scanning Pipeline

Integrate:
- SAST (SonarQube)
- Dependency scanning (Snyk)
- Container scanning (Trivy)
- DAST (OWASP ZAP)
- License compliance

### Exercise 5: Monitoring & Alerting

Set up:
- Pipeline metrics dashboard
- Application performance monitoring
- Log aggregation
- Alert rules
- Incident management

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Slow pipelines | Implement caching, parallel execution, and incremental builds |
| Flaky tests | Add retry logic, improve test isolation, use test containers |
| Security vulnerabilities | Scan early, fail fast, automated patching |
| Deployment failures | Implement rollback, health checks, gradual rollout |
| Resource constraints | Use auto-scaling, resource limits, spot instances |
| Complex dependencies | Use dependency management, version pinning |

## 🎯 Best Practices Checklist

- [ ] **Version Control**: All pipeline code in Git
- [ ] **Modularity**: Reusable components and templates
- [ ] **Testing**: Comprehensive test pyramid
- [ ] **Security**: Integrated security scanning
- [ ] **Quality Gates**: Automated quality checks
- [ ] **Artifacts**: Versioned and immutable
- [ ] **Environments**: Consistent across stages
- [ ] **Deployment**: Zero-downtime strategies
- [ ] **Rollback**: Automated rollback capability
- [ ] **Monitoring**: Full observability
- [ ] **Documentation**: Pipeline and process docs
- [ ] **Secrets**: Secure secret management
- [ ] **Compliance**: Audit trails and compliance checks
- [ ] **Performance**: Optimized pipeline execution
- [ ] **Feedback**: Fast feedback loops

## 📊 Metrics to Track

### DORA Metrics
- **Deployment Frequency**: How often you deploy
- **Lead Time**: Commit to production time
- **MTTR**: Mean time to recovery
- **Change Failure Rate**: % of failed deployments

### Pipeline Metrics
- Build success rate
- Test coverage
- Pipeline duration
- Queue time
- Resource utilization

### Quality Metrics
- Code coverage
- Technical debt
- Security vulnerabilities
- Performance benchmarks

## 📚 Additional Resources
- [CI/CD Best Practices](https://www.atlassian.com/continuous-delivery/principles)
- [The DevOps Handbook](https://itrevolution.com/the-devops-handbook/)
- [Continuous Delivery](https://continuousdelivery.com/)
- [SRE Book](https://sre.google/sre-book/table-of-contents/)
- [12 Factor App](https://12factor.net/)

## ⏭️ Next Steps

Congratulations! You've completed the CI/CD labs. Consider:
- Implementing these practices in real projects
- Exploring advanced deployment strategies (Argo Rollouts, Flagger)
- Setting up production-grade monitoring (Datadog, New Relic)
- Obtaining certifications (CKA, AWS DevOps, Jenkins Engineer)
- Contributing to open-source CI/CD tools