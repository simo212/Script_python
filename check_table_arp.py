#!/usr/bin/python

import os,sys,re

#Communaute SNMP des switchs
communaute = "snmpNAGIOS78"

#On verifie qu'il y a le nombre d'arguments necessaire
if len(sys.argv) < 4:
    print """
Sonde comptant le nombre d'enregistrements dans la table ARP du switch.

Utilisation : check_table_arp.py <ip switch> <seuil alerte> <seuil critique>

Les seuils sont en nombre d'entrees dans la table.
"""
    sys.exit(3)

#On recupere les arguments
ip = sys.argv[1]
alerte = int(sys.argv[2])
critique = int(sys.argv[3])

#On verfie le format de l'ip
if not re.match("^192\.168\.\d{1,3}\.\d{1,3}$", ip):
    print "L'ip du switch n'a pas un format valide (192.168.xxx.xxx)"
    sys.exit(2)

#On verifie que le seuil critique est >= au seuil d'alerte
if alerte > critique:
    print "Le seuil d'alerte doit etre inferieur ou egal au seuil critique"
    sys.exit(2)

#On interroge le switch
retour = os.popen("snmpwalk -c {0} -v 1 {1} 1.3.6.1.2.1.4.22.1.2 | wc -l".format(communaute, ip)).read()

#On convertit le nombre d'entres en entier
nb_entrees = int(retour)

#Preparation du statut et du code de retour
statut = "OK"
code = 0

#On compare avec les seuils
if nb_entrees >= alerte:
    statut = "ALERTE"
    code = 1

if nb_entrees >= critique:
    statut = "CRITIQUE"
    code = 2

#Message de retour
print "{0} - Il y a {1} entrees dans la table ARP du switch {2} | nb_entrees={1}".format(statut, nb_entrees, ip)
sys.exit(code)
