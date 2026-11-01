#!/bin/bash
# Déploie toute la stack de supervision dans le namespace "supervision".
# Prérequis : un cluster Kubernetes accessible via kubectl (minikube, kind...),
# et l'image demo-app construite (docker build -t demo-app:latest demo-app/).
set -e
cd "$(dirname "$0")/.."

echo "Génération de la ConfigMap des tableaux de bord..."
python3 scripts/generer_configmap.py

echo "Application des manifestes..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/prometheus/
kubectl apply -f k8s/grafana/
kubectl apply -f k8s/node-exporter/
kubectl apply -f k8s/demo-app/

echo "Stack déployée. Vérifiez avec : bash scripts/verifier.sh"
