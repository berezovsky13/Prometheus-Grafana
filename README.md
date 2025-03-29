# Kubernetes HPA Demo with Prometheus and Grafana

This project demonstrates Horizontal Pod Autoscaling (HPA) in Kubernetes with Prometheus and Grafana monitoring.

## Prerequisites

- Kubernetes cluster
- Helm
- kubectl
- Docker

## Project Structure

```
.
├── app.py                 # Flask application with metrics
├── complex-hpa.yaml       # Kubernetes HPA configuration
├── prometheus-minimal.yaml # Prometheus Helm values
└── Dockerfile            # Container image definition
```

## Setup Instructions

### 1. Create Monitoring Namespace

First, ensure the monitoring namespace is properly created and not in a terminating state:

```bash
# Delete the namespace if it exists and is stuck
kubectl delete namespace monitoring --force

# Create a new namespace
kubectl create namespace monitoring
```

### 2. Install Prometheus and Grafana

```bash
# Add Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  -f prometheus-minimal.yaml
```

### 3. Build and Deploy the Application

```bash
# Build the Docker image
docker build -t berezovsky8/hpa-app:latest .

# Push the image to Docker Hub
docker push berezovsky8/hpa-app:latest

# Apply Kubernetes configuration
kubectl apply -f complex-hpa.yaml
```

### 4. Access the Application

Get the service URL:
```bash
kubectl get svc complex-app-service
```

Access the application using either:
```bash
# Using localhost
curl http://localhost:31418/

# Using node IP
curl http://<your-node-ip>:<node-port>/
```

### 5. Generate Load

You can generate load using either of these commands:
```bash
# Using localhost
curl http://localhost:31418/load/http

# Using node IP
curl http://<your-node-ip>:<node-port>/load/http
```

### 6. Monitor HPA

Watch the HPA scaling:
```bash
kubectl get hpa -w
```

### 7. Access Grafana and Prometheus Dashboards

#### Access Grafana:

1. Get the Grafana admin password:
```bash
kubectl --namespace monitoring get secrets prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 -d ; echo
```

2. Port-forward Grafana:
```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

3. Access Grafana:
- Open http://localhost:3000 in your browser
- Username: admin
- Password: (from step 1)

#### Access Prometheus:

1. Port-forward Prometheus:
```bash
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
```

2. Access Prometheus:
- Open http://localhost:9090 in your browser (NOT the node IP)
- No login required
- Keep the port-forward command running in a separate terminal

Note: You must use localhost (127.0.0.1) to access Prometheus, not the node IP. The port-forward command creates a tunnel from your local machine to the Prometheus service inside the cluster.

#### Verify Prometheus is collecting metrics:

1. Check Prometheus targets:
- Go to http://localhost:9090/targets
- Look for targets with "UP" status

2. Query metrics:
- Go to http://localhost:9090/graph
- Try these example queries:
  - `http_requests_total`
  - `cpu_usage`
  - `memory_usage`
  - `queue_size`

#### Import Grafana Dashboard:

1. In Grafana (http://localhost:3000):
- Click "+" in the left sidebar
- Select "Import"
- Enter dashboard ID: 1860 (Node Exporter Full)
- Click "Load"
- Select your Prometheus data source
- Click "Import"

2. Create a custom dashboard for HPA metrics:
- Click "+" in the left sidebar
- Select "New Dashboard"
- Add panels for:
  - CPU Usage
  - Memory Usage
  - HTTP Requests
  - Queue Size
  - Number of Pods

## Application Features

- Flask web application with Prometheus metrics
- CPU and memory usage monitoring
- Request queue management
- Automatic garbage collection
- Health check endpoint
- Metrics endpoint for Prometheus

## HPA Configuration

The HPA is configured to scale based on:
- CPU utilization (target: 20%)
- Memory utilization (target: 30%)
- HTTP requests per second (target: 1)

Scaling behavior:
- Scale up: Aggressive (400% every 3s or 8 pods every 5s)
- Scale down: Very aggressive (100% every 1s or 8 pods every 1s)
- No stabilization window for scale down

## Troubleshooting

1. If the monitoring namespace is stuck:
```bash
kubectl delete namespace monitoring --force
kubectl create namespace monitoring
```

2. Check pod status:
```bash
kubectl get pods
```

3. View pod logs:
```bash
kubectl logs <pod-name>
```

4. Check HPA status:
```bash
kubectl get hpa
kubectl describe hpa complex-hpa
```

5. View metrics:
```bash
curl http://localhost:31418/metrics
```

## Notes

- The application uses a maximum queue size of 100 requests
- Requests are dropped with 503 status when queue is full
- Garbage collection is performed after processing each request
- Metrics are updated on each request
- The application exposes Prometheus metrics on port 8000 