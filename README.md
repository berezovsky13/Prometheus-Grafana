# Kubernetes HPA Examples with Monitoring

This repository contains examples of Horizontal Pod Autoscaling (HPA) in Kubernetes, from simple to complex scenarios, along with monitoring setup using Prometheus and Grafana.

## Prerequisites

- Kubernetes cluster (k3s, minikube, or any other)
- kubectl configured to work with your cluster
- Docker (for building the application image)
- Helm (for installing Prometheus)

## Step 1: Simple HPA Example

This example demonstrates basic CPU-based autoscaling.

1. Apply the simple HPA configuration:
```bash
kubectl apply -f simple-hpa.yaml
```

2. Verify the deployment and HPA:
```bash
kubectl get pods
kubectl get hpa
```

3. Generate CPU load to trigger scaling:
```bash
# Get the pod name
kubectl get pods

# Generate CPU load
kubectl exec -it <pod-name> -- sh -c 'while true; do :; done'
```

4. Monitor the scaling:
```bash
# Watch HPA status
kubectl get hpa -w

# Watch pods
kubectl get pods -w
```

## Step 2: Complex HPA Example

This example demonstrates multi-metric autoscaling with a custom application.

1. Build the application image:
```bash
# Build the Docker image
docker build -t your-registry/complex-app:latest .

# Push to your registry
docker push your-registry/complex-app:latest
```

2. Update the image in complex-hpa.yaml:
```yaml
# Replace this line with your image
image: your-registry/complex-app:latest
```

3. Apply the complex HPA configuration:
```bash
kubectl apply -f complex-hpa.yaml
```

4. Get the NodePort service URL:
```bash
kubectl get svc complex-app-service
```

5. Test different types of load:

CPU Load:
```bash
curl http://<node-ip>:<node-port>/load/cpu
```

Memory Load:
```bash
curl http://<node-ip>:<node-port>/load/memory
```

HTTP Request Load:
```bash
for i in {1..20}; do curl http://<node-ip>:<node-port>/load/http; done
```

6. Monitor the scaling:
```bash
# Watch HPA status
kubectl get hpa -w

# Watch pods
kubectl get pods -w
```

## Step 3: Monitoring Setup with Prometheus and Grafana

1. Add the Prometheus Helm repository:
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

2. Install Prometheus with minimal configuration:
```bash
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  -f prometheus-minimal.yaml
```

3. Port-forward Grafana:
```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

4. Access Grafana:
- URL: http://localhost:3000
- Username: admin
- Password: admin

5. Import the dashboard:
- Go to Dashboards > Import
- Copy and paste the contents of `grafana-dashboard.json`
- Click Import

## Monitoring Features

The setup provides:
- CPU usage monitoring
- Memory usage monitoring
- HTTP request rate monitoring
- Automatic scaling based on multiple metrics
- Visual thresholds for scaling triggers

## Cleanup

To remove everything:

1. Remove the applications:
```bash
kubectl delete -f complex-hpa.yaml
kubectl delete -f simple-hpa.yaml
```

2. Remove Prometheus:
```bash
helm uninstall prometheus -n monitoring
kubectl delete namespace monitoring
```

## Troubleshooting

1. Check if metrics-server is installed:
```bash
kubectl get deployment metrics-server -n kube-system
```

2. Check HPA status:
```bash
kubectl describe hpa
```

3. Check Prometheus targets:
```bash
kubectl port-forward -n monitoring svc/prometheus-server 9090:9090
# Then visit http://localhost:9090/targets
```

## Notes

- The simple HPA scales based on CPU utilization
- The complex HPA scales based on CPU, memory, and HTTP requests
- Prometheus collects metrics every 15 seconds
- Grafana dashboard refreshes every 5 seconds
- HPA has stabilization windows to prevent thrashing 