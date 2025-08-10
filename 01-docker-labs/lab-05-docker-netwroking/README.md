# Lab 05: Docker Networking

## 🎯 Objectives
- Master Docker networking concepts
- Implement network isolation and segmentation
- Configure custom networks and drivers
- Build service mesh patterns
- Implement load balancing and service discovery

## ⏱️ Duration: 120 minutes

## 📋 Prerequisites
- Completed Labs 01-04
- Understanding of TCP/IP networking
- Basic knowledge of DNS and routing
- Docker and Docker Compose installed

## 🏗️ Architecture

```
Docker Network Types:
┌────────────────────────────────────┐
│           Host Network              │
├────────────────────────────────────┤
│        Bridge Networks              │
│  ┌──────────┐    ┌──────────┐     │
│  │ Default  │    │  Custom  │     │
│  │  Bridge  │    │  Bridge  │     │
│  └──────────┘    └──────────┘     │
├────────────────────────────────────┤
│         Overlay Network            │
│  ┌──────────────────────────┐     │
│  │   Multi-Host Networking   │     │
│  └──────────────────────────┘     │
├────────────────────────────────────┤
│         MacVLAN Network            │
│  ┌──────────────────────────┐     │
│  │   Direct Physical Access  │     │
│  └──────────────────────────┘     │
└────────────────────────────────────┘
```

## 📁 Lab Structure
```
lab-05-docker-networking/
├── README.md (this file)
├── bridge-network/
│   ├── docker-compose.yml
│   └── test-connectivity.sh
├── overlay-network/
│   ├── docker-compose.yml
│   └── swarm-setup.sh
├── macvlan-network/
│   ├── setup.sh
│   └── test.sh
├── service-mesh/
│   ├── docker-compose.yml
│   ├── consul-config.json
│   └── envoy-config.yaml
├── load-balancing/
│   ├── docker-compose.yml
│   ├── haproxy.cfg
│   └── nginx.conf
├── setup/
│   ├── setup.md
│   └── verify.md
└── solutions/
    └── advanced-networking.md
```

## 🚀 Quick Start

```bash
# Create lab directory
mkdir -p ~/docker-labs/lab-05-docker-networking
cd ~/docker-labs/lab-05-docker-networking

# List current networks
docker network ls

# Inspect default bridge
docker network inspect bridge

# Create custom network
docker network create --driver bridge myapp-network
```

## 📝 Key Concepts

### Network Drivers

#### 1. Bridge (Default)
- Single host networking
- Containers can communicate via IP
- Port mapping for external access

#### 2. Host
- No network isolation
- Container uses host networking directly
- Best performance

#### 3. Overlay
- Multi-host networking
- Requires Swarm mode or external key-value store
- Encrypted communication

#### 4. MacVLAN
- Assigns MAC address to container
- Appears as physical device on network
- Direct external connectivity

#### 5. None
- No networking
- Complete isolation

### Network Commands

```bash
# Create network
docker network create [OPTIONS] NETWORK

# List networks
docker network ls

# Inspect network
docker network inspect NETWORK

# Connect container to network
docker network connect NETWORK CONTAINER

# Disconnect container from network
docker network disconnect NETWORK CONTAINER

# Remove network
docker network rm NETWORK

# Prune unused networks
docker network prune
```

## 📚 Exercises

### Exercise 1: Bridge Network Isolation

Create isolated environments using bridge networks.

```bash
# Create two isolated networks
docker network create frontend --subnet=172.20.0.0/16
docker network create backend --subnet=172.21.0.0/16

# Run containers in different networks
docker run -d --name web --network frontend nginx
docker run -d --name db --network backend mysql:8

# Test isolation (should fail)
docker exec web ping db
```

### Exercise 2: Multi-Network Container

Connect a container to multiple networks.

```bash
# Create API container connected to both networks
docker run -d --name api --network frontend nginx

# Connect to second network
docker network connect backend api

# Now API can communicate with both networks
docker exec api ping web
docker exec api ping db
```

### Exercise 3: Custom DNS and Aliases

Configure custom DNS resolution.

```bash
# Create network with custom options
docker network create mynet \
  --driver bridge \
  --subnet=172.30.0.0/16 \
  --ip-range=172.30.5.0/24 \
  --gateway=172.30.5.254 \
  --opt com.docker.network.bridge.name=docker1

# Run with network alias
docker run -d --name service1 \
  --network mynet \
  --network-alias primary-service \
  --network-alias backup-service \
  nginx

# Access via alias
docker run --rm --network mynet alpine ping primary-service
```

### Exercise 4: Load Balancing

Implement load balancing with multiple containers.

```bash
# Create network
docker network create lb-network

# Run multiple backend instances
for i in 1 2 3; do
  docker run -d --name backend-$i \
    --network lb-network \
    --network-alias backend \
    nginx
done

# Test DNS round-robin
docker run --rm --network lb-network alpine nslookup backend
```

### Exercise 5: Service Mesh Pattern

Implement service discovery and mesh networking.

## ✅ Verification

Run the verification steps in `setup/verify.md`.

## 🎯 Challenge

Build a complete microservices network with:
1. Frontend network (public)
2. Application network (internal)
3. Database network (restricted)
4. Service discovery
5. Load balancing
6. Network policies

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Container can't reach another | Check network connectivity and DNS |
| Port binding fails | Check for conflicts with netstat/ss |
| DNS resolution fails | Verify network configuration and aliases |
| Overlay network issues | Check Swarm mode and node connectivity |
| Performance issues | Consider host networking for specific services |

## 📊 Network Performance Testing

```bash
# Install iperf3 for network testing
docker run -d --name iperf3-server \
  --network mynet \
  networkstatic/iperf3 -s

# Run client test
docker run --rm --network mynet \
  networkstatic/iperf3 -c iperf3-server

# Test latency
docker run --rm --network mynet \
  alpine ping -c 10 iperf3-server
```

## 🔒 Security Considerations

1. **Network Segmentation**: Isolate services by function
2. **Encryption**: Use overlay networks with encryption for sensitive data
3. **Firewall Rules**: Implement iptables rules for additional security
4. **Network Policies**: Use tools like Calico for Kubernetes-style policies
5. **Monitoring**: Track network traffic and anomalies

## 📚 Additional Resources
- [Docker Network Documentation](https://docs.docker.com/network/)
- [Network Driver Comparison](https://docs.docker.com/network/drivers/)
- [Docker Network Tutorials](https://docs.docker.com/network/tutorials/)

## ⏭️ Next Steps
Congratulations! You've completed the Docker labs. Consider:
- Docker Swarm for orchestration
- Kubernetes for production workloads
- Service mesh implementations (Istio, Linkerd)
- Container security deep dive