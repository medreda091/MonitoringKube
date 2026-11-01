"""Cohérence globale : références entre manifestes, compose et appli démo."""

import importlib.util
import re
import sys

import yaml

from tests.conftest import RACINE, charger_yaml, tous_les_manifestes

FORMAT_METRIQUE = re.compile(r"^[a-z_]+(\{[a-z_]+=\"[^\"]+\"\})? [0-9]+$", re.MULTILINE)


def test_les_configmaps_referencees_existent():
    configmaps = {
        doc["metadata"]["name"]
        for _, doc in tous_les_manifestes()
        if doc["kind"] == "ConfigMap"
    }
    for chemin, doc in tous_les_manifestes():
        if doc["kind"] not in ("Deployment", "DaemonSet"):
            continue
        for volume in doc["spec"]["template"]["spec"].get("volumes", []):
            if "configMap" in volume:
                assert volume["configMap"]["name"] in configmaps, (chemin, volume)


def test_le_compose_reference_des_fichiers_existants():
    with open(RACINE / "docker-compose.yml", encoding="utf-8") as fichier:
        compose = yaml.safe_load(fichier)
    assert {"prometheus", "grafana", "demo-app"} <= set(compose["services"])
    for service in compose["services"].values():
        for volume in service.get("volumes", []):
            hote = volume.split(":")[0]
            assert (RACINE / hote).exists(), volume


def test_les_metriques_de_la_demo_sont_au_format_prometheus():
    spec = importlib.util.spec_from_file_location("app_demo", RACINE / "demo-app" / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.requetes["/"] = 7
    module.erreurs["/erreur"] = 2
    sortie = module.render_metrics()
    assert "demo_requetes_total{route=\"/\"} 7" in sortie
    assert "demo_erreurs_total{route=\"/erreur\"} 2" in sortie
    assert "demo_duree_secondes" in sortie
    for ligne in sortie.splitlines():
        if ligne.startswith("#") or not ligne.strip():
            continue
        assert FORMAT_METRIQUE.match(ligne), ligne
