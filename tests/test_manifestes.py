"""Chaque manifeste Kubernetes doit être valide et complet."""

from tests.conftest import RACINE, charger_yaml, tous_les_manifestes

NAMESPACE_ATTENDU = "supervision"


def test_tous_les_yaml_se_chargent():
    manifestes = tous_les_manifestes()
    assert len(manifestes) >= 10  # namespace, prometheus, grafana, exporter, demo
    for chemin, doc in manifestes:
        assert doc.get("apiVersion"), f"apiVersion manquant dans {chemin}"
        assert doc.get("kind"), f"kind manquant dans {chemin}"
        assert doc.get("metadata", {}).get("name"), f"name manquant dans {chemin}"


def test_tout_est_dans_le_namespace_supervision():
    for chemin, doc in tous_les_manifestes():
        if doc["kind"] in ("ClusterRole", "ClusterRoleBinding", "Namespace"):
            continue  # ressources de cluster, sans namespace
        assert doc["metadata"].get("namespace") == NAMESPACE_ATTENDU, chemin


def test_les_deploiements_ont_des_ressources():
    for chemin, doc in tous_les_manifestes():
        if doc["kind"] not in ("Deployment", "DaemonSet"):
            continue
        conteneurs = doc["spec"]["template"]["spec"]["containers"]
        assert conteneurs, chemin
        for conteneur in conteneurs:
            assert conteneur.get("image"), f"image manquante dans {chemin}"
            ressources = conteneur.get("resources", {})
            assert ressources.get("limits"), f"limites absentes dans {chemin}"
            assert ressources.get("requests"), f"requests absents dans {chemin}"


def test_les_services_ciblent_un_deploiement_existant():
    selections = {}
    for _, doc in tous_les_manifestes():
        if doc["kind"] in ("Deployment", "DaemonSet"):
            selections[doc["metadata"]["name"]] = doc["spec"]["template"]["metadata"]["labels"]
    for chemin, doc in tous_les_manifestes():
        if doc["kind"] != "Service":
            continue
        selecteur = doc["spec"]["selector"]
        assert any(
            all(labels.get(cle) == valeur for cle, valeur in selecteur.items())
            for labels in selections.values()
        ), f"aucun déploiement ne correspond au service {chemin}"
