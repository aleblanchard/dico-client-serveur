#!/bin/bash

cd .. #pour avoir acces a admins.json sinon ca marchait pas car ca chercher dans /tests/data/admin.json alors que c'est dans data/admins.json

PORT_MASTER=8888
PORT=7777
HOST=localhost
DICO_MASTER="data/mois_duree_maitre.json"
DICO="data/mois_duree.json"

python3 dico_server.py "$PORT_MASTER" "$DICO_MASTER" >/dev/null &
PID_MASTER=$!
sleep 1

python3 dico_server.py "$PORT" "$DICO" "$HOST" "$PORT_MASTER" >/dev/null &
PID=$!
sleep 1

echo " "
echo "-------------- TESTS CLIENT --------------"
echo " "
echo "---- TESTS GET ----"
echo " "

echo "Test 1 : GET janvier (présent que sur serveur maitre), réponse attendu: 31"
python3 dico_client.py "$HOST" "$PORT" get "janvier"
echo " "

echo "Test 2 : GET avril (présent sur serveur), réponse attendu: 30"
python3 dico_client.py "$HOST" "$PORT" get "avril"
echo " "

echo "Test 3 : GET février (présent que sur serveur maitre), réponse attendu: 28"
python3 dico_client.py "$HOST" "$PORT_MASTER" get "février"
echo " "

echo "Test 4 : GET erreur, réponse attendu: Key not found"
python3 dico_client.py "$HOST" "$PORT" get "juuuuuillet"
echo " "

echo " "
echo "---- TESTS PREF ----"
echo " "

echo "Test 1 : PREF j (juin/juillet présent localement), réponse attendu: juin: 30\n juillet: 31\n janvier: 31\n"
python3 dico_client.py "$HOST" "$PORT" pref "j"
echo " "

echo "Test 2 : PREF f (présent uniquement sur le serveur maître), réponse attendu: février: 28"
python3 dico_client.py "$HOST" "$PORT" pref "f"
echo " "

echo "Test 3 : PREF s (présent uniquement sur le serveur maître), réponse attendu: septembre 30"
python3 dico_client.py "$HOST" "$PORT" pref "s"
echo " "

echo "Test 4 : PREF jjjjjj , réponse attendu: Key not found"
python3 dico_client.py "$HOST" "$PORT" pref "jjjjjj"
echo " "

echo " "
echo "-------------- TESTS ADMIN --------------"
echo " "

echo "Test 1 : SET admin_test 1234 (doit mettre a jour les deux dictionnaires de serveur et serveur maitre), réponse attendu: UPDATE SUCCESSFUL"
echo -e "admin\n1234\nSET admin_test 1234\nEXIT" | python3 dico_admin.py "$HOST" "$PORT"
echo " "

echo "Test 2 : GET admin_test, Verifie si bien present apres: SET admin_test 1234, réponse attendu: 1234"
python3 dico_client.py "$HOST" "$PORT_MASTER" get "admin_test"
echo " "

echo "Test 3 : PREF adm, Verifie si bien present apres: PREF adm, réponse attendu: admin_test : 1234"
python3 dico_client.py "$HOST" "$PORT_MASTER" pref "adm"
echo " "

echo "Test 4 : DEL admin_test, (doit supprimer sur les deux dictionnaires), réponse attendu: DELETION SUCCESSFUL"
echo -e "admin\n1234\nDEL admin_test\nEXIT" | python3 dico_admin.py "$HOST" "$PORT"
echo " "

echo "Test 5 : Vérification synchro, verifie si bien supprimé sur serveur maitre apres: DEL admin_test, réponse attendu: Key not found"
python3 dico_client.py "$HOST" "$PORT_MASTER" get "admin_test"
echo " "

echo "Test 6 : Ajout d'un nouvel administrateur professeur"
echo -e "admin\n1234\nADD_ADMIN professeur 0000\nEXIT" | python3 dico_admin.py "$HOST" "$PORT"
echo " "

echo "Test 7 : Connexion sur le nouvel admin professeur et ajout d'une entrée, réponse attendu : UPDATE SUCCESSFUL"
echo -e "professeur\n0000\nSET Porofesseur Si tu as la ref tu joues à LoL\nEXIT" | python3 dico_admin.py "$HOST" "$PORT"
echo " "

echo "Test 8 : Vérification sur le serveur maitre si l'entrée à bien était rajouté, réponse attendu : Si tu as la ref tu joues à LoL"
python3 dico_client.py "$HOST" "$PORT_MASTER" get "Porofesseur"
echo " "

kill "$PID"
kill "$PID_MASTER"