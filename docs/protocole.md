### Protocole de Communication en trois partie ###
• client ➔ serveur
• administrateur ➔ serveur
• serveur ➔ serveur maitre

# Schéma de fonctionnement :

                            +-------------------+
							|     Serveur       |
+--------+----------+		|  +------------+   |         +-------------------+
|  Administrateur   |-------|  |Dictionnaire|   |---------|      Client       |
+--------+----------+		|  +------------+   |         +-------------------+
							+--------+----------+
  									 |
 									 |  //Les dicos serveur - serveur maître sont synchro
 									 |
							+-------------------+
							|  Serveur Maître   |
							|  +-------------+  |
				            |  | Dictionnaire|  |
							|  +-------------+  |
							+--------+----------+
                

# Format global :
	- Les echanges entre les differentes machines (client/serveur/admin/serveur maitre) utilisent une connexion TCP.
	- Les messages sont encodés en UTF-8.
	- Un message correspond à une ligne de texte terminée par \n.
	- Chaque commande envoyée fait = une ligne / Chaque réponse fait = une ou plusieurs lignes.
	- Les dictionnaires sont stockés au format JSON, mais les communications sont en texte.


# Protocole de communication (client ➔ serveur)
	Le client permet à un utilisateur de consulter un dictionnaire.

	-Format utilisation des commandes :
	    "GET <clé>"          ex : GET février
	    "PREF <prefixe>"     ex : PREF j

	-Réponses du serveur :
		• Pour GET :
		    →Si la clé existe, le serveur renvoie une ligne contenant uniquement la valeur de la clé.
		    →Si la clé n'existe pas, le serveur renvoie "Key not found".

		• Pour PREF :
		    →Si au moins une clé correspond au préfixe, le serveur renvoie une ligne par paire trouvée : "<clé>: <valeur>"
		    →S'il n'y a aucun résultat, le serveur renvoie : "Key not found"

	-Si le serveur reçoit une commande qu'il ne connaît pas, il renvoie : "Unknown command".

	-Exemple d'utilisation des commandes GET et PREF :
		→Initialison un dictionnaire suivant :
		{
		    "janvier" : 31,
	    	"février" : 28,
	    	"mars" : 31
		}

		• Exemple pour GET :

			Client ➔ serveur : GET février\n     (clé présente)
			Serveur ➔ client : 28\n

			Client ➔ serveur : GET juillet\n     (clé non présente)
			Serveur ➔ client : Key not found\n
	 	
		• Exemple pour PREF :
		
			Client ➔ serveur : PREF j\n         (prefixe présent)
			Serveur ➔ client : janvier: 31\n

			Client ➔ serveur : PREF z\n         (prefixe non présent)
			Serveur ➔ client : Key not found\n

	-Gestion de la connexion :
		Une connexion client sert a envoyer une seule commande. Le serveur envoie sa réponse puis coupe immédiatement la connexion.	


# Protocole de communication (administrateur ➔ serveur)
	Le rôle administrateur permet d'ajouter, supprimer ou modifier dans le dictionnaire.
	Contrairement aux clients simple, il reste connecté et doit s'authentifier.
	Il utilise également des lignes de texte.

	-Authentification :
	Le mot de passe n'est pas envoyé en clair, le client envoie un hash SHA-256, le serveur compare ce hash avec
	celui stocké dans "admins.json" qui stock les admins et leur hash.

		L'administrateur s'authentifie avec la commande :
	    	"ADMIN <login> <motdepasse>"
		→En cas de succès, le server renvoie :
	    	"AUTH SUCCESSFUL"
			(On affiche dans la console "LOGGED AS ADMINISTRATOR")
		→En cas d'echec le server renvoie :
	    	"AUTH FAILED"
			(On affiche dans la console "LOGIN OR PASSWORD INCORRECT")


	-L'administrateur possède plusieurs commandes :

	    • "SET <cle> <valeur>" :
	    	Cela ajoute une nouvelle entrée ou modifie la valeur associée a une clé.
			Cette modification met à jour le dictionnaire du server et du server maître.
	    →Réponse :
			"UPDATE SUCCESSFUL"


	    • "DEL <cle>" :
	    	Supprime une entrée, si la clé existe.
			Cette modification met à jour le dictionnaire du server et du server maître.
		→Réponse :
			"DELETION SUCCESSFUL"
		→Si pas de <cle> trouvé, renvoie:
			"Key not found"


		• "ADD_ADMIN <new_login> <new_password> :
			Permet d'ajouter un nouvel administrateur au serveur.
			Le serveur stockera le nouveau mot de passe sous forme chiffrée dans "admins.json".
		→Réponse :
			"Admin <login> added !"
		→Si le login existe déjà:
			"Login <login> already used"


	    • "EXIT":
	    	Termine la session administrateur.
	    →Réponse :
			"ADMIN SESSION CLOSED"

	-Gestion de la connexion :
		Contrairement au client, l'administrateur reste connecté après une commande. La connexion ne se ferme que lorsque qu'il utilise EXIT.

# Protocole de communication (serveur ➔ serveur maître)
	Le serveur maître possède le dictionnaire de référence.
	Le serveur joue le role de client vis a vis du serveur maître.
	Quand la clé n'est pas trouvée localement, le serveur interroge le serveur maître.
	La communication serveur-serveur maître réutilise exactement les mêmes commandes textes que pour un client simple.

	-Lorsqu'un client envoie une commande GET <cle> au serveur :
		•Le serveur cherche la clé dans son dicoctionnaire local.

	    	→Si la clé existe :
				Il renvoie la valeur au client.

	    	→Si la clé n'existe pas :
				Il ouvre une connexion TCP vers le serveur maitre et lui envoie la commande, par ex : GET <cle>
				Il lit la réponse "<valeur>" ou "Key not found", puis renvoie la valeur au client.
			
			→Si le serveur maître renvoie une valeur valide :
				Le serveur l'ajoute a son dictionnaire local, puis renvoie la valeur au client.

			→Si le serveur maître renvoie "Key not found" :
				Il renvoie uniquement "Key not found" au client.

	- Synchronisation des dictionnaires serveur-serveur maître :
		Quand un administrateur effectue un SET, DEL ou ADD_ADMIN sur le serveur, le serveur ouvre une connexion TCP vers le serveur maitre.

		→ Il s'authentifie en réutilisant le login et le mot de passe de l'admin.
			"ADMIN <login> <password>"

		→Si le serveur maitre repond "AUTH SUCCESSFUL", le serveur envoie la commande au serveur maitre :
			"SET <cle> <valeur>" ou "DEL <cle>"
			Le serveur maitre met a jour son dictionnaire.