"""Les tableaux de bord Grafana doivent être valides et branchés sur Prometheus."""

import json

from tests.conftest import RACINE, charger_tableau, charger_yaml

UID_PROMETHEUS = "prometheus-principal"


def test_les_tableaux_ont_un_titre_un_uid_et_des_panneaux():
    for nom in ("vue-ensemble.json", "application-demo.json"):
        tableau = charger_tableau(nom)
        assert tableau["title"] and tableau["uid"]
        assert len(tableau["panels"]) >= 3
        for panneau in tableau["panels"]:
            assert panneau["title"] and panneau["targets"]
            for cible in panneau["targets"]:
                assert cible["expr"], panneau


def test_les_panneaux_utilisent_la_bonne_source_prometheus():
    for nom in ("vue-ensemble.json", "application-demo.json"):
        tableau = charger_tableau(nom)
        for panneau in tableau["panels"]:
            assert panneau["datasource"]["uid"] == UID_PROMETHEUS, panneau


def test_la_configmap_embarque_les_meme_tableaux_que_les_fichiers():
    configmap = charger_yaml(RACINE / "k8s" / "grafana" / "dashboards-configmap.yaml")[0]
    assert configmap["metadata"]["name"] == "grafana-dashboards"
    for nom_fichier, contenu in configmap["data"].items():
        assert json.loads(contenu) == charger_tableau(nom_fichier)


def test_la_source_de_donnees_pointe_vers_le_service_prometheus():
    for chemin in (
        RACINE / "grafana" / "provisioning" / "datasources" / "prometheus.yml",
        RACINE / "k8s" / "grafana" / "datasource-configmap.yaml",
    ):
        docs = charger_yaml(chemin)
        if docs[0].get("kind") == "ConfigMap":
            import yaml

            source = yaml.safe_load(docs[0]["data"]["prometheus.yml"])
        else:
            source = docs[0]
        datasource = source["datasources"][0]
        assert datasource["uid"] == UID_PROMETHEUS
        assert datasource["url"] == "http://prometheus:9090"
        assert datasource["isDefault"] is True
