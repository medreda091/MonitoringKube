"""Génère la ConfigMap Kubernetes qui embarque les tableaux de bord Grafana.

Usage : python3 scripts/generer_configmap.py
Le fichier k8s/grafana/dashboards-configmap.yaml est régénéré à partir du
contenu de grafana/dashboards/*.json, pour que les deux restent identiques.
"""

import json
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_TABLEAUX = RACINE / "grafana" / "dashboards"
SORTIE = RACINE / "k8s" / "grafana" / "dashboards-configmap.yaml"


def generer():
    fichiers = sorted(DOSSIER_TABLEAUX.glob("*.json"))
    if not fichiers:
        raise SystemExit("Aucun tableau de bord trouvé dans grafana/dashboards/.")
    lignes = [
        "# Fichier généré par scripts/generer_configmap.py, ne pas modifier à la main.",
        "# Il embarque les tableaux de bord de grafana/dashboards/ pour Kubernetes.",
        "apiVersion: v1",
        "kind: ConfigMap",
        "metadata:",
        "  name: grafana-dashboards",
        "  namespace: supervision",
        "data:",
    ]
    for fichier in fichiers:
        contenu = fichier.read_text(encoding="utf-8")
        json.loads(contenu)  # vérifie que le JSON est valide avant de l'embarquer
        lignes.append(f"  {fichier.name}: |")
        lignes.extend("    " + ligne for ligne in contenu.splitlines())
    SORTIE.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print(f"ConfigMap générée : {SORTIE} ({len(fichiers)} tableaux de bord).")


if __name__ == "__main__":
    generer()
