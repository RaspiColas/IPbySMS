#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------------------------------#
#													#
#				IP-by-SMS.py						#
#													#
#---------------------------------------------------#

"""

Script pour envoyer par SMS l'adresse IP et le HOSTNAME d'un pi

Ecrit par Nicolas Mercouroff 
Version du 2 novembre 2020

"""

from time import sleep, strftime
import urllib2, socket
import ConfigParser
from os import path
from sys import argv

PATH_PREFIX = path.dirname(path.abspath(__file__)) + '/'
LOG_FILENAME = PATH_PREFIX + 'log_sms.log'
CONFIG_FILENAME = PATH_PREFIX + 'ipbysms.conf'
HOSTNAME = '/proc/sys/kernel/hostname'
SMS_URL = "https://smsapi.free-mobile.fr/sendmsg"
MAX_ITER = 20  # Max nb of iteration of info fetching attempts
DELAY = 60  # Delai between two retries in seconds

# Tableau des codes erreurs HTTP
HTTPErrorCode = {
    200: "Requête traitée avec succès le SMS a été envoyé sur votre mobile",
    400: "La syntaxe de la requête est erronée",
    402: "Trop de SMS ont été envoyés en trop peu de temps.",
    403: "Vous n’avez pas activé le service ou vous avez fait une erreur dans le login ou le mot de passe.",
    500: "Erreur interne du serveur. Réessayez ultérieurement.",
    999: "Erreur inconnue. Réessayez ultérieurement."
}

param = {}
debug = False


def tolog(txt, forceprint=False):
	"""
		Logs events and prints it if forceprint or verbose = True
	"""
	if debug or forceprint:
		print(txt)
	now = strftime('%Y/%m/%d %H:%M:%S')
	msg = "%s\t%s" % (now, txt)
	with open(LOG_FILENAME, 'a') as file:
		file.write(msg + "\n")
	return


#-------------------------------------------------
#		Read config
#-------------------------------------------------

def get_conf():
	global param

	tolog("Loading the configuration file...")
	try:
		config = ConfigParser.ConfigParser()
		config.read(CONFIG_FILENAME)

		param["user1"] = config.get('SMSAPI', 'user')
		param["pass1"] = config.get('SMSAPI', 'pass')
		tolog("...success loading config")
		return True

	except Exception as e:
		tolog('Error reading config file %s: %s' % (CONFIG_FILENAME, e), True)
		return False


#-------------------------------------------------
#		Send SMS
#-------------------------------------------------


def send_text_sms(text):
	"""
		Sending text by SMS  
	"""
	msg = "%21Alerte%20" + text
	tolog("Sending message '%s' by SMS..." % (msg))
	api_url = "%s?user=%s&pass=%s&msg=%s" % (SMS_URL, param["user1"], param["pass1"], msg)
	try:
		req = urllib2.Request(api_url)
		rep = urllib2.urlopen(req)
		HTTPError = rep.getcode()
		tolog("...return code %s: %s" % (HTTPError, HTTPErrorCode[HTTPError]))
		return True
	except Exception as e:
		tolog('Error Service smsapi.free-mobile.fr: %s' % (e), True)
		return False


#-------------------------------------------------
#		Get IP
#-------------------------------------------------

def get_local_ip():
	tolog("Getting local IP...")
	no_err = True
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.connect(("8.8.8.8", 80))
		ip = sock.getsockname()[0]
		sock.close()
		tolog("...success getting IP: %s" % (ip))
	except Exception as e:
		tolog("Error getting local IP: %s" %(e), True)
		ip = "(unknown ip)"
		no_err = False

	tolog("Getting local hostname...")
	try:
		with open(HOSTNAME, 'r') as f:
			hostname = f.read().strip()
	except Exception as e:
		tolog("Error getting local hostname: %s" % (e), True)
		hostname = "(unknown hostname)"
	
	return no_err, ip, hostname


#-------------------------------------------------
#		Main
#-------------------------------------------------

def ip_by_sms():

	if not get_conf():
		return False

	for i in range(MAX_ITER):
		tolog("Fecthing local IP: attemp #%s" % (i))
		no_err, local_IP, hostname = get_local_ip()
		if no_err:
			break
		tolog("Sleeping for %s s..." % (DELAY), True)
		sleep(DELAY)
	if not no_err:
		return False

	for i in range(MAX_ITER):
		tolog("Sending local IP: attemp #%s" % (i))
		no_err = send_text_sms("%s%%20IP%%20=%%20%s" % (hostname, local_IP))
		if no_err:
			return True
		tolog("Sleeping for %s s..." % (DELAY), True)
		sleep(DELAY)

	return False


if __name__ == '__main__':
	if len(argv) == 2:
		debug = (argv[1] == '-v')

	ip_by_sms()


#-------------------------------------------------
#----- FIN DU PROGRAMME --------------------------
#-------------------------------------------------
