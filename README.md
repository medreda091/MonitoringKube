# MonitoringKube

Stack de supervision déployable sur Kubernetes : Prometheus collecte les
métriques, Grafana les affiche dans des tableaux de bord lisibles, et une
petite application de démonstration fournit des métriques à observer. Le
projet sert aussi en local avec Docker Compose, sans cluster.

## Ce que ça supervise

| Indicateur (KPI) | Source | Seuil d'alerte |
|---|---|---|
| Disponibilité des cibles (`up`) | Prometheus | 0 pendant 2 min → critique |
| Taux d'erreur de l'application | Appli de démonstration | > 5 % pendant 5 min |
| Utilisation CPU des noeuds | Node exporter | > 80 % pendant 10 min |
| Mémoire utilisée des noeuds | Node exporter | > 85 % pendant 10 min |
| Débit de requêtes par route | Appli de démonstration | suivi, pas d'alerte |

## Tableaux de bord Grafana

- **Vue d'ensemble** : instances actives, CPU et mémoire des noeuds,
  requêtes par seconde et taux d'erreur de l'application.
- **Application de démonstration** : débit par route, erreurs par route,
  durée de fonctionnement et disponibilité.

## Stack

- Python 3.12 (application de démonstration, bibliothèque standard uniquement)
- Prometheus 2.53, Grafana 11.1, Node exporter 1.8
- Kubernetes (manifestes YAML), Docker, Docker Compose, GitHub Actions

## Lancement local

```bash
docker compose up
```

Puis ouvrir Prometheus sur http://localhost:9090 et Grafana sur
http://localhost:3000 (identifiants par défaut : admin / admin, à changer
à la première connexion). Pour générer du trafic à observer :

```bash
curl http://localhost:8000/
curl http://localhost:8000/erreur   # simule une requête en erreur
curl http://localhost:8000/metrics  # métriques brutes au format Prometheus
```

## Déploiement Kubernetes

```bash
docker build -t demo-app:latest demo-app/
bash scripts/deploy.sh
bash scripts/verifier.sh
```

Puis :

```bash
kubectl port-forward -n supervision svc/prometheus 9090:9090
kubectl port-forward -n supervision svc/grafana 3000:3000
```

La découverte des cibles est automatique : tout pod annoté
`prometheus.io/scrape: "true"` est collecté, et les noeuds sont découverts
via l'API Kubernetes (voir `k8s/prometheus/rbac.yaml`).

## Interprétation des résultats

Quelques lectures utiles quand on regarde les tableaux de bord :

- **Un taux d'erreur qui grimpe sans hausse du trafic** : le problème vient
  de l'application elle-même (bug, dépendance en panne), pas de la charge.
- **CPU ou mémoire qui montent lentement sur plusieurs jours** : piste de
  fuite de ressources, à confirmer en comparant les redémarrages de pods.
- **Une cible `up = 0`** : le service ne répond plus du tout — vérifier
  d'abord que le pod tourne avant de chercher plus loin.
- **Un pic de requêtes suivi d'erreurs** : saturation probable, la piste
  est la capacité (répliques, limites de ressources) plutôt que le code.

## Qualité des données

Les métriques de l'application de démonstration sont émises dans un format
strictement validé par les tests (une ligne par série, labels entre
accolades, valeur numérique). Côté Prometheus, les règles d'enregistrement
(`job:demo_requetes:rate5m`, `job:demo_erreurs:ratio5m`) agrègent les
données brutes avant l'affichage, pour que les tableaux de bord restent
lisibles même quand le nombre de séries augmente.

## Structure du projet

```
k8s/                  Manifestes Kubernetes (namespace supervision)
  prometheus/         ConfigMap, déploiement, service, RBAC
  grafana/            Déploiement, service, provisioning, tableaux de bord
  node-exporter/      DaemonSet sur chaque noeud
  demo-app/           Déploiement et service de l'application de démonstration
prometheus/           Configuration locale et règles d'alerte
grafana/
  dashboards/         Tableaux de bord (JSON, source de vérité)
  provisioning/       Source de données et fournisseur de tableaux de bord
demo-app/             Application Python sans dépendance (port 8000)
scripts/              Déploiement, vérification, génération de la ConfigMap
tests/                Validation des manifestes, règles et tableaux de bord
```

## Tests

```bash
pip install pytest pyyaml
python3 -m pytest tests/ -q
```

Les tests valident les manifestes YAML, la configuration Prometheus, les
règles d'alerte, les tableaux de bord Grafana et la cohérence de
l'ensemble : sélecteurs de services, ConfigMaps référencées, source de
données Grafana, format des métriques de l'application de démonstration,
et identité entre les règles locales et celles embarquées dans Kubernetes.

## Améliorations possibles

- Persistance des données Prometheus avec un volume persistant (PVC) au
  lieu du répertoire temporaire actuel.
- Alertmanager pour router les alertes vers un canal de notification.
- Authentification Grafana adossée à un fournisseur d'identité.
