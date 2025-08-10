# Lab 01: Pods & Deployments

## 🎯 Objectives
- Create and manage Kubernetes pods
- Deploy applications using Deployments
- Perform rolling updates and rollbacks
- Understand pod lifecycle and health checks

## ⏱️ Duration: 45 minutes

## 📋 Prerequisites
- Running Kubernetes cluster
- kubectl configured
- Basic YAML knowledge

## 🏗️ Architecture
```
┌─────────────────────────────────────┐
│         Kubernetes Cluster          │
├─────────────────────────────────────┤
│  Deployment (nginx-deployment)      │
│  ├── ReplicaSet                     │
│  │   ├── Pod-1 (nginx:1.21)        │
│  │   ├── Pod-2 (nginx:1.21)        │
│  │   └── Pod-3 (nginx:1.21)        │
└─────────────────────────────────────┘
```

## 📝 Instructions

### Step 1: Create Your First Pod

Create `manifests/simple-pod.yaml`:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
    environment: lab
spec:
  containers:
  - name: nginx
    image: nginx:1.21-alpine
    ports:
    - containerPort: 80
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

Apply and verify:
```bash
kubectl apply -f manifests/simple-pod.yaml
kubectl get pods
kubectl describe pod nginx-pod
kubectl logs nginx-pod
```

### Step 2: Multi-Container Pod

Create `manifests/multi-container-pod.yaml`:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: webapp-pod
spec:
  containers:
  - name: web-server
    image: nginx:1.21-alpine
    ports:
    - containerPort: 80
    volumeMounts:
    - name: shared-data
      mountPath: /usr/share/nginx/html
  - name: content-generator
    image: busybox:1.35
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo '<h1>Generated at: '$(date)'</h1>' > /html/index.html; sleep 10; done"]
    volumeMounts:
    - name: shared-data
      mountPath: /html
  volumes:
  - name: shared-data
    emptyDir: {}
```

Apply and test:
```bash
kubectl apply -f manifests/multi-container-pod.yaml
kubectl exec -it webapp-pod -c web-server -- cat /usr/share/nginx/html/index.html
```

### Step 3: Create a Deployment

Create `manifests/nginx-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21-alpine
        ports:
        - containerPort: 80
        env:
        - name: ENVIRONMENT
          value: "production"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
```

Deploy and manage:
```bash
kubectl apply -f manifests/nginx-deployment.yaml
kubectl get deployments
kubectl get replicasets
kubectl get pods -l app=nginx
```

### Step 4: Scale the Deployment

```bash
# Scale up
kubectl scale deployment nginx-deployment --replicas=5

# Watch pods being created
kubectl get pods -w

# Scale down
kubectl scale deployment nginx-deployment --replicas=2
```

### Step 5: Rolling Update

Update the deployment:
```bash
# Update image version
kubectl set image deployment/nginx-deployment nginx=nginx:1.22-alpine

# Check rollout status
kubectl rollout status deployment/nginx-deployment

# View rollout history
kubectl rollout history deployment/nginx-deployment
```

### Step 6: Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/nginx-deployment

# Rollback to specific revision
kubectl rollout undo deployment/nginx-deployment --to-revision=1
```

### Step 7: Advanced Deployment Strategies

Create `manifests/advanced-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp-deployment
  annotations:
    kubernetes.io/change-cause: "Initial deployment"
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  minReadySeconds: 10
  progressDeadlineSeconds: 600
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
        version: v1
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - webapp
              topologyKey: kubernetes.io/hostname
      containers:
      - name: webapp
        image: nginx:1.21-alpine
        ports:
        - containerPort: 80
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]
        startupProbe:
          httpGet:
            path: /
            port: 80
          failureThreshold: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          successThreshold: 1
          failureThreshold: 3
```

## ✅ Verification Steps

Run `scripts/verify.sh`:
```bash
#!/bin/bash
echo "🔍 Verifying Lab 01..."

# Check pods
echo "Checking pods..."
kubectl get pods

# Check deployments
echo "Checking deployments..."
kubectl get deployments

# Test pod connectivity
echo "Testing pod connectivity..."
POD_NAME=$(kubectl get pods -l app=nginx -o jsonpath='{.items[0].metadata.name}')
kubectl exec $POD_NAME -- curl -s localhost > /dev/null && echo "✅ Pod is responding" || echo "❌ Pod not responding"

# Check resource usage
echo "Resource usage:"
kubectl top pods

echo "✅ Lab 01 verification complete!"
```

## 🧹 Cleanup

Run `scripts/cleanup.sh`:
```bash
#!/bin/bash
echo "🧹 Cleaning up Lab 01..."

kubectl delete -f manifests/ 2>/dev/null || true
kubectl delete pod nginx-pod webapp-pod 2>/dev/null || true
kubectl delete deployment nginx-deployment webapp-deployment 2>/dev/null || true

echo "✅ Cleanup complete!"
```

## 🐛 Troubleshooting

### Pod Stuck in Pending
```bash
kubectl describe pod <pod-name>
kubectl get events --sort-by='.lastTimestamp'
```

### Pod CrashLoopBackOff
```bash
kubectl logs <pod-name> --previous
kubectl describe pod <pod-name>
```

### ImagePullBackOff
```bash
# Check image name and availability
kubectl describe pod <pod-name> | grep -A 5 Events
```

## 📚 Additional Resources
- [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)