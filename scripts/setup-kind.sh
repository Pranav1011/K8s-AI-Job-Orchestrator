#!/bin/bash
set -e

echo "🔧 Creating Kind cluster..."
# Ensure kind is installed
if ! command -v kind &> /dev/null; then
    echo "Kind is not installed. Please install it first."
    exit 1
fi

kind create cluster --name ai-scheduler

echo "📦 Installing CRDs..."
kubectl apply -f controller/config/crd/bases/

echo "🔐 Creating secrets..."
kubectl create secret generic db-credentials \
    --from-literal=username=aijobs \
    --from-literal=password=aijobs \
    --dry-run=client -o yaml | kubectl apply -f -

# Install Prometheus Operator via Helm if Helm is present
if command -v helm &> /dev/null; then
  echo "📊 Installing Prometheus Operator..."
  helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
  helm repo update
  helm install prometheus prometheus-community/kube-prometheus-stack \
      --namespace monitoring --create-namespace --wait
else
  echo "Helm not found, skipping Prometheus installation."
fi

echo "✅ Cluster ready!"
kubectl get nodes
