#!/usr/bin/env python3
import socket
import sys

def main():
    if len(sys.argv)< 5:
        print("Commande inconnu\n")
        print("Usage: python3 dico_client.py <host> <port> <command> <key>\n") 
        print("Commands:")
        print("GET <key> : Récupère la valeur associée à la clé. Affiche 'Key not found' si la clé n'existe pas.\n")
        print("PREF <prefix> : Affiche toutes les couples clé-valeur dont la clé commence par le préfixe donné.\n")
        sys.exit(1)

    host = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except Exception as e:
        print("erreur le port doit etre un nombre de 0 à 65535\n", e)
        sys.exit(1)
    command = sys.argv[3].upper()
    key = sys.argv[4]

    if (command != "GET" and command != "PREF"):
        print("erreur commande inconnu\n")
        sys.exit(1)

    try:
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv.connect((host, port))

        request = command +" "+ key+"\n"
        serv.sendall(request.encode('utf-8'))
        result = ""
        while True:
            data = serv.recv(1024)
            if len(data) == 0:
                break
            result += data.decode('utf-8').strip()
        if result:
            print(result+"\n")
        else:
            print("erreur\n")
        serv.close()


    except Exception as e:
        print("erreur", e)
        sys.exit(1)

if __name__ == "__main__":
    main()