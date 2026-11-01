#!/bin/bash
# Affiche l'état de la stack de supervision dans le namespace "supervision".
kubectl get pods,svc -n supervision
echo "---"
echo "Prometheus : kubectl port-forward -n supervision svc/prometheus 9090:9090"
echo "Grafana    : kubectl port-forward -n supervision svc/grafana 3000:3000"
echo "(Identifiants Grafana par défaut : admin / admin, à changer à la première connexion.)"
