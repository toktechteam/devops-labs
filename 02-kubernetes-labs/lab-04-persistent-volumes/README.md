# Lab 04: Persistent Volumes

## 🎯 Objectives
- Create and manage PersistentVolumes (PV)
- Work with PersistentVolumeClaims (PVC)
- Implement different storage classes
- Deploy stateful applications
- Understand volume snapshots and backups

## ⏱️ Duration: 60 minutes

## 📋 Prerequisites
- Completed Labs 01-03
- Running Kubernetes cluster
- Storage provisioner (hostPath for local, CSI for cloud)

## 🏗️ Architecture
```
┌────────────────────────────────────────┐
│         Storage Architecture           │
├────────────────────────────────────────┤
│     StorageClass → Dynamic PV          │
│            ↓                           │
│    PersistentVolume (PV)               │
│            ↓                           │
│   PersistentVolumeClaim (PVC)          │
│            ↓                           │
│   ┌─────────────────────┐              │
│   │    StatefulSet      │              │
│   │   ┌───────────┐     │              │
│   │   │   Pod-0   │     │              │
│   │   │  PVC-0 ←──┼─────┼──→ PV-0     │
│   │   └───────────┘     │              │
│   │   ┌───────────┐     │              │
│   │   │   Pod-1   │     │              │
│   │   │  PVC-1 ←──┼─────┼──→ PV-1     │
│   │   └───────────┘     │              │
│   └─────────────────────┘              │
└────────────────────────────────────────┘
```

## 📝 Instructions

### Step 1: Create a PersistentVolume

Create `manifests/pv-hostpath.yaml`:
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-hostpath-manual
  labels:
    type: local
spec:
  storageClassName: manual
  capacity:
    storage: 2Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: "/mnt/data/pv-manual"
    type: DirectoryOrCreate
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-hostpath-shared
  labels:
    type: local
spec:
  storageClassName: manual
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Recycle
  hostPath:
    path: "/mnt/data/pv-shared"
    type: DirectoryOrCreate
```

Apply and verify:
```bash
kubectl apply -f manifests/pv-hostpath.yaml
kubectl get pv
kubectl describe pv pv-hostpath-manual
```

### Step 2: Create PersistentVolumeClaim

Create `manifests/pvc-manual.yaml`:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-manual
spec:
  storageClassName: manual
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  selector:
    matchLabels:
      type: local
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-shared
spec:
  storageClassName: manual
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 3Gi
```

Create and verify:
```bash
kubectl apply -f manifests/pvc-manual.yaml
kubectl get pvc
kubectl describe pvc pvc-manual
```

### Step 3: Use PVC in a Pod

Create `manifests/pod-with-pvc.yaml`:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-storage
spec:
  containers:
  - name: app
    image: nginx:alpine
    volumeMounts:
    - name: data-volume
      mountPath: /usr/share/nginx/html
    - name: shared-volume
      mountPath: /data/shared
  initContainers:
  - name: setup
    image: busybox
    command: ['sh', '-c']
    args:
    - |
      echo "<h1>Persistent Volume Test</h1>" > /data/index.html
      echo "<p>Pod: $(hostname)</p>" >> /data/index.html
      echo "<p>Date: $(date)</p>" >> /data/index.html
      echo "Shared data" > /shared/data.txt
    volumeMounts:
    - name: data-volume
      mountPath: /data
    - name: shared-volume
      mountPath: /shared
  volumes:
  - name: data-volume
    persistentVolumeClaim:
      claimName: pvc-manual
  - name: shared-volume
    persistentVolumeClaim:
      claimName: pvc-shared
```

Deploy and test:
```bash
kubectl apply -f manifests/pod-with-pvc.yaml
kubectl exec pod-with-storage -- cat /usr/share/nginx/html/index.html
```

### Step 4: Dynamic Provisioning with StorageClass

Create `manifests/storageclass.yaml`:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: k8s.io/minikube-hostpath  # Change for your environment
parameters:
  type: pd-ssd
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: slow-disk
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: k8s.io/minikube-hostpath
parameters:
  type: pd-standard
reclaimPolicy: Retain
volumeBindingMode: Immediate
```

### Step 5: Deploy MySQL with Persistent Storage

Create `manifests/mysql-pvc.yaml`:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 10Gi
```

Create `manifests/mysql-deployment.yaml`:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
type: Opaque
stringData:
  root-password: "MyR00tP@ssw0rd"
  database: "labdb"
  user: "labuser"
  password: "L@bP@ssw0rd"
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-config
data:
  my.cnf: |
    [mysqld]
    port = 3306
    socket = /var/run/mysqld/mysqld.sock
    datadir = /var/lib/mysql
    default_storage_engine = InnoDB
    character-set-server = utf8mb4
    collation-server = utf8mb4_unicode_ci
    max_connections = 100
    innodb_buffer_pool_size = 256M
    innodb_log_file_size = 64M
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: root-password
        - name: MYSQL_DATABASE
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: database
        - name: MYSQL_USER
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: user
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: password
        ports:
        - containerPort: 3306
        volumeMounts:
        - name: mysql-storage
          mountPath: /var/lib/mysql
        - name: mysql-config
          mountPath: /etc/mysql/conf.d
        livenessProbe:
          exec:
            command:
            - mysqladmin
            - ping
            - -h
            - localhost
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - mysql
            - -h
            - localhost
            - -e
            - "SELECT 1"
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: mysql-storage
        persistentVolumeClaim:
          claimName: mysql-pvc
      - name: mysql-config
        configMap:
          name: mysql-config
---
apiVersion: v1
kind: Service
metadata:
  name: mysql
spec:
  selector:
    app: mysql
  ports:
  - port: 3306
    targetPort: 3306
  clusterIP: None
```

### Step 6: StatefulSet with Persistent Volumes

Create `manifests/statefulset-postgres.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-headless
spec:
  clusterIP: None
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres-headless
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14-alpine
        env:
        - name: POSTGRES_DB
          value: "testdb"
        - name: POSTGRES_USER
          value: "testuser"
        - name: POSTGRES_PASSWORD
          value: "testpass"
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - testuser
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - testuser
          initialDelaySeconds: 5
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 5Gi
```

### Step 7: Volume Snapshots

Create `manifests/volume-snapshot.yaml`:
```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-snapclass
driver: hostpath.csi.k8s.io  # Change based on your CSI driver
deletionPolicy: Delete
---
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: mysql-snapshot
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: mysql-pvc
```

### Step 8: Backup and Restore Application

Create `scripts/backup-restore.sh`:
```bash
#!/bin/bash

# Backup function
backup_mysql() {
    echo "📦 Creating MySQL backup..."
    
    POD_NAME=$(kubectl get pods -l app=mysql -o jsonpath='{.items[0].metadata.name}')
    
    kubectl exec $POD_NAME -- mysqldump \
        -u root \
        -p'MyR00tP@ssw0rd' \
        --all-databases \
        --single-transaction \
        --routines \
        --triggers > mysql-backup-$(date +%Y%m%d-%H%M%S).sql
    
    echo "✅ Backup completed"
}

# Restore function
restore_mysql() {
    echo "📥 Restoring MySQL backup..."
    
    if [ -z "$1" ]; then
        echo "Usage: restore_mysql <backup-file>"
        return 1
    fi
    
    POD_NAME=$(kubectl get pods -l app=mysql -o jsonpath='{.items[0].metadata.name}')
    
    kubectl exec -i $POD_NAME -- mysql \
        -u root \
        -p'MyR00tP@ssw0rd' < $1
    
    echo "✅ Restore completed"
}

# Volume backup using jobs
create_backup_job() {
    kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: volume-backup-$(date +%Y%m%d-%H%M%S)
spec:
  template:
    spec:
      containers:
      - name: backup
        image: busybox
        command: ["/bin/sh"]
        args:
        - -c
        - |
          echo "Starting backup..."
          tar -czf /backup/data-$(date +%Y%m%d-%H%M%S).tar.gz /data/*
          echo "Backup completed"
          ls -la /backup/
        volumeMounts:
        - name: data
          mountPath: /data
        - name: backup
          mountPath: /backup
      restartPolicy: Never
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: pvc-manual
      - name: backup
        persistentVolumeClaim:
          claimName: backup-pvc
EOF
}

case "$1" in
    backup)
        backup_mysql
        ;;
    restore)
        restore_mysql $2
        ;;
    volume-backup)
        create_backup_job
        ;;
    *)
        echo "Usage: $0 {backup|restore <file>|volume-backup}"
        exit 1
        ;;
esac
```

### Step 9: Advanced Storage Patterns

Create `manifests/redis-cluster.yaml`:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: redis-config
data:
  redis.conf: |
    maxmemory 256mb
    maxmemory-policy allkeys-lru
    save 900 1
    save 300 10
    save 60 10000
    appendonly yes
    appendfilename "appendonly.aof"
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis
spec:
  serviceName: redis-headless
  replicas: 3
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      initContainers:
      - name: config
        image: redis:7-alpine
        command: ['sh', '-c']
        args:
        - |
          cp /mnt/config/redis.conf /etc/redis/redis.conf
          echo "replica-announce-ip ${POD_IP}" >> /etc/redis/redis.conf
          echo "replica-announce-port 6379" >> /etc/redis/redis.conf
        env:
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        volumeMounts:
        - name: config
          mountPath: /mnt/config
        - name: redis-config
          mountPath: /etc/redis
      containers:
      - name: redis
        image: redis:7-alpine
        command: ["redis-server"]
        args: ["/etc/redis/redis.conf"]
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: data
          mountPath: /data
        - name: redis-config
          mountPath: /etc/redis
        livenessProbe:
          tcpSocket:
            port: 6379
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config
        configMap:
          name: redis-config
      - name: redis-config
        emptyDir: {}
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 1Gi
---
apiVersion: v1
kind: Service
metadata:
  name: redis-headless
spec:
  clusterIP: None
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
```

### Step 10: Test Data Persistence

Create `scripts/test-persistence.sh`:
```bash
#!/bin/bash

echo "🔍 Testing data persistence..."

# Test MySQL persistence
test_mysql() {
    echo "Testing MySQL..."
    
    POD_NAME=$(kubectl get pods -l app=mysql -o jsonpath='{.items[0].metadata.name}')
        USE labdb;
        CREATE TABLE IF NOT EXISTS test_table (
            id INT PRIMARY KEY AUTO_INCREMENT,
            data VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO test_table (data) VALUES ('Test data $(date)');
        SELECT * FROM test_table;"
    
    # Delete pod
    echo "Deleting MySQL pod..."
    kubectl delete pod $POD_NAME
    
    # Wait for new pod
    sleep 30
    
    # Check data persistence
    NEW_POD=$(kubectl get pods -l app=mysql -o jsonpath='{.items[0].metadata.name}')
    echo "Checking data in new pod: $NEW_POD"
    kubectl exec $NEW_POD -- mysql -u root -p'MyR00tP@ssw0rd' -e "
        USE labdb;
        SELECT * FROM test_table;"
}

# Test Redis persistence
test_redis() {
    echo "Testing Redis..."
    
    POD_NAME=$(kubectl get pods -l app=redis -o jsonpath='{.items[0].metadata.name}')
    
    # Set test data
    kubectl exec $POD_NAME -- redis-cli SET testkey "testvalue-$(date)"
    kubectl exec $POD_NAME -- redis-cli GET testkey
    
    # Force save
    kubectl exec $POD_NAME -- redis-cli BGSAVE
    sleep 5
    
    # Delete pod
    echo "Deleting Redis pod..."
    kubectl delete pod $POD_NAME
    
    # Wait for new pod
    sleep 20
    
    # Check data persistence
    NEW_POD=$(kubectl get pods -l app=redis -o jsonpath='{.items[0].metadata.name}')
    echo "Checking data in new pod: $NEW_POD"
    kubectl exec $NEW_POD -- redis-cli GET testkey
}

# Test StatefulSet ordering
test_statefulset() {
    echo "Testing StatefulSet..."
    
    for i in 0 1 2; do
        POD="postgres-$i"
        echo "Checking $POD..."
        kubectl exec $POD -- psql -U testuser -d testdb -c "
            CREATE TABLE IF NOT EXISTS test_data (
                id SERIAL PRIMARY KEY,
                pod_name VARCHAR(100),
                data TEXT
            );
            INSERT INTO test_data (pod_name, data) 
            VALUES ('$POD', 'Data from $POD at $(date)');
            SELECT * FROM test_data;"
    done
}

case "$1" in
    mysql)
        test_mysql
        ;;
    redis)
        test_redis
        ;;
    statefulset)
        test_statefulset
        ;;
    all)
        test_mysql
        echo ""
        test_redis
        echo ""
        test_statefulset
        ;;
    *)
        echo "Usage: $0 {mysql|redis|statefulset|all}"
        exit 1
        ;;
esac

echo "✅ Persistence test complete!"