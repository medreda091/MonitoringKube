"""La configuration Prometheus et ses règles d'alerte doivent être cohérentes."""

import yaml

from tests.conftest import RACINE, charger_yaml


def _regles(chemin):
    with open(chemin, encoding="utf-8") as fichier:
        return yaml.safe_load(fichier)["groups"]


def test_configuration_locale():
    with open(RACINE / "prometheus" / "prometheus.yml", encoding="utf-8") as fichier:
        config = yaml.safe_load(fichier)
    assert config["global"]["scrape_interval"] == "15s"
    jobs = [job["job_name"] for job in config["scrape_configs"]]
    assert "prometheus" in jobs and "demo-app" in jobs
    assert config["rule_files"] == ["rules.yml"]


def test_regles_locales_et_kubernetes_identiques():
    locales = _regles(RACINE / "prometheus" / "rules.yml")
    configmap = charger_yaml(RACINE / "k8s" / "prometheus" / "configmap.yaml")[0]
    embarquees = yaml.safe_load(configmap["data"]["rules.yml"])["groups"]
    assert locales == embarquees


def test_chaque_alerte_a_un_seuil_une_duree_et_un_resume():
    for chemin in (RACINE / "prometheus" / "rules.yml",):
        for groupe in _regles(chemin):
            for regle in groupe["rules"]:
                if "alert" not in regle:
                    continue
                assert regle["expr"], regle
                assert regle["for"], regle
                assert regle["labels"]["severity"] in ("critique", "avertissement")
                assert regle["annotations"]["summary"], regle


def test_les_alertes_attendues_existent():
    alertes = [
        regle["alert"]
        for groupe in _regles(RACINE / "prometheus" / "rules.yml")
        for regle in groupe["rules"]
        if "alert" in regle
    ]
    for attendue in ("InstanceIndisponible", "TauxErreurEleve", "MemoireElevee", "CpuEleve"):
        assert attendue in alertes


def test_la_decouverte_kubernetes_est_active():
    configmap = charger_yaml(RACINE / "k8s" / "prometheus" / "configmap.yaml")[0]
    config = yaml.safe_load(configmap["data"]["prometheus.yml"])
    roles = [
        sd["kubernetes_sd_configs"][0]["role"]
        for job in config["scrape_configs"]
        if "kubernetes_sd_configs" in job
        for sd in [job]
    ]
    assert "pod" in roles and "node" in roles
