# MonitoringKube

Stack de supervision déployable sur Kubernetes : Prometheus collecte les
métriques, Grafana les affiche dans des tableaux de bord, et une petite
application de démonstration fournit des métriques à observer.

## Ce que le projet contient

- **Prometheus** : collecte des métriques des pods (découverte automatique),
  des noeuds et de l'application de démonstration, avec des règles
  d'enregistrement et des alertes.
- **Grafana** : deux tableaux de bord provisionnés automatiquement.
- **Node exporter** : métriques système de chaque noeud (CPU, mémoire...).
- **Application de démonstration** : serveur Python sans dépendance qui
  expose un endpoint `/metrics` au format Prometheus.

## Lancement local

```bash
docker compose up
```

Puis ouvrir Prometheus sur http://localhost:9090 et Grafana sur
http://localhost:3000 (identifiants par défaut : admin / admin, à changer
à la première connexion).

## Déploiement Kubernetes

```bash
docker build -t demo-app:latest demo-app/
bash scripts/deploy.sh
bash scripts/verifier.sh
```

## Tests

```bash
pip install pytest pyyaml
python3 -m pytest tests/ -q
```

Les tests valident les manifestes YAML, la configuration Prometheus, les
règles d'alerte, les tableaux de bord Grafana et la cohérence de
l'ensemble (sélecteurs, ConfigMaps référencées, source de données).
