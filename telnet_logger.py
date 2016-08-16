#!/usr/bin/env python3

# telnet_logger.py
# -John Taylor
# Aug-16-2016
# Python 3.5.2
# Logs a non-interactive telnet session

"""
Example ini file, with 2 sections:

[main]
host=rainmaker.wunderground.com 
port=23
# this should be a UNC path so that it is clickable from within an email client
logfile=\\_HOST_\c$\logs\session-_DATE_._TIME_.log

[smtp]
use_smtp=yes
host=smtp.example.com
from=Alert User <alerts@example.com>
to=admins@example.com

"""

import sys,os.path,time,logging,smtplib
import configparser,telnetlib,argparse
import platform
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

pgm_name="telnet_logger.py"
pgm_version=1.0
pgm_date="2016-08-16 09:33"

# global reference to the .ini config file
config = False

# global reference to the telnet connection
tn = False

# time in seconds before a telnet open operation will timeout
tn_timeout = 10

############################################################################################################

# convert _DATE_ with current YYMMDD
# convert _TIME_ with HHMMSS
# convert _HOST_ with the system's Hostname
def expand_config_macros():
	global config

	d = time.strftime("%Y%m%d", time.localtime())
	t = time.strftime("%H%M%S", time.localtime())
	localhost = get_localhost_name()

	config["main"]["logfile"] = config["main"]["logfile"].replace("_DATE_",d).replace("_TIME_",t).replace("_HOST_",localhost)

############################################################################################################

# return "" (empty string) on success, error message on failure
def validate_config_file():
	global config

	valid = 0
	for c in config.sections():
		if "main" == c: valid += 1
		if "smtp" == c: valid += 1

	if valid != 2:
		return "Error #102: config file must contain 2 sections: main, smtp";
		
	valid = 0
	for c in config["main"]:
		if "host" == c: valid += 1
		if "port" == c: valid += 1
		if "logfile" == c: valid += 1

	if valid != 3:
		return "Error #103: config 'main' scection must contain 3 settings: host, port, logfile";

	valid = 0
	for c in config["smtp"]:
		if "use_smtp" == c: valid += 1
		if "host" == c: valid += 1
		if "from" == c: valid += 1
		if "to" == c: valid += 1

	if "no" == config["smtp"]["use_smtp"]:
		return ""

	if valid != 4:
		return "Error #103: config 'smtp' scection must contain 4 settings: use_smtp, host, from, to";

	return ""

############################################################################################################

# connect to telnet server on given port
# return "" (empty string) on success, error message on failure
def telnet_connect():
	global config, tn, tn_timeout

	err_msg = ""
	try:
		tn = telnetlib.Telnet(config["main"]["host"], config["main"]["port"], tn_timeout)
	except:
		err_msg = "telnet connection error: %s" % (sys.exc_info()[0])

	return err_msg

############################################################################################################

# start reading from telnet on an open connection
# write the incoming telnet contents to the log file
def telnet_read():
	global config

	err_msg=""
	while(1):
		try:
			tmp = tn.read_very_eager()
		except:
			err_msg = "telnet read error: %s" % (sys.exc_info()[0])
		data = tmp.decode()
		if(len(data)):
			print(data)
			logging.info(data)
		time.sleep(1)

############################################################################################################

# typically returns the value of COMPUTERNAME or HOSTNAME env variable
def get_localhost_name():
	return platform.node()

############################################################################################################

# send an email notification
# msg_type should be either 'started' or 'ended'
def email_notify(msg_type):
	if "yes" != config["smtp"]["use_smtp"]:
		return

	localhost = get_localhost_name()	
	now = time.strftime("%Y:%m:%d %H:%M:%S", time.localtime())

	email_subject = "%s %s at %s on %s" % (pgm_name, msg_type, now, localhost)
	email_body = "Log file path: %s\r\n\r\n" % (config["main"]["logfile"])

	msg = MIMEMultipart()
	msg["Subject"] = email_subject
	msg["From"] = config["smtp"]["from"]
	msg["To"] = config["smtp"]["to"]
	part1 = MIMEText(email_body, 'plain')
	msg.attach(part1)

	try:
		s = smtplib.SMTP(config["smtp"]["host"])
		s.send_message(msg)
		s.quit()
	except:
		err_msg = "email error: %s" % (sys.exc_info()[0])
		print(); print(err_msg); print()
		logging.info(err_msg)
		return False

	return True
	
############################################################################################################

# program exeuction begins here
# return a valid integer for program's exit code back to the OS
def main():
	global config, tn
	
	# parse cmd-line arguments
	parser = argparse.ArgumentParser(description="%s: write telnet ouput to a log file" % (pgm_name), epilog="version: %s (%s)" % (pgm_version,pgm_date))
	parser.add_argument("ini_config_file", help="full path to ini config file")
	args = parser.parse_args()

	# load the ini config file
	if not os.path.isfile(args.ini_config_file):
		print(); print("Error #101, unable to open:", args.ini_config_file); print()
		return 1

	# verify config file contents
	config = configparser.ConfigParser()
	config.read(args.ini_config_file)

	err_msg = validate_config_file()
	if len(err_msg):
		print(err_msg)
		return 2
	else:
		expand_config_macros()
		logging.basicConfig(filename=config["main"]["logfile"],level=logging.INFO,format='%(asctime)s|%(message)s',datefmt='%Y%m%d.%H%M%S')
		print(); print("logfile:", config["main"]["logfile"]); print()
		email_notify("started")

	# start telnet connection
	err_msg = telnet_connect()
	if len(err_msg):
		print(err_msg)
		logging.info(err_msg)
		logging.shutdown()
		return 3

	# read telnet stream and write it to a log file
	err_msg = ""
	try:
		telnet_read()
	except:
		err_msg = "telnet read error: %s" % (sys.exc_info()[0])
		print(); print(err_msg); print()
		logging.info(err_msg)
		logging.shutdown()
		return 3

	return 0
	
############################################################################################################

if "__main__" == __name__:
	m = main()
	email_notify("ended")
	sys.exit( m )

# end of script
