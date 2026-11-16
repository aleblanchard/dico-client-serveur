#!/usr/bin/env python3
import socket
import sys
import json 
import os
import hashlib
import select


ADMIN_LIST = "data/admins.json"

def load_dico(dico_file: str):
    if not os.path.exists(dico_file):
        return {}
    try:
        with open(dico_file, "r", encoding="utf-8") as f :      #fichier ouvert en lecture puis encodé en utf 8
            data = json.load(f)                                 #lit et decode le fichier json
        if isinstance(data, dict):                              #on verifie que ce qu'on a lu est bien un dict
            return data
        else:                                                   #sinon on retourne un dict vide
           return {}

    except Exception:
        return {}

def add_dico(dico_file : str, dico) :
    try :
        with open(dico_file, 'w', encoding='utf-8') as f :
            json.dump(dico,f, indent=4, ensure_ascii=False)     #indent pour les espaces, ensure_ascii pour les accents
    except Exception as e:
        print("erreur ajout\n",e)


def noyeux_joel():
    print("")
    print("       * ")
    print("      / \\      ")
    print("     /   \\     ")
    print("    /     \\    ")
    print("   /       \\   ")
    print("  /         \\  ")
    print(" /___________\\ ")
    print("      |||       ")

def search_on_maitre(serv_maitre_host, serv_maitre_port, cmd, arg): #permet de chercher si on a pas la réponse sur le serveur on cherche sur le serv maitre
    if serv_maitre_host and serv_maitre_port:
        try:
            serv_maitre = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serv_maitre.connect((serv_maitre_host, serv_maitre_port))
            request = cmd +" "+ arg+"\n"
            serv_maitre.sendall(request.encode('utf-8'))
            result = ""
            while True:
                data = serv_maitre.recv(1024)
                if len(data) == 0:
                    break
                result += data.decode('utf-8').strip()
            serv_maitre.close()
            if result:
                return result+"\n"
                
        except Exception as e:
            print("erreur serveur maitre\n", e)
    
    return None

def add_admin(login, password):
    pass_hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()  #on hash le mdp pour la securité
    admin_l[login] = pass_hashed    #on stock le hash dans liste (login : hash)
    add_dico(ADMIN_LIST, admin_l)  #on sauvegarde la liste dans le fichier admins.json
    print(f"ADMIN {login} ADDED\n")

def synchro_dico(serv_maitre_host, serv_maitre_port, login, password, cmd):    #pour que le serveur et serveur maitre soit synchro et ai les memes donnees
    if serv_maitre_host and serv_maitre_port:
        try:
            serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serv.connect((serv_maitre_host, serv_maitre_port))
            connexion = "ADMIN " + login + " " + password +"\n"      #on ce connecte en admin au serveur maitre
            serv.sendall(connexion.encode('utf-8'))
            response = serv.recv(1024).decode('utf-8').strip()
            
            if response == "AUTH SUCCESSFUL":                        #si on reussi a ce connecter en admin au serv maitre
                request = cmd +"\n"                                  #on lui envoie la commande souhaiter pour le mettre a jour
                serv.sendall(request.encode('utf-8'))
            serv.close()

        except Exception as e:
            print("erreur syncrho dico\n", e)





if len(sys.argv) == 3:       #pour savoir si on initialise un serveur maitre ou non 
    port = int(sys.argv[1])
    dico_file = sys.argv[2]
    serv_maitre_host = None   #pas de serveur maitre
    serv_maitre_port = None

elif len(sys.argv) == 5:
    port = int(sys.argv[1])
    dico_file = sys.argv[2]
    serv_maitre_host = sys.argv[3]      #avec serveur maitre
    serv_maitre_port = int(sys.argv[4])

dico = load_dico(dico_file)      #charge le dico
admin_l = load_dico(ADMIN_LIST)   #charge liste admins

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
serv.bind(("",port))
serv.listen(5)
noyeux_joel()

print("Server open on port: ", port)

if (serv_maitre_host and serv_maitre_port):
    print("Server master open on: ", serv_maitre_host, serv_maitre_port)


is_connected = [serv]   #is_connected contient tous les sockets
admins = []             #liste pour savoir qui est co en admin
memory = {}             #sert pour stocker login password pour les admins connectés              
while is_connected :
        l1,l2,l3 = select.select(is_connected,[], []) #methode vu cours, l1 contient la liste des sockets qui veulent ce connecter
        for i in l1:
            if i is serv:
                conn,addr = serv.accept()
                print("New client", addr)
                is_connected.append(conn)    #ajoute nouveau client a la liste des connectées
            else :                        
                data = i.recv(1024).decode("utf-8").strip()

                if not data:   
                    print(f"CLIENT {login} DECONNECTE\n")     #sort de la boucle quand le client a quitté
                    if i in is_connected : 
                        is_connected.remove(i)                #on supprime le client de la liste des connectees
                    if i in admins :
                        admins.remove(i)                     
                    if i in memory :
                        del memory[i]                         #supprimer la clé et sa valeur
                    i.close()
                    continue
                response = None  
                
                if data:
                    sep = data.find(" ")       #cherche le premier espace, -1 si pas d'espace trouver
                    if sep == -1 :
                        if data == "EXIT":
                            if i in admins:
                                response = "ADMIN SESSION CLOSED\n"
                                i.sendall(response.encode("utf-8"))
                                is_connected.remove(i)       #supprime le client
                                admins.remove(i)
                                del memory[i]
                                i.close()
                                continue
                            else :
                                response = "EXIT SUCCESS\n"
                                i.sendall(response.encode("utf-8"))
                                is_connected.remove(i)
                                i.close()
                                continue
                        else:
                            response = "Usage : <cmd> <arg> OR Unknown command\n"
                    else :
                        cmd = data[:sep]        #stock ce qu'il y a avant le premier espace, donc la commande
                        arg = data[sep + 1:]    #stock ce qu'il y a apres le premier espace, donc l'argument

                            


                        if cmd == "GET" :
                            if arg in dico :
                                response = str(dico[arg]) + "\n"
                            else: 
                                response = "Key not found\n"
                                result_maitre = search_on_maitre(serv_maitre_host, serv_maitre_port, cmd, arg)  #si pas trouver sur le serveur on chercher sur le serveur maitre
                                if result_maitre:  #si on trouve ce que l'on cherche dans dico maitre
                                    response = result_maitre
                            
                                    if (result_maitre != "Key not found\n"):
                                        dico[arg] = result_maitre.strip()   #stock le resultat dans dico serveur si trouver sur serveur maitre mais pas serveur 
                                        add_dico(dico_file, dico)           #sauvegarde la nouvelle entrer
                            if i not in admins:  #si c'est pas un admin on repond puis on coupe la connexion avec serveur maitre
                                i.sendall(response.encode("utf-8"))
                                is_connected.remove(i)
                                i.close()
                                continue         #client suivant
                        
                        elif cmd == "PREF" :
                            prefix = arg
                            found = []
                            for k, v in dico.items():
                                if k.startswith(prefix):   # Vérifie si la clé commence par le préfixe
                                    found.append(f"{k}: {v}")  #on ajoute l'entrer trouver ; key , valeur
                            if found:
                                response = "\n".join(found)
                            else:
                                response = "Key not found\n"
                                result_maitre = search_on_maitre(serv_maitre_host, serv_maitre_port, cmd, arg) #si pas trouver sur le serveur on chercher sur le serveur maitre
                                if result_maitre:
                                    response = result_maitre
                            if i not in admins:         #si c'est pas un admin on repond puis on coupe la connexion avec serveur maitre
                                i.sendall(response.encode("utf-8"))
                                is_connected.remove(i)
                                i.close()
                                continue        #client suivant
                        


                        elif cmd == "ADMIN":
                            logmdp = arg.find(" ")
                            if logmdp == -1:
                                print("Usage : <login> <password>\n")
                                response = "Usage : <login> <password>\n"
                            else :
                                login = arg[:logmdp]
                                hash_client = arg[logmdp + 1:]

                                if login in admin_l:
                                    password = admin_l[login]
                                    if password == hash_client:
                                        admins.append(i)
                                        memory[i] = (login,password)        #on retient les logs
                                        response = "AUTH SUCCESSFUL"
                                        print(f"CLIENT {login} LOGGED AS ADMINISTRATOR")
                                    else :
                                        response = "AUTH FAILED"
                                else :
                                    response = "AUTH FAILED"
                            

                        elif cmd == "ADD_ADMIN":
                            if i not in admins:
                                response = "Vous devez être administrateur pour avoir accès à cette commande\n"
                            else:
                                sep = arg.find(" ")   #cherche le premier espace -1 si pas trouver
                                if sep == -1:
                                    response = "Usage : ADD_ADMIN <new_login> <new_password>"
                                else :
                                    new_login = arg[:sep]     #stock le login du nouveau admin
                                    new_password = arg[sep + 1:]     #stock le mdp du nouveau admin

                                    if new_login in admin_l:  #si le login existe deja
                                        response = f"Login {new_login} already used\n"
                                    else:
                                        add_admin(new_login, new_password)  #ajoute le nouveau admin
                                        synchro_dico(serv_maitre_host, serv_maitre_port, memory[i][0], memory[i][1], "ADD_ADMIN "+ new_login +" " + new_password) # on envoie au serveur maitre pour qu'il ajoute l'admin aussi, memory[i][0] c'est le login du client i et memory[i][1] sont mot de passe 
                                        response = f"Admin {new_login} added !\n"


                        elif cmd == "SET":
                            if i not in admins:
                                response = "Vous devez être administrateur pour avoir accès à cette commande\n"
                            else:
                                sep = arg.find(" ")
                                if sep == -1:
                                    response = "Usage : SET <key> <value>\n"
                                else:
                                    key = arg[:sep]
                                    value = arg[sep + 1:] 
                                    dico[key] = value         #met a jour le dico
                                    add_dico(dico_file, dico)     #sauvegarde l'ajout dans le fichier json
                                    
                                    mlogin, mpassword = memory[i]       #on récupère les logs de l'admin pour ce connecter sur le serveur maitre et mettre a jour serveur maitre
                                    synchro_dico(serv_maitre_host, serv_maitre_port, mlogin, mpassword, "SET "+ key +" " + value) # ajoute l'entrer au serveur maitre
                                    response = "UPDATE SUCCESSFUL\n"


                        elif cmd == "DEL":
                            if i not in admins:
                                response = "Vous devez être administrateur pour avoir accès à cette commande\n"
                            else:
                                mlogin, mpassword = memory[i] #stock le login et le mdp de l'admin i pour la recherche dans le serveur_maitre
                                if arg in dico:
                                    del dico[arg]       #si l'argument est trouver dans le dico on supprime cet argument
                                    add_dico(dico_file, dico)     #on sauvegarde la suppression dans le fichier json
                                    synchro_dico(serv_maitre_host, serv_maitre_port, mlogin, mpassword, "DEL " + arg) #met a jour le dico maitre apres supression d'une entrer
                                    response = "DELETION SUCCESSFUL\n"
                                else:
                                    response = "Key not found\n"
                                    synchro_dico(serv_maitre_host, serv_maitre_port, mlogin, mpassword, "DEL " + arg)



                        elif cmd == "EXIT": #ferme la session admin proprement
                            if i in admins :
                                response = "ADMIN SESSION CLOSED\n"
                                is_connected.remove(i)
                                admins.remove(i)
                                del memory[i]
                                i.close()
                                continue
                        else:
                            response = "Unknown command\n"

                if response and i in is_connected:
                    i.sendall(response.encode("utf-8"))
