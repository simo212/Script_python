#!/usr/bin/python

#Plugin pour verifier la connexion internet. Ca fait un ping sur 3 sites differents :
#des que l'un d'eux repond, on renvoie "OK", sinon on indique qu'aucun n'est joignable, donc connexion internet pas bonne a priori.

import os,sys,re,string

for site in ["google.fr", "yahoo.fr", "millenium.org"]:
    retour = os.popen("ping -c 1 -W 5 {0} 2> /dev/null".format(site)).read()
    recu = re.findall("([01]) received", retour)
    if not recu == []:
        recu = recu[0]
        if recu == "1":
            print "Ping sur {0} reussi |dispo=1".format(site)
            sys.exit(0)

print "Aucun ping reussi sur les trois ! |dispo=0"
sys.exit(2)

