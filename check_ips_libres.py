#!/usr/bin/python

#Plugin qui sert a connaitre le nombre d'IPs libres d'un DHCP windows pour un sous reseau
#Utilisation : check_ips_libres.py -H <ip DHCP> -n <adresse sous reseau> -w <seuil alerte> -c <seuil critique>

import sys,os,re,getopt

#Fonction d'affichage de l'aide
def aide():
    print """
Plugin pour connaitre le nombre d'adresse IP libres d'un DHCP windows pour un sous reseau.

Options a renseigner :
    -H <ip du serveur DHCP>
    -n <adresse du sous reseau>  (du type 192.168.1.0)
    -w <seuil d'alerte>  (nombre d'ip libres)
    -c <seuil critique>  (nombre d'ips libres)
"""

#Debut du programme
try:
    #Recuperation des otpions
    options, args = getopt.getopt(sys.argv[1:], "H:n:w:c:")
except getopt.GetoptError:
    #Option inattendue : affiche l'aide et quitte
    aide()
    sys.exit(3)

#S'il manque des otpions, affiche l'aide et quitte
if not len(options) == 4:
    aide()
    sys.exit(3)

#On recupere les options dans un tableau et leurs valeurs dans un autre (plus pratique)
opt=[o for o, v in options]
val=[v for o, v in options]

addr = val[opt.index("-H")]
ss_reseau = val[opt.index("-n")]
alerte = int(val[opt.index("-w")])
critique = int(val[opt.index("-c")])

#On verifie que l'ip du serveur a un format valide
if not re.match("^(\d{1,3}\.){3}\d{1,3}$", addr):
    print "Adresse IP invalide pour l'option -H"
    sys.exit(3)

#On verifie que l'ip du sous reseau a un format valide
if not re.match("^(\d{1,3}\.){3}0$", ss_reseau):
    print "Adresse de sous reseau invalide"
    sys.exit(3)

#On verifie que les seuils sont positifs et que alerte >= critique
if alerte < critique or alerte < 0 or critique < 0:
    print "Les seuils d'alerte et critique doivent etre des entiers, et alerte > critique"
    sys.exit(3)

try:
    #On fait une reqete snmp pour avoir le nombre d'adresses utilisees
    retour = os.popen("snmpget -c public -v 1 {0} SNMPv2-SMI::enterprises.311.1.3.2.1.1.2.{1}".format(addr, ss_reseau)).read()
    #On recupere le nombre d'adresses dans le retour
    utilisees = int(re.findall("\d+$", retour.strip())[0])

    #On fait une requete snmp pour avoir lenombre d'adresses libres
    retour = os.popen("snmpget -c public -v 1 {0} SNMPv2-SMI::enterprises.311.1.3.2.1.1.3.{1}".format(addr, ss_reseau)).read()
    #On recupere le nombre d'adresses dans le retour
    libres = int(re.findall("\d+$", retour.strip())[0])
except:
    print "Erreur : impossible d'obtenir des informations pour ce sous reseau"
    sys.exit(3)

total = libres + utilisees

#On compare avec les seuils
if libres <= critique:
    statut = "CRITIQUE"
    code = 2
elif libres <= alerte:
    statut = "ALERTE"
    code = 1
else:
    statut = "OK"
    code = 0

#Retour pour Nagios
print "{0} : Il reste {1} IPs libres sur {2} pour le sous reseau {3}".format(statut, libres, total, ss_reseau)
sys.exit(code)
