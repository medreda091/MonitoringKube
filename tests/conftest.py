"""Utilitaires partagés : chargement des manifestes YAML et des tableaux de bord."""

import json
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parent.parent


def charger_yaml(chemin):
    """Charge tous les documents d'un fichier YAML (séparés par ---)."""
    with open(chemin, encoding="utf-8") as fichier:
        return [doc for doc in yaml.safe_load_all(fichier) if doc]


def tous_les_manifestes():
    """Tous les manifestes YAML du dossier k8s/, avec leur chemin."""
    resultat = []
    for chemin in sorted((RACINE / "k8s").rglob("*.yaml")):
        for doc in charger_yaml(chemin):
            resultat.append((chemin, doc))
    return resultat


def charger_tableau(nom):
    with open(RACINE / "grafana" / "dashboards" / nom, encoding="utf-8") as fichier:
        return json.load(fichier)
