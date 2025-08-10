# Lab 03: ConfigMaps & Secrets

## 🎯 Objectives
- Create and manage ConfigMaps
- Work with Kubernetes Secrets
- Mount configurations as volumes
- Use environment variables from ConfigMaps/Secrets
- Implement configuration hot-reload

## ⏱️ Duration: 45 minutes

## 📋 Prerequisites
- Completed Labs 01-02
- Running Kubernetes cluster
- Basic understanding of application configuration

## 🏗️ Architecture
```
┌──────────────────────────────────────┐
│         Configuration Sources        │
├──────────────────────────────────────┤
│  ConfigMaps          Secrets         │
│  ┌─────────┐      ┌──────────┐      │
│  │app.conf │      │ API Keys │      │
│  │db.conf  │      │Passwords │      │
│  └─────────┘      └──────────┘      │
│       ↓                 ↓            │
│  ┌────────────────────────────┐     │
│  │         Pod                │     │
│  │  ┌──────────────────┐     │     │
│  │  │ /config (volume) │     │     │
│  │  │ ENV Variables    │     │     │
│  │  └──────────────────┘     │     │
│  └────────────────────────────┘     │
└──────────────────────────────────────┘
```

## 📝 Instructions

### Step 1: Create ConfigMap from Literal Values

Create `manifests/configmap-literal.yaml`:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_MODE: "production"
  LOG_LEVEL: "info"
  MAX_CONNECTIONS: "100"
  CACHE_SIZE: "256MB"
  DATABASE_POOL_SIZE: "20"
```

Apply using kubectl:
```bash
# From YAML
kubectl apply -f manifests/configmap-literal.yaml

# From command line
kubectl create configmap app-config-cli \
  --from-literal=APP_MODE=development \
  --from-literal=LOG_LEVEL=debug

# View ConfigMap
kubectl describe configmap app-config
```

### Step 2: Create ConfigMap from Files

Create `config/app.properties`:
```properties
# Application Configuration
app.name=kubernetes-lab
app.version=3.0.0
app.environment=production

# Database Configuration
database.host=postgres.default.svc.cluster.local
database.port=5432
database.name=appdb
database.pool.size=20
database.pool.timeout=30s

# Cache Configuration
cache.enabled=true
cache.ttl=3600
cache.max.size=1000

# Feature Flags
feature.new-ui=enabled
feature.analytics=enabled
feature.experimental=disabled
```

Create `config/nginx.conf`:
```nginx
server {
    listen 80;
    server_name localhost;
    
    location / {
        root /usr/share/nginx/html;
        index index.html;
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    location /api {
        proxy_pass http://backend-service:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Create ConfigMap from files:
```bash
kubectl create configmap app-properties \
  --from-file=config/app.properties \
  --from-file=config/nginx.conf
```

### Step 3: Use ConfigMap as Environment Variables

Create `manifests/pod-with-configmap-env.yaml`:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: configmap-env-pod
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'env | grep -E "APP_|LOG_|MAX_" && sleep 3600']
    env:
    - name: APP_MODE
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: APP_MODE
    - name: LOG_LEVEL
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: LOG_LEVEL
    envFrom:
    - configMapRef:
        name: app-config
        prefix: CONFIG_
```

### Step 4: Mount ConfigMap as Volume

Create `manifests/pod-with-configmap-volume.yaml`:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: configmap-volume-pod
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
      readOnly: true
    - name: nginx-config
      mountPath: /etc/nginx/conf.d
      readOnly: true
    command: ["/bin/sh"]
    args: ["-c", "ls -la /etc/config && nginx -g 'daemon off;'"]
  volumes:
  - name: config-volume
    configMap:
      name: app-properties
      items:
      - key: app.properties
        path: application.conf
  - name: nginx-config
    configMap:
      name: app-properties
      items:
      - key: nginx.conf
        path: default.conf
```

### Step 5: Create and Use Secrets

Create `manifests/secret-literal.yaml`:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  # Values are base64 encoded
  # admin
  DB_USERNAME: YWRtaW4=
  # P@ssw0rd123
  DB_PASSWORD: UEBzc3cwcmQxMjM=
  # my-secret-api-key-12345
  API_KEY: bXktc2VjcmV0LWFwaS1rZXktMTIzNDU=
```

Create secrets using kubectl:
```bash
# From YAML
kubectl apply -f manifests/secret-literal.yaml

# From command line
kubectl create secret generic db-credentials \
  --from-literal=username=dbuser \
  --from-literal=password='S3cur3P@ss!'

# From files
echo -n 'admin' > ./username.txt
echo -n 'secretpassword' > ./password.txt
kubectl create secret generic file-secrets \
  --from-file=./username.txt \
  --from-file=./password.txt

# View secret (encoded)
kubectl get secret app-secrets -o yaml
```

### Step 6: Use Secrets in Pods

Create `manifests/pod-with-secrets.yaml`:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-pod
spec:
  containers:
  - name: app
    image: alpine
    command: ['sh', '-c', 'echo "DB User: $DB_USER" && echo "API Key exists: $(test -f /etc/secrets/api-key && echo yes || echo no)" && sleep 3600']
    env:
    - name: DB_USER
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: DB_USERNAME
    - name: DB_PASS
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: DB_PASSWORD
    volumeMounts:
    - name: secret-volume
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secret-volume
    secret:
      secretName: app-secrets
      defaultMode: 0400
      items:
      - key: API_KEY
        path: api-key
```

### Step 7: Create TLS Secret

Generate certificates:
```bash
# Generate private key
openssl genrsa -out tls.key 2048

# Generate certificate
openssl req -new -x509 -key tls.key -out tls.crt -days 365 -subj "/CN=app.local"

# Create TLS secret
kubectl create secret tls app-tls \
  --cert=tls.crt \
  --key=tls.key
```

Create `manifests/pod-with-tls.yaml`:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: tls-pod
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    volumeMounts:
    - name: tls-certs
      mountPath: /etc/nginx/certs
      readOnly: true
    - name: nginx-config
      mountPath: /etc/nginx/conf.d
  volumes:
  - name: tls-certs
    secret:
      secretName: app-tls
  - name: nginx-config
    configMap:
      name: nginx-tls-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-tls-config
data:
  default.conf: |
    server {
        listen 443 ssl;
        server_name app.local;
        
        ssl_certificate /etc/nginx/certs/tls.crt;
        ssl_certificate_key /etc/nginx/certs/tls.key;
        
        location / {
            root /usr/share/nginx/html;
            index index.html;
        }
    }
```

### Step 8: Dynamic Configuration Updates

Create `manifests/configmap-hot-reload.yaml`:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: dynamic-config
data:
  config.json: |
    {
      "version": "1.0.0",
      "features": {
        "feature1": true,
        "feature2": false
      },
      "settings": {
        "timeout": 30,
        "retries": 3
      }
    }
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: config-watcher
spec:
  replicas: 1
  selector:
    matchLabels:
      app: config-watcher
  template:
    metadata:
      labels:
        app: config-watcher
    spec:
      containers:
      - name: app
        image: busybox
        command: ["/bin/sh"]
        args:
        - -c
        - |
          while true; do
            echo "=== Configuration at $(date) ==="
            cat /config/config.json
            echo ""
            inotifywait -e modify /config/ 2>/dev/null || sleep 30
          done
        volumeMounts:
        - name: config
          mountPath: /config
      volumes:
      - name: config
        configMap:
          name: dynamic-config
```

### Step 9: Sealed Secrets (Production Pattern)

Create `manifests/deployment-with-config.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: secure-app
  template:
    metadata:
      labels:
        app: secure-app
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
    spec:
      serviceAccountName: secure-app
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
      containers:
      - name: app
        image: alpine
        command: ["/bin/sh"]
        args:
        - -c
        - |
          echo "Starting secure application..."
          echo "Environment: $ENVIRONMENT"
          echo "Database: $DB_HOST:$DB_PORT"
          echo "Checking mounted secrets..."
          ls -la /etc/secrets/
          sleep 3600
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: APP_MODE
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: database-config
              key: host
        - name: DB_PORT
          valueFrom:
            configMapKeyRef:
              name: database-config
              key: port
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: password
        volumeMounts:
        - name: app-config
          mountPath: /etc/config
          readOnly: true
        - name: secrets
          mountPath: /etc/secrets
          readOnly: true
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
      volumes:
      - name: app-config
        configMap:
          name: app-config
          defaultMode: 0444
      - name: secrets
        secret:
          secretName: app-secrets
          defaultMode: 0400
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: secure-app
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: database-config
data:
  host: "postgres.database.svc.cluster.local"
  port: "5432"
  database: "appdb"
---
apiVersion: v1
kind: Secret
metadata:
  name: database-secret
type: Opaque
stringData:
  username: dbadmin
  password: "MyS3cur3P@ssw0rd!"
```

## ✅ Verification Steps

Run `scripts/verify.sh`:
```bash
#!/bin/bash

echo "🔍 Verifying Lab 03..."

# Check ConfigMaps
echo "ConfigMaps:"
kubectl get configmaps
echo ""

# Check Secrets
echo "Secrets:"
kubectl get secrets
echo ""

# Verify environment variables
echo "Testing ConfigMap environment variables:"
kubectl exec configmap-env-pod -- env | grep -E "APP_|CONFIG_" || echo "Pod not found"
echo ""

# Verify mounted files
echo "Testing mounted ConfigMap:"
kubectl exec configmap-volume-pod -- ls -la /etc/config || echo "Pod not found"
echo ""

# Verify secret mounting
echo "Testing mounted Secrets:"
kubectl exec secret-pod -- ls -la /etc/secrets || echo "Pod not found"
echo ""

echo "✅ Lab 03 verification complete!"
```

## 🧹 Cleanup

Run `scripts/cleanup.sh`:
```bash
#!/bin/bash

echo "🧹 Cleaning up Lab 03..."

# Delete resources
kubectl delete -f manifests/ 2>/dev/null || true
kubectl delete configmap app-config-cli app-properties file-config 2>/dev/null || true
kubectl delete secret db-credentials file-secrets app-tls 2>/dev/null || true
kubectl delete pod configmap-env-pod configmap-volume-pod secret-pod tls-pod 2>/dev/null || true

# Clean up files
rm -f username.txt password.txt tls.key tls.crt

echo "✅ Cleanup complete!"
```

## 🐛 Troubleshooting

### ConfigMap Not Found
```bash
kubectl get configmap
kubectl describe pod <pod-name> | grep -A 10 Events
```

### Secret Decoding
```bash
# Decode base64 secret
kubectl get secret app-secrets -o jsonpath='{.data.DB_USERNAME}' | base64 -d
```

### Volume Mount Issues
```bash
kubectl describe pod <pod-name>
kubectl exec <pod-name> -- ls -la /mount/path
```

## 📚 Additional Resources
- [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Security Best Practices](https://kubernetes.io/docs/concepts/security/)