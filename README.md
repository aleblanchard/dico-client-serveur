# Dico — dictionnaire clé/valeur client-serveur en Python

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Sockets TCP](https://img.shields.io/badge/R%C3%A9seau-TCP-informational)

Projet universitaire de **réseau** (Université de Bordeaux) : un service de dictionnaire distribué qui communique en TCP avec un protocole texte maison.
Un **client** interroge un **serveur**, qui délègue au **serveur maître** les clés qu'il ne connaît pas. Un **administrateur** authentifié peut modifier les données, et les changements sont synchronisés avec le maître.

```
 Client ──GET/PREF──▶ Serveur ──(clé inconnue)──▶ Serveur maître
                         ▲                              ▲
 Admin ──SET/DEL/ADD_ADMIN┘───── synchronisation ───────┘
```

## Fonctionnalités

- `GET <clé>` et `PREF <préfixe>` côté client (une commande par connexion)
- Repli automatique sur le serveur maître, avec mise en cache locale de la valeur
- Session administrateur persistante : `SET`, `DEL`, `ADD_ADMIN`, `EXIT`
- Mot de passe jamais envoyé en clair : le client transmet un hash SHA-256
- Serveur mono-thread multi-clients grâce à `select`
- Dictionnaires stockés en JSON (UTF-8, accents gérés)

## Structure

```
.
├── dico_server.py      # serveur (et serveur maître)
├── dico_client.py      # client en ligne de commande
├── dico_admin.py       # client administrateur interactif
├── dico_local.py       # manipulation d'un dictionnaire JSON en local
├── data/               # dictionnaires d'exemple + comptes admin
├── docs/
│   ├── protocole.md    # spécification complète du protocole
│   └── securite.pdf    # analyse de sécurité
└── tests/
    └── test_server_client.sh
```

## Prérequis

Python 3.8 ou plus, aucune dépendance externe.

## Utilisation

```bash
# 1. Serveur maître (port 8888)
python3 dico_server.py 8888 data/mois_duree_maitre.json

# 2. Serveur relié au maître (port 7777)
python3 dico_server.py 7777 data/mois_duree.json localhost 8888

# 3. Client
python3 dico_client.py localhost 7777 GET janvier     # -> 31
python3 dico_client.py localhost 7777 PREF j          # -> juin: 30, juillet: 31, janvier: 31

# 4. Administrateur
python3 dico_admin.py localhost 7777
```

Compte administrateur de démonstration : `admin` / `1234` (défini dans `data/admins.json`, à changer pour tout usage réel).

## Tests

Le script lance un serveur maître et un serveur, puis exécute les scénarios client et administrateur en affichant le résultat attendu à côté du résultat obtenu :

```bash
cd tests && ./test_server_client.sh
```

> Le script modifie les fichiers de `data/` : `git checkout data/` les remet dans leur état d'origine.

## Protocole

La spécification complète (format des messages, réponses, synchronisation serveur ↔ maître) est dans [`docs/protocole.md`](docs/protocole.md).

## Limites connues

- Le hash SHA-256 non salé protège seulement contre la lecture du mot de passe en clair, pas contre le rejeu ni le cassage par dictionnaire : la communication n'est pas chiffrée (pas de TLS).
- Projet pédagogique : non prévu pour un usage en production.

## Auteurs

Projet réalisé en binôme à l'Université de Bordeaux :

- **Alexis Blanchard**
- **Félix Claus**
