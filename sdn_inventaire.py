"""Inventaire d'un réseau via l'API REST d'un contrôleur SDN Cisco Packet Tracer.

Usage :
    python sdn_inventaire.py --controleur http://192.168.101.254 --utilisateur cisco
"""

import argparse
import getpass
import sys

import requests


def obtenir_jeton(controleur, utilisateur, mot_de_passe):
    """Demande un jeton d'authentification (serviceTicket) au contrôleur."""
    reponse = requests.post(
        f"{controleur}/api/v1/ticket",
        json={"username": utilisateur, "password": mot_de_passe},
        timeout=10,
    )
    reponse.raise_for_status()
    return reponse.json()["response"]["serviceTicket"]


def interroger(controleur, jeton, ressource):
    """Envoie une requête GET authentifiée et renvoie la liste de résultats."""
    reponse = requests.get(
        f"{controleur}/api/v1/{ressource}",
        headers={"X-Auth-Token": jeton},
        timeout=10,
    )
    reponse.raise_for_status()
    return reponse.json()["response"]


def main():
    parser = argparse.ArgumentParser(description="Inventaire réseau via un contrôleur SDN")
    parser.add_argument("--controleur", default="http://192.168.101.254",
                        help="adresse du contrôleur (défaut : %(default)s)")
    parser.add_argument("--utilisateur", required=True, help="identifiant du contrôleur")
    args = parser.parse_args()

    # Le mot de passe est demandé sans être affiché ni écrit dans le script
    mot_de_passe = getpass.getpass("Mot de passe : ")

    try:
        jeton = obtenir_jeton(args.controleur, args.utilisateur, mot_de_passe)

        print("\nÉquipements réseau")
        print(f"{'Nom':<20}{'Modèle':<20}{'Adresse de gestion'}")
        for equipement in interroger(args.controleur, jeton, "network-device"):
            print(f"{equipement['hostname']:<20}{equipement['platformId']:<20}"
                  f"{equipement['managementIpAddress']}")

        print("\nHôtes")
        print(f"{'Nom':<20}{'Adresse IP':<20}{'Adresse MAC'}")
        for hote in interroger(args.controleur, jeton, "host"):
            print(f"{hote['hostName']:<20}{hote['hostIp']:<20}{hote['hostMac']}")

    except requests.RequestException as erreur:
        sys.exit(f"Erreur de communication avec le contrôleur : {erreur}")


if __name__ == "__main__":
    main()
