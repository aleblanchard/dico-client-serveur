#!/usr/bin/env python3
import socket
import sys
import hashlib

rouge = "\033[31m"     #pour avoir couleur dans le terminal
VERT = "\033[32m"
BLEU = "\033[34m"
cyan = "\033[35m"
RESET = "\033[0m"

def main():
    if len(sys.argv) != 3:
        print(f"Usage : python3 dico_admin.py <host> <port>\n")
        sys.exit(1)
    host = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except Exception as e :
        print("erreur le port doit etre un nombre de 0 à 65535\n", e)
        sys.exit(1)
    
    try:
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv.connect((host, port))
        print(f"Connecté (client admin) sur : {host}:{port}")

        ok = False
        while not ok:        #tant qu'on est pas connecté au serveur"
            user = input(f"{cyan}Login : ")
            password = input(f"{cyan}Password: ")
            hash_client = hashlib.sha256(password.encode('utf-8')).hexdigest() #pour chiffrer le mot de passe et ne pas l'envoyer en clair sur le reseau
            request = "ADMIN "+ user +" "+ hash_client + "\n"      #on envoie la commande ADMIN USER HASHED_PASS 
            serv.sendall(request.encode('utf-8'))

            data = serv.recv(1024).decode('utf-8').strip()
            if data == "AUTH SUCCESSFUL":       #si on arrive a ce connecter en admin
                ok = True                  #on est connecté on sort de la boucle
                print(f"{VERT}LOGGED AS ADMINISTRATOR\n {RESET}")
            else :
                print(f"{rouge}LOGIN OR PASSWORD INCORRECT\n {RESET}")



        while True:    #pour rester connecter en continu on reste dans boucle
            command = input(f"{VERT}@{user} ->{RESET} ")
            if command == "EXIT":
                break       #si on ce deconnecte "EXIT", on sort de la boucle
            request = command
            serv.sendall(request.encode('utf-8'))


            data = serv.recv(1024)
            if len(data) == 0:
                break
            reponse = data.decode('utf-8').strip()
            print(reponse)

    except Exception as e:
        print("Erreur \n", e)









if __name__ == "__main__":
    main()