#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Plugin servant a connaitre le nombre de connexions actives sur l'ensemble des serveurs TSE
Ce script utilise les retours des plugins check_connexions_tse.py presents sur les serveurs,
fait la somme et envoie le retour a nagios.

Pour ajouter un serveur TSE, installer NSClient++ et python sur le nouveau serveur et configurez
l'execution du script check_connexions_tse.py avec l'alias "alias_check_connexion_tse"
(voir le fichier nsclient-exemple.ini). Ensuite, editez ce script pour ajouter l'ip du serveur 
au tableau "serveurs"

Utilisation : check_connexions_tse_total.py -w <seuil alerte> -c <seuil critique>

Les seuils sont en nombre d'utilisateurs actifs.
"""

import os,sys,string,re,getopt

#Tableau contenant la liste des ips des serveurs TSE
serveurs = ["192.168.1.52", "192.168.1.213", "192.168.1.14"]

#Fonction d'affichage de l'aide
def aide():
    print """
Plugin servant a connaitre le nombre de connexions actives sur l'ensemble des serveurs TSE.
Ce script utilise les retours des plugins check_connexions_tse.py presents sur les serveurs,
fait la somme et envoie le retour a nagios.

Pour ajouter un serveur TSE, installer NSClient++ et python sur le nouveau serveur et configurez
l'execution du script check_connexions_tse.py avec l'alias "alias_check_connexion_tse"
(voir le fichier nsclient-exemple.ini). Ensuite, editez ce script pour ajouter l'ip du serveur 
au tableau "serveurs"

Utilisation : check_connexions_tse_total.py -w <seuil alerte> -c <seuil critique>

Les seuils sont en nombre d'utilisateurs actifs.
"""

#Recuperation des arguments
try:
    options, args = getopt.getopt(sys.argv[1:], "w:c:")
except getopt.GetoptError:
    aide() 
    sys.exit(3)

opt = [o for o,v in options]
val = [v for o,v in options]

#On verifie qu'il y a bien les deux options de renseignees
if not ("-w" in opt and "-c" in opt):
    aide()
    sys.exit(3)

#On recupere le seuil d'alerte
alerte = val[opt.index("-w")]
#On recupere le seuil critique
critique = val[opt.index("-c")]

#On verifie que les seuils sont bien des entiers
if not (re.match("^\d+$", alerte) and re.match("^\d+$", critique)):
    print "Les seuils d'alerte et critique doivent etre des entiers !"
    sys.exit(3)
    
#Conversion des seuils en type entier
alerte = int(alerte)
critique = int(critique)

#On verifie que le seuil d'alerte est >= au seuil critique
if alerte > critique:
    print "Le seuil d'alerte doit etre inferieur ou egal au seuil critique"
    sys.exit(3)

somme = 0
for serveur in serveurs:
    #On lance la commande pour recuperer la liste des utilisateurs
    retour = os.popen("/usr/local/nagios/libexec/check_nrpe -H {0} -c alias_check_connexions".format(serveur)).read()
    somme += int(re.findall("'nb_actifs'=(\d+)", retour)[0])
    somme += int(re.findall("'nb_decos'=(\d+)", retour)[0])
    
#On verifie par rapport aux seuils et on envoie le retour a Nagios
if somme >= critique:
    statut = "CRITIQUE"
    code = 2
elif somme >= alerte:
    statut = "ALERTE"
    code = 1
else:
    statut = "OK"
    code = 0

print "{0} : {1} utilisateurs actifs au total sur les serveurs TSE|total_utilisateurs={1}".format(statut, somme)
sys.exit(code)
