#!/usr/bin/python

# -*- coding: utf-8 -*-

import sys,os,string,re, getopt

#Affichage de l'aide
def aide():
	print """
	Sonde servant a surveiller le processeur du coeur de reseau.
		
	Utilisation : check_cpu_switch.py -h <ip switch> [-w <seuil alerte>] [-c <seuil critique>]
	
	Les seuils sont en % d'utilisation (s'applique a la moyenne de la charge du processeur sur 5 minutes)
	"""
	sys.exit(3)
    
#Recuperation des options
try:
	options, args = getopt.getopt(sys.argv[1:], "h:w:c:")
except getopt.GetoptError:
	print aide()

opt=[o for o, v in options]
val=[v for o, v in options]

#Si l'hote n'est pas indique, on affiche l'aide
if not '-h' in opt:
	aide()
	
#Recuperation du seuil d'alerte
if "-w" in opt:
	alerte = int(val[opt.index("-w")])
#Recuperation du seuil critique
if "-c" in opt:
	critique = int(val[opt.index("-c")])
#Si critique < alerte, ca va pas
if "-w" in opt and "-c" in opt and critique < alerte:
	print "Le seuil critique doit etre superieur ou egal au seuil d'alerte"
	sys.exit(2)
	
#On recupere l'ip du switch
ip = val[opt.index('-h')]
if not re.match("(\d{1,3}\.){3}\d{1,3}", ip):
    print "Le format de l'adresse IP fournie n'est pas valide"
    sys.exit(3)

#On recupere les donnees
retour = os.popen("snmpget -c snmpNAGIOS78 -v 1 {0} .1.3.6.1.4.1.43.45.1.6.1.1.1.3.65536 2> /dev/null".format(ip)).read()
val_retour_1 = re.findall("Gauge32: (\d+)", retour)

retour = os.popen("snmpget -c snmpNAGIOS78 -v 1 {0} .1.3.6.1.4.1.43.45.1.6.1.1.1.4.65536 2> /dev/null".format(ip)).read()
val_retour_2 = re.findall("Gauge32: (\d+)", retour)

if val_retour_1 == [] or val_retour_2 == []:
    print "Erreur dans la recuperation des donnees"
    sys.exit(3)

cpu1 = int(val_retour_1[0])
cpu5 = int(val_retour_2[0])

statut = "OK"
code = 0

#On compare avec les seuils
if "-w" in opt and int(cpu5) >= alerte:
	statut = "ALERTE"
	code = 1
	
if "-c" in opt and int(cpu5) >= critique:
	statut = "CRITIQUE"
	code = 2

	#Retour de la sonde
print "{2} - Utilisation CPU : moyenne 1 min = {0}%, moyenne 5 min = {1}% | moy_1_min={0}% moy_5_min={1}%".format(cpu1, cpu5, statut)
sys.exit(code)

