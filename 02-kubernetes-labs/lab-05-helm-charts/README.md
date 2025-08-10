# Lab 05: Helm Charts

## 🎯 Objectives
- Install and configure Helm
- Create custom Helm charts
- Deploy applications using Helm
- Manage releases and rollbacks
- Work with Helm repositories

## ⏱️ Duration: 90 minutes

## 📋 Prerequisites
- Completed Labs 01-04
- Running Kubernetes cluster
- Helm 3.x installed

## 🏗️ Architecture
```
┌────────────────────────────────────────┐
│           Helm Architecture            │
├────────────────────────────────────────┤
│     Helm Client → Helm Repository      │
│            ↓                           │
│        Chart Package                   │
│            ↓                           │
│    Values.yaml + Templates             │
│            ↓                           │
│     Kubernetes Manifests               │
│            ↓                           │
│   ┌─────────────────────┐              │
│   │  Release (webapp)   │              │
│   │  ├── Deployment     │              │
│   │  ├── Service        │              │
│   │  ├── ConfigMap      │              │
│   │  └── Ingress        │              │
│   └─────────────────────┘              │
└────────────────────────────────────────┘
```

## 📝 Instructions

### Step 1: Install Helm

```bash
# Install Helm (if not already installed)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installation
helm version

# Add common repositories
helm repo add stable https://charts.helm.sh/stable
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
```

### Step 2: Create Your First Helm Chart

Create chart structure:
```bash
# Create new chart
helm create webapp-chart

# Chart structure
tree webapp-chart/
```

Update `webapp-chart/Chart.yaml`:
```yaml
apiVersion: v2
name: webapp-chart
description: A Helm chart for deploying a full-stack web application
type: application
version: 1.0.0
appVersion: "2.0.0"
keywords:
  - webapp
  - nodejs
  - mongodb
home: https://github.com/yourusername/webapp-chart
sources:
  - https://github.com/yourusername/webapp
maintainers:
  - name: DevOps Team
    email: devops@example.com
dependencies:
  - name: mongodb
    version: "13.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: mongodb.enabled
```

### Step 3: Customize Templates

Update `webapp-chart/templates/deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "webapp-chart.fullname" . }}
  labels:
    {{- include "webapp-chart.labels" . | nindent 4 }}
    version: {{ .Values.image.tag | default .Chart.AppVersion }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  strategy:
    type: {{ .Values.strategy.type }}
    {{- if eq .Values.strategy.type "RollingUpdate" }}
    rollingUpdate:
      maxSurge: {{ .Values.strategy.rollingUpdate.maxSurge }}
      maxUnavailable: {{ .Values.strategy.rollingUpdate.maxUnavailable }}
    {{- end }}
  selector:
    matchLabels:
      {{- include "webapp-chart.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        checksum/secret: {{ include (print $.Template.BasePath "/secret.yaml") . | sha256sum }}
        {{- with .Values.podAnnotations }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      labels:
        {{- include "webapp-chart.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "webapp-chart.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      initContainers:
        - name: wait-for-db
          image: busybox:1.35
          command: ['sh', '-c']
          args:
            - |
              until nc -z {{ .Values.mongodb.service.name | default "mongodb" }} {{ .Values.mongodb.service.port | default 27017 }}; do
                echo "Waiting for MongoDB..."
                sleep 2
              done
              echo "MongoDB is ready!"
      containers:
        - name: {{ .Chart.Name }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.targetPort | default 3000 }}
              protocol: TCP
          env:
            - name: NODE_ENV
              value: {{ .Values.environment }}
            - name: PORT
              value: "{{ .Values.service.targetPort | default 3000 }}"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: {{ include "webapp-chart.fullname" . }}-secret
                  key: database-url
            {{- range $key, $value := .Values.env }}
            - name: {{ $key }}
              value: {{ $value | quote }}
            {{- end }}
          envFrom:
            - configMapRef:
                name: {{ include "webapp-chart.fullname" . }}-config
          livenessProbe:
            httpGet:
              path: {{ .Values.healthcheck.liveness.path }}
              port: http
            initialDelaySeconds: {{ .Values.healthcheck.liveness.initialDelaySeconds }}
            periodSeconds: {{ .Values.healthcheck.liveness.periodSeconds }}
            timeoutSeconds: {{ .Values.healthcheck.liveness.timeoutSeconds }}
            failureThreshold: {{ .Values.healthcheck.liveness.failureThreshold }}
          readinessProbe:
            httpGet:
              path: {{ .Values.healthcheck.readiness.path }}
              port: http
            initialDelaySeconds: {{ .Values.healthcheck.readiness.initialDelaySeconds }}
            periodSeconds: {{ .Values.healthcheck.readiness.periodSeconds }}
            timeoutSeconds: {{ .Values.healthcheck.readiness.timeoutSeconds }}
            successThreshold: {{ .Values.healthcheck.readiness.successThreshold }}
          {{- if .Values.startupProbe.enabled }}
          startupProbe:
            httpGet:
              path: {{ .Values.healthcheck.startup.path }}
              port: http
            failureThreshold: {{ .Values.healthcheck.startup.failureThreshold }}
            periodSeconds: {{ .Values.healthcheck.startup.periodSeconds }}
          {{- end }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          volumeMounts:
            - name: app-config
              mountPath: /app/config
            {{- if .Values.persistence.enabled }}
            - name: data
              mountPath: {{ .Values.persistence.mountPath }}
            {{- end }}
      volumes:
        - name: app-config
          configMap:
            name: {{ include "webapp-chart.fullname" . }}-config
        {{- if .Values.persistence.enabled }}
        - name: data
          persistentVolumeClaim:
            claimName: {{ include "webapp-chart.fullname" . }}-pvc
        {{- end }}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

Create `webapp-chart/templates/configmap.yaml`:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "webapp-chart.fullname" . }}-config
  labels:
    {{- include "webapp-chart.labels" . | nindent 4 }}
data:
  APP_NAME: {{ .Values.appConfig.name | quote }}
  APP_VERSION: {{ .Chart.AppVersion | quote }}
  LOG_LEVEL: {{ .Values.appConfig.logLevel | quote }}
  {{- range $key, $value := .Values.appConfig.features }}
  FEATURE_{{ $key | upper }}: {{ $value | quote }}
  {{- end }}
  config.json: |
    {
      "app": {
        "name": "{{ .Values.appConfig.name }}",
        "version": "{{ .Chart.AppVersion }}",
        "environment": "{{ .Values.environment }}"
      },
      "features": {{ .Values.appConfig.features | toJson }},
      "api": {
        "timeout": {{ .Values.appConfig.api.timeout }},
        "retries": {{ .Values.appConfig.api.retries }}
      }
    }
```

Create `webapp-chart/templates/secret.yaml`:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "webapp-chart.fullname" . }}-secret
  labels:
    {{- include "webapp-chart.labels" . | nindent 4 }}
type: Opaque
data:
  {{- if .Values.mongodb.enabled }}
  database-url: {{ printf "mongodb://%s:%s@%s:%d/%s" .Values.mongodb.auth.username .Values.mongodb.auth.password (include "webapp-chart.mongodb.fullname" .) (.Values.mongodb.service.port | int) .Values.mongodb.auth.database | b64enc }}
  {{- else }}
  database-url: {{ .Values.externalDatabase.url | b64enc }}
  {{- end }}
  {{- range $key, $value := .Values.secrets }}
  {{ $key }}: {{ $value | b64enc }}
  {{- end }}
```

### Step 4: Configure Values

Update `webapp-chart/values.yaml`:
```yaml
# Default values for webapp-chart
replicaCount: 3

image:
  repository: nginx
  pullPolicy: IfNotPresent
  tag: "1.21-alpine"

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

environment: production

strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0

serviceAccount:
  create: true
  annotations: {}
  name: ""

podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "3000"

podSecurityContext:
  fsGroup: 2000
  runAsNonRoot: true
  runAsUser: 1000

securityContext:
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: false
  allowPrivilegeEscalation: false

service:
  type: ClusterIP
  port: 80
  targetPort: 3000
  annotations: {}

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: app.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: app-tls
      hosts:
        - app.example.com

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

persistence:
  enabled: true
  storageClass: "fast-ssd"
  accessMode: ReadWriteOnce
  size: 10Gi
  mountPath: /data

healthcheck:
  liveness:
    path: /health
    initialDelaySeconds: 30
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3
  readiness:
    path: /ready
    initialDelaySeconds: 5
    periodSeconds: 5
    timeoutSeconds: 3
    successThreshold: 1
  startup:
    path: /health
    failureThreshold: 30
    periodSeconds: 10

startupProbe:
  enabled: true

nodeSelector: {}
tolerations: []
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app.kubernetes.io/name
            operator: In
            values:
            - webapp-chart
        topologyKey: kubernetes.io/hostname

# Application configuration
appConfig:
  name: "WebApp"
  logLevel: "info"
  features:
    newUI: true
    analytics: true
    betaFeatures: false
  api:
    timeout: 30
    retries: 3

# Secrets (will be base64 encoded)
secrets:
  apiKey: "my-secret-api-key"
  jwtSecret: "my-jwt-secret-key"

# Environment variables
env:
  TZ: "UTC"
  MAX_WORKERS: "4"

# MongoDB subchart configuration
mongodb:
  enabled: true
  auth:
    enabled: true
    username: webapp
    password: secretpassword
    database: webappdb
  persistence:
    enabled: true
    size: 20Gi
  service:
    name: mongodb
    port: 27017

# External database (if mongodb.enabled is false)
externalDatabase:
  url: "mongodb://external-host:27017/webapp"
```

### Step 5: Create Environment-Specific Values

Create `webapp-chart/values-dev.yaml`:
```yaml
environment: development
replicaCount: 1

image:
  tag: "latest"

appConfig:
  logLevel: "debug"
  features:
    betaFeatures: true

resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi

autoscaling:
  enabled: false

ingress:
  hosts:
    - host: dev.app.example.com
      paths:
        - path: /
          pathType: Prefix
```

Create `webapp-chart/values-prod.yaml`:
```yaml
environment: production
replicaCount: 5

appConfig:
  logLevel: "warn"

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 5
  maxReplicas: 20
```

### Step 6: Add Hooks and Tests

Create `webapp-chart/templates/tests/test-connection.yaml`:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "webapp-chart.fullname" . }}-test-connection"
  labels:
    {{- include "webapp-chart.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": test
spec:
  containers:
    - name: wget
      image: busybox
      command: ['wget']
      args: ['{{ include "webapp-chart.fullname" . }}:{{ .Values.service.port }}']
  restartPolicy: Never
```

Create `webapp-chart/templates/hooks/pre-install-job.yaml`:
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: "{{ include "webapp-chart.fullname" . }}-pre-install"
  labels:
    {{- include "webapp-chart.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": pre-install
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  template:
    metadata:
      name: "{{ include "webapp-chart.fullname" . }}"
      labels:
        {{- include "webapp-chart.selectorLabels" . | nindent 8 }}
    spec:
      restartPolicy: Never
      containers:
        - name: pre-install
          image: busybox
          command: ['sh', '-c']
          args:
            - |
              echo "Running pre-install tasks..."
              echo "Checking cluster resources..."
              echo "Setup complete!"
```

### Step 7: Deploy with Helm

```bash
# Lint the chart
helm lint webapp-chart/

# Dry run to preview
helm install webapp webapp-chart/ --dry-run --debug

# Install the chart
helm install webapp webapp-chart/

# Install with custom values
helm install webapp-dev webapp-chart/ -f webapp-chart/values-dev.yaml

# Upgrade a release
helm upgrade webapp webapp-chart/ --set image.tag=2.0.0

# Check release status
helm status webapp

# List releases
helm list

# Run tests
helm test webapp
```

### Step 8: Create Chart Repository

Create `scripts/package-chart.sh`:
```bash
#!/bin/bash

CHART_DIR="webapp-chart"
REPO_DIR="charts-repo"

# Package chart
helm package $CHART_DIR

# Create repo index
mkdir -p $REPO_DIR
mv *.tgz $REPO_DIR/
helm repo index $REPO_DIR --url https://yourdomain.com/charts

echo "✅ Chart packaged and repository index created"
```

### Step 9: Advanced Helm Patterns

Create `webapp-chart/templates/NOTES.txt`:
```
🎉 {{ .Chart.Name }} has been deployed!

Chart Version: {{ .Chart.Version }}
App Version: {{ .Chart.AppVersion }}
Release: {{ .Release.Name }}
Namespace: {{ .Release.Namespace }}

To access your application:

{{- if .Values.ingress.enabled }}
  {{- range $host := .Values.ingress.hosts }}
    {{- range .paths }}
  http{{ if $.Values.ingress.tls }}s{{ end }}://{{ $host.host }}{{ .path }}
    {{- end }}
  {{- end }}
{{- else if contains "NodePort" .Values.service.type }}
  export NODE_PORT=$(kubectl get --namespace {{ .Release.Namespace }} -o jsonpath="{.spec.ports[0].nodePort}" services {{ include "webapp-chart.fullname" . }})
  export NODE_IP=$(kubectl get nodes --namespace {{ .Release.Namespace }} -o jsonpath="{.items[0].status.addresses[0].address}")
  echo http://$NODE_IP:$NODE_PORT
{{- else if contains "LoadBalancer" .Values.service.type }}
  NOTE: It may take a few minutes for the LoadBalancer IP to be available.
  You can watch the status by running:
  kubectl get --namespace {{ .Release.Namespace }} svc -w {{ include "webapp-chart.fullname" . }}
{{- else if contains "ClusterIP" .Values.service.type }}
  kubectl port-forward --namespace {{ .Release.Namespace }} svc/{{ include "webapp-chart.fullname" . }} 8080:{{ .Values.service.port }}
  echo "Visit http://127.0.0.1:8080 to use your application"
{{- end }}

To check the status:
  helm status {{ .Release.Name }}

To run tests:
  helm test {{ .Release.Name }}

To uninstall:
  helm uninstall {{ .Release.Name }}
```

### Step 10: Umbrella Chart

Create `umbrella-chart/Chart.yaml`:
```yaml
apiVersion: v2
name: microservices-stack
description: Umbrella chart for microservices deployment
type: application
version: 1.0.0
dependencies:
  - name: webapp-chart
    version: "1.0.0"
    repository: "file://../webapp-chart"
    alias: frontend
  - name: webapp-chart
    version: "1.0.0"
    repository: "file://../webapp-chart"
    alias: backend
  - name: postgresql
    version: "12.x.x"
    repository: "https://charts.bitnami.com/bitnami"
  - name: redis
    version: "17.x.x"
    repository: "https://charts.bitnami.com/bitnami"
  - name: rabbitmq
    version: "11.x.x"
    repository: "https://charts.bitnami.com/bitnami"
```

## ✅ Verification Steps

Run `scripts/verify.sh`:
```bash
#!/bin/bash

echo "🔍 Verifying Lab 05..."

# Check Helm version
echo "Helm version:"
helm version --short

# List repositories
echo -e "\nHelm repositories:"
helm repo list

# List releases
echo -e "\nHelm releases:"
helm list --all-namespaces

# Check specific release
if helm list | grep -q webapp; then
    echo -e "\nWebapp release status:"
    helm status webapp
    
    echo -e "\nRelease values:"
    helm get values webapp
    
    echo -e "\nRelease history:"
    helm history webapp
fi

# Check deployed resources
echo -e "\nDeployed resources:"
kubectl get all -l app.kubernetes.io/instance=webapp

echo "✅ Lab 05 verification complete!"
```

## 🧹 Cleanup

Run `scripts/cleanup.sh`:
```bash
#!/bin/bash

echo "🧹 Cleaning up Lab 05..."

# List all releases
RELEASES=$(helm list -q)

# Uninstall releases
for release in $RELEASES; do
    echo "Uninstalling $release..."
    helm uninstall $release
done

# Clean up PVCs
kubectl delete pvc --all

# Remove local charts
rm -rf webapp-chart/charts
rm -f webapp-chart/Chart.lock
rm -f webapp-chart-*.tgz

echo "✅ Cleanup complete!"
```

## 🐛 Troubleshooting

### Chart Installation Fails
```bash
# Debug with dry-run
helm install webapp webapp-chart/ --dry-run --debug

# Check generated manifests
helm template webapp webapp-chart/

# Lint chart
helm lint webapp-chart/
```

### Dependencies Not Downloading
```bash
# Update dependencies
helm dependency update webapp-chart/

# List dependencies
helm dependency list webapp-chart/
```

### Release Stuck
```bash
# Check release status
helm status webapp

# Get release manifests
helm get manifest webapp

# Force delete
helm uninstall webapp --no-hooks
```

## 📚 Additional Resources
- [Helm Documentation](https://helm.sh/docs/)
- [Chart Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Helm Hub](https://artifacthub.io/)
- [Chart Testing](https://github.com/helm/chart-testing)