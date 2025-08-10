# Lab 02: Services & Networking

## 🎯 Objectives
- Create different types of Kubernetes Services
- Implement service discovery
- Configure Ingress controllers
- Understand network policies

## ⏱️ Duration: 60 minutes

## 📋 Prerequisites
- Completed Lab 01
- Running Kubernetes cluster
- kubectl configured

## 🏗️ Architecture
```
┌────────────────────────────────────────────┐
│              Ingress Controller            │
├────────────────────────────────────────────┤
│     Service (LoadBalancer/NodePort)        │
├────────────────────────────────────────────┤
│          ClusterIP Services                │
│  ┌─────────────┐      ┌─────────────┐     │
│  │  Frontend   │ ---> │   Backend   │     │
│  │   Service   │      │   Service   │     │
│  └─────────────┘      └─────────────┘     │
│        ↓                     ↓             │
│  ┌─────────────┐      ┌─────────────┐     │
│  │Frontend Pods│      │Backend Pods │     │
│  └─────────────┘      └─────────────┘     │
└────────────────────────────────────────────┘
```

## 📝 Instructions

### Step 1: Deploy Backend Application

Create `app/backend/server.js`:
```javascript
const express = require('express');
const app = express();
const PORT = 3000;

app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    hostname: require('os').hostname()
  });
});

app.get('/api/data', (req, res) => {
  res.json({
    message: 'Hello from backend',
    version: '1.0.0',
    pod: require('os').hostname(),
    headers: req.headers
  });
});

app.listen(PORT, () => {
  console.log(`Backend server running on port ${PORT}`);
});
```

Create `app/backend/package.json`:
```json
{
  "name": "backend-service",
  "version": "1.0.0",
  "main": "server.js",
  "dependencies": {
    "express": "^4.18.2"
  },
  "scripts": {
    "start": "node server.js"
  }
}
```

Create `app/backend/Dockerfile`:
```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

Create `manifests/backend-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
        tier: backend
    spec:
      containers:
      - name: backend
        image: node:16-alpine
        command: ["/bin/sh"]
        args: ["-c", "npm install express && node -e \"$(cat <<'EOF'
const express = require('express');
const app = express();
const PORT = 3000;

app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    hostname: require('os').hostname()
  });
});

app.get('/api/data', (req, res) => {
  res.json({
    message: 'Hello from backend',
    version: '1.0.0',
    pod: require('os').hostname()
  });
});

app.listen(PORT, () => {
  console.log('Backend server running on port ' + PORT);
});
EOF
)\""]
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
```

### Step 2: Create ClusterIP Service

Create `manifests/backend-service.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  labels:
    app: backend
spec:
  type: ClusterIP
  selector:
    app: backend
  ports:
  - port: 80
    targetPort: 3000
    protocol: TCP
    name: http
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
```

Deploy backend:
```bash
kubectl apply -f manifests/backend-deployment.yaml
kubectl apply -f manifests/backend-service.yaml
kubectl get svc backend-service
```

### Step 3: Deploy Frontend Application

Create `manifests/frontend-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
        tier: frontend
    spec:
      containers:
      - name: frontend
        image: nginx:alpine
        ports:
        - containerPort: 80
        volumeMounts:
        - name: config
          mountPath: /usr/share/nginx/html
        - name: nginx-config
          mountPath: /etc/nginx/conf.d
      volumes:
      - name: config
        configMap:
          name: frontend-config
      - name: nginx-config
        configMap:
          name: nginx-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-config
data:
  index.html: |
    <!DOCTYPE html>
    <html>
    <head>
        <title>Kubernetes Service Demo</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            button { padding: 10px 20px; margin: 10px; cursor: pointer; }
            #response { background: #f0f0f0; padding: 20px; margin-top: 20px; border-radius: 5px; }
            .success { color: green; }
            .error { color: red; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Kubernetes Services Lab</h1>
            <button onclick="testBackend()">Test Backend Service</button>
            <button onclick="testDNS()">Test DNS Resolution</button>
            <div id="response"></div>
        </div>
        <script>
            async function testBackend() {
                try {
                    const response = await fetch('/api/data');
                    const data = await response.json();
                    document.getElementById('response').innerHTML = 
                        '<h3 class="success">Backend Response:</h3><pre>' + 
                        JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('response').innerHTML = 
                        '<h3 class="error">Error:</h3>' + error.message;
                }
            }

            async function testDNS() {
                try {
                    const response = await fetch('/api/health');
                    const data = await response.json();
                    document.getElementById('response').innerHTML = 
                        '<h3 class="success">Health Check:</h3><pre>' + 
                        JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('response').innerHTML = 
                        '<h3 class="error">Error:</h3>' + error.message;
                }
            }
        </script>
    </body>
    </html>
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
data:
  default.conf: |
    upstream backend {
        server backend-service:80;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        location / {
            root /usr/share/nginx/html;
            index index.html;
        }
        
        location /api/ {
            proxy_pass http://backend/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
```

### Step 4: Create NodePort Service

Create `manifests/frontend-service-nodeport.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-nodeport
spec:
  type: NodePort
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080
    protocol: TCP
```

Deploy frontend:
```bash
kubectl apply -f manifests/frontend-deployment.yaml
kubectl apply -f manifests/frontend-service-nodeport.yaml
kubectl get svc frontend-nodeport
```

### Step 5: Create LoadBalancer Service

Create `manifests/frontend-service-loadbalancer.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-loadbalancer
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
spec:
  type: LoadBalancer
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
  externalTrafficPolicy: Local
```

### Step 6: Implement Headless Service

Create `manifests/headless-service.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-headless
spec:
  clusterIP: None
  selector:
    app: backend
  ports:
  - port: 3000
    targetPort: 3000
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: backend-stateful
spec:
  serviceName: backend-headless
  replicas: 3
  selector:
    matchLabels:
      app: backend-stateful
  template:
    metadata:
      labels:
        app: backend-stateful
    spec:
      containers:
      - name: backend
        image: busybox
        command: ['sh', '-c', 'echo "Pod $(hostname)" && sleep 3600']
```

### Step 7: Configure Ingress

Create `manifests/ingress.yaml`:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  ingressClassName: nginx
  rules:
  - host: app.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-nodeport
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
  - host: backend.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
```

### Step 8: Network Policies

Create `manifests/network-policy.yaml`:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: frontend
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 3000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          app: dns
    ports:
    - protocol: UDP
      port: 53
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-network-policy
spec:
  podSelector:
    matchLabels:
      app: frontend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 80
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: backend
    ports:
    - protocol: TCP
      port: 3000
```

### Step 9: Service Discovery Testing

Create `scripts/test-service-discovery.sh`:
```bash
#!/bin/bash

echo "🔍 Testing Service Discovery..."

# Create test pod
kubectl run test-pod --image=busybox --rm -it --restart=Never -- sh -c "
echo 'Testing DNS resolution...'
nslookup backend-service
echo ''
echo 'Testing service connectivity...'
wget -qO- backend-service/api/health
echo ''
echo 'Testing headless service...'
nslookup backend-headless
"

echo "✅ Service discovery test complete!"
```

## ✅ Verification Steps

Run `scripts/verify.sh`:
```bash
#!/bin/bash

echo "🔍 Verifying Lab 02..."

# Check services
echo "Services:"
kubectl get svc

# Check endpoints
echo -e "\nEndpoints:"
kubectl get endpoints

# Test service DNS
echo -e "\nTesting DNS resolution:"
kubectl run dns-test --image=busybox --rm -it --restart=Never -- nslookup backend-service

# Check ingress
echo -e "\nIngress:"
kubectl get ingress

# Test connectivity
if [ -x "$(command -v minikube)" ]; then
    NODE_IP=$(minikube ip)
    NODE_PORT=$(kubectl get svc frontend-nodeport -o jsonpath='{.spec.ports[0].nodePort}')
    echo -e "\nTesting NodePort service:"
    curl -s http://$NODE_IP:$NODE_PORT || echo "NodePort not accessible"
fi

echo "✅ Lab 02 verification complete!"
```

## 🧹 Cleanup

Run `scripts/cleanup.sh`:
```bash
#!/bin/bash

echo "🧹 Cleaning up Lab 02..."

kubectl delete -f manifests/ 2>/dev/null || true
kubectl delete pod test-pod 2>/dev/null || true

echo "✅ Cleanup complete!"
```

## 🐛 Troubleshooting

### Service Not Reachable
```bash
# Check service and endpoints
kubectl describe svc <service-name>
kubectl get endpoints <service-name>

# Test from within cluster
kubectl run debug --image=busybox --rm -it --restart=Never -- wget -qO- <service-name>
```

### Ingress Not Working
```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress resource
kubectl describe ingress app-ingress

# Check ingress logs
kubectl logs -n ingress-nginx <ingress-controller-pod>
```

### DNS Resolution Issues
```bash
# Check CoreDNS
kubectl get pods -n kube-system | grep coredns

# Test DNS
kubectl run dns-test --image=busybox --rm -it --restart=Never -- nslookup kubernetes.default
```

## 📚 Additional Resources
- [Services](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)