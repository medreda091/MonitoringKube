"""Petite application de démonstration qui expose ses propres métriques.

Elle sert une page d'accueil, une route qui simule parfois une erreur, et
un endpoint /metrics au format Prometheus. Aucune dépendance externe :
uniquement la bibliothèque standard, pour que l'image reste légère.
"""

import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DEPART = time.time()
# Compteurs en mémoire : requêtes servies et requêtes en erreur, par route.
requetes = {}
erreurs = {}


def render_metrics():
    """Rend les métriques au format d'exposition Prometheus."""
    lignes = [
        "# HELP demo_requetes_total Nombre total de requetes recues, par route.",
        "# TYPE demo_requetes_total counter",
    ]
    for route in sorted(requetes):
        lignes.append(f'demo_requetes_total{{route="{route}"}} {requetes[route]}')
    lignes.append("# HELP demo_erreurs_total Nombre total de requetes en erreur, par route.")
    lignes.append("# TYPE demo_erreurs_total counter")
    for route in sorted(erreurs):
        lignes.append(f'demo_erreurs_total{{route="{route}"}} {erreurs[route]}')
    lignes.append("# HELP demo_duree_secondes Duree de fonctionnement en secondes.")
    lignes.append("# TYPE demo_duree_secondes gauge")
    lignes.append(f"demo_duree_secondes {int(time.time() - DEPART)}")
    return "\n".join(lignes) + "\n"


class Handler(BaseHTTPRequestHandler):
    """Gère les trois routes de l'application de démonstration."""

    def _repondre(self, code, corps, type_contenu="text/plain; charset=utf-8"):
        contenu = corps.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", type_contenu)
        self.send_header("Content-Length", str(len(contenu)))
        self.end_headers()
        self.wfile.write(contenu)

    def do_GET(self):  # noqa: N802 (nom imposé par http.server)
        if self.path == "/metrics":
            self._repondre(200, render_metrics())
            return
        if self.path == "/erreur":
            erreurs["/erreur"] = erreurs.get("/erreur", 0) + 1
            requetes["/erreur"] = requetes.get("/erreur", 0) + 1
            self._repondre(500, "Erreur simulee pour la supervision.\n")
            return
        requetes["/"] = requetes.get("/", 0) + 1
        self._repondre(200, "Application de demonstration MonitoringKube.\n")

    def log_message(self, *args):
        # Silence volontaire : les logs ne polluent pas la sortie du conteneur.
        pass


if __name__ == "__main__":
    serveur = ThreadingHTTPServer(("0.0.0.0", 8000), Handler)
    print("Application de demonstration sur le port 8000.")
    serveur.serve_forever()
