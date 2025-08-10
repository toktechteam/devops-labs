# ArgoCD GitOps Lab Setup

## Prerequisites

```bash
# Check Kubernetes cluster
kubectl cluster-info
kubectl get nodes

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify Helm
helm version
```

## Step 1: Install ArgoCD

```bash
# Create namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for pods to be ready
kubectl wait --for=condition=Ready pods --all -n argocd --timeout=300s

# Check pods
kubectl get pods -n argocd
```

## Step 2: Access ArgoCD UI

### Option A: Port Forwarding (Recommended for lab)

```bash
# Port forward ArgoCD server
kubectl port-forward svc/argocd-server -n argocd 8080:443 &

# Access at https://localhost:8080
```

### Option B: LoadBalancer

```bash
# Patch service to LoadBalancer
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'

# Get external IP
kubectl get svc argocd-server -n argocd
```

### Option C: Ingress

```bash
# Apply ingress
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: argocd-server-ingress
  namespace: argocd
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
spec:
  rules:
  - host: argocd.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: argocd-server
            port:
              number: 443
EOF
```

## Step 3: Login to ArgoCD

```bash
# Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Save password
ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
echo "Admin password: $ARGOCD_PASSWORD"

# Login via UI
# Username: admin
# Password: (from above)
```

## Step 4: Install ArgoCD CLI

```bash
# Download latest ArgoCD CLI
sudo curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64

# Make executable
sudo chmod +x /usr/local/bin/argocd

# Verify installation
argocd version

# Login to ArgoCD
argocd login localhost:8080 --username admin --password $ARGOCD_PASSWORD --insecure
```

## Step 5: Configure Git Repository

```bash
# Add repository to ArgoCD
argocd repo add https://github.com/<your-username>/gitops-demo \
  --username <github-username> \
  --password <github-token>

# Or for public repos
argocd repo add https://github.com/<your-username>/gitops-demo
```

## Step 6: Create First Application

### Via CLI:

```bash
# Create application
argocd app create demo-app \
  --repo https://github.com/<your-username>/gitops-demo \
  --path applications/demo-app/overlays/development \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace demo-dev \
  --sync-policy automated \
  --auto-prune \
  --self-heal

# Sync application
argocd app sync demo-app

# Check status
argocd app get demo-app
```

### Via UI:

1. Click "New App"
2. Enter application details:
    - Name: demo-app
    - Project: default
    - Sync Policy: Automatic
3. Source:
    - Repository: Your Git repo URL
    - Path: applications/demo-app/overlays/development
4. Destination:
    - Cluster: https://kubernetes.default.svc
    - Namespace: demo-dev
5. Click "Create"

## Step 7: Create App of Apps

```bash
# Apply app-of-apps pattern
kubectl apply -f argocd/applications/app-of-apps.yaml

# This will create all other applications
```

## Step 8: Configure RBAC

```bash
# Create RBAC policy
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-rbac-cm
  namespace: argocd
data:
  policy.default: role:readonly
  policy.csv: |
    p, role:developer, applications, get, */*, allow
    p, role:developer, applications, sync, */*, allow
    g, dev-team, role:developer
EOF

# Restart ArgoCD server
kubectl rollout restart deployment argocd-server -n argocd
```

## Step 9: Set Up Notifications

```bash
# Install ArgoCD Notifications
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj-labs/argocd-notifications/release-1.0/manifests/install.yaml

# Configure Slack notification
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-notifications-cm
  namespace: argocd
data:
  service.slack: |
    token: $slack-token
  template.app-deployed: |
    message: |
      Application {{.app.metadata.name}} is now running new version.
  trigger.on-deployed: |
    - when: app.status.operationState.phase in ['Succeeded']
      send: [app-deployed]
EOF
```

## Step 10: Verify Installation

```bash
# Check ArgoCD components
kubectl get all -n argocd

# Check applications
argocd app list

# Check repository
argocd repo list

# Check cluster
argocd cluster list

# View ArgoCD settings
argocd admin settings rbac
```

## Troubleshooting

### Cannot access UI
```bash
# Check service
kubectl get svc -n argocd

# Check port forwarding
ps aux | grep port-forward
```

### Application not syncing
```bash
# Check application status
argocd app get <app-name>

# Manual sync
argocd app sync <app-name>

# Check events
kubectl get events -n <namespace>
```

### Authentication issues
```bash
# Reset admin password
kubectl -n argocd patch secret argocd-secret \
  -p '{"data": {"admin.password": null, "admin.passwordMtime": null}}'

# Restart server
kubectl rollout restart deployment argocd-server -n argocd
```

## Next Steps

1. Create multiple applications
2. Implement Kustomize overlays
3. Set up automated sync policies
4. Configure webhook for automatic sync
5. Implement progressive delivery with Argo Rollouts