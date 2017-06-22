"""
sdc.py - Save Device Config
John Taylor
Jun-16-2017

The purpose of this script is to:
-	Periodically, save the config of all devices listed in the config.ini file
-	If the currently downloaded config file is a duplicate of the previously saved config file, then it is not saved again
-	When a change is made to a config, email a "diff" between the previous config and the current config

All of the options / settings are in the config.ini file.

The program has two modes: a server mode and a client mode. When the server starts, it generates a random UDP port number (that it listens on) and a random UUID.  
These are sent in an email as the first portion of an Authentication string.  The remaining portion is a password which is a secret that only you should know.
These 3 comma-delimited items make up the full Authentication string.

Example:
9676,3d894414-2f07-467b-9473-3a03c4bd2ac2,SECRET_PASSWORD_HERE
(There no spaces in between fields.)

To run the server:

cd \sdc\save_device_config
if not exist sdc.sqlite3 sqlite3 sdc.sqlite3 < schema.sql
python sdc.py -c config.ini

Once this is running, it will send an email with the first portion of the Authentication string and then listen on the chosen UDP port number.

To run the client:

cd \sdc\save_device_config
python sdc.py -c config.ini -a

This will ask for the Authentication string, which can be pasted in.  It will not be displayed on the screen.
If the Authentication string is correct, you should then see:
Response: OK

If the password is not correct, the server will return an error and then exit.
This entire process will have to be started again.

#################################################################################################

Developed on Jun-16-2017
========================
Windows 10, OS X 10.6
Python 3.6.1
netmiko 1.4.1 (3rd party Python module)

Supported device types, see CLASS_MAPPER_BASE:
https://raw.githubusercontent.com/ktbyers/netmiko/master/netmiko/ssh_dispatcher.py
You must update the 'device_commands' dict (below)

More on the password encryption:
https://cryptography.io/en/latest/

To create an encrypted Fernet password for the INI file:
from cryptography.fernet import Fernet
key = Fernet.generate_key() # save this key to your password database/keychain
f = Fernet(key)
password = f.encrypt(b"your_device_password_goes_here")
print(password)
"""

#################################################################################################
# Example config.ini:
"""
# devices: comma-delimited list of host names or ip addresses
# port: optional, default is DEFAULT_PORT (22)
# verbose: optional [True|False]; when True, see more details about the SSH connection
# username: the SSH host login name
# password: this is reversible encryption for the device password

# file_dest macros
# ----------------
# &X = section name
# &V = device name
# &T = device type
# &I = ip address
# &P = port number
# &Y = year  &M = month  &D = day
# &H = hour  &N = minute  &S = second
# &O = OS path separator (usually '/' or '\')

[global]
database=sdc.sqlite3
sleep_time=60

[smtp]
server=smtp.example.com
from=noreply@example.com
to_list=alerts@example.com

[switches]
device_type=hp_procurve
device_list=switch1, switch2, switch3
username=admin
password=gAAAmf09fsd0MDS0FMFFDM0DK94307GJ09TJ54_jfsdsdfFSEF439843NFOsfhnsfh349834409tdfklgndfgFLSD43FDGN=s===
config_fname=configs&O&T&O&V&O&V--&Y&M&D.&H&N&S.log
"""
# end of example config.ini
#################################################################################################

#################################################################################################
# schema.sql
"""
drop table if exists files;
create table if not exists files (
	id                   integer primary key autoincrement,
	section              varchar(256) collate nocase,
    device_name          varchar(256) collate nocase,
    device_type          varchar(256) collate nocase,
    username             varchar(64) collate nocase,
    ip                   varchar(256) collate nocase,
    port                 integer not null default 22,
    config_fname         varchar(1024) collate nocase,
    config_sha1          char(40),
    config_sha256        char(64),
    config_fsize         int not null default 0,
	db_insert_date       timestamp,
    run_time             timestamp,
    same_as_prev_cfg     int not null default 0

    constraint section_len check( length(section) >= 2 and length(section) <= 256),
	constraint device_name_len check( length(device_name) >= 2 and length(device_name) <= 256),
    constraint username_len check( length(username) >= 2 and length(username) <= 64),
    constraint device_type_len check( length(device_type) >= 2 and length(device_type) <= 256),
    constraint ip_len check( length(ip) >= 2 and length(ip) <= 256),
    constraint port_range check (port >= 1 and port <=65535),
    constraint config_fname check( length(config_fname) >=2 and length(config_fname) <= 1024),
    constraint config_sha1 check( length(config_sha1) == 40),
    constraint config_fsize check(config_fsize > 0),
	constraint did_date check( db_insert_date >= '2017-06-19' ),
	
	--
	constraint date_year check( cast(substr(db_insert_date,1,4) as integer) >= 2017 and cast(substr(db_insert_date,1,4) as integer) <= 2099),
	constraint date_month check( cast(substr(db_insert_date,6,2) as integer) >= 1    and cast(substr(db_insert_date,6,2) as integer) <= 12),
	constraint date_day check( cast(substr(db_insert_date,9,2) as integer) >= 1    and cast(substr(db_insert_date,9,2) as integer) <= 31)
);
drop trigger if exists trig_files_did;
create trigger trig_files_did after insert on files
begin
	update files set db_insert_date = datetime('now','localtime') where rowid = new.rowid;
end;
"""
# end of schema.sql
#################################################################################################

# TODO: make sure listening UDP port in not already in use
# TODO: retention on conf files
# TODO: use the runtime field in the SQL so that there is consistent times across muliple scans

#################################################################################################

from cryptography.fernet import Fernet
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from netmiko import ConnectHandler
import argparse
import configparser
import difflib
import getpass
import hashlib
import os
import os.path
import random
import smtplib
import socket
import socketserver
import sqlite3
import sys
import time
import uuid

pgm_name="sdc"
pgm_version="1.01"
pgm_date="Jun-22-2017"

DEFAULT_PORT = 22
INTERNAL_INI_SECTIONS = ( "global", "smtp" )
VERBOSE_OUTPUT = True

device_commands = {}
device_commands["hp_procurve"]    = ( "no page", "SAVE::show run" )
device_commands["hp_comware"]     = ( "SAVE::display current-configuration", )
device_commands["paloalto_panos"] = ( "set cli pager off", "SAVE::show config running")
device_commands["ubiquiti_edge"]  = ( "configure", "run terminal length 9999", "SAVE::run show configuration all", "exit")

#################################################################################################

def create_html_diff(oldfname:str, newfname:str) -> str:
    """Create an html version of the difference between the previous and current configs

    Args:
        oldfname: file name of the previously saved config file

        newfname: file name of the config file that was just saved

    Return:
        The file name that contatins the html diff
    """

    if VERBOSE_OUTPUT: print("Creating HTML diff between: old:%s   new:%s" % (oldfname,newfname))
    with open(oldfname) as fp: oldlines = fp.read().splitlines()
    with open(newfname) as fp: newlines = fp.read().splitlines()

    olddesc = os.path.basename(oldfname)
    newdesc = os.path.basename(newfname)
    html_diff = difflib.HtmlDiff().make_file(oldlines,newlines,olddesc,newdesc,context=True,numlines=3)
    diffname = "%s%sdiff__%s__%s.html" % (os.path.dirname(newfname), os.sep, olddesc, newdesc)
    if os.path.exists(diffname):
        os.remove(diffname)
    if VERBOSE_OUTPUT: print("Creating HTML diff file: %s" %(diffname))
    with open(diffname,mode="w",encoding="utf-8") as fp:
        fp.write(html_diff)

    return diffname

#################################################################################################

def err(errno:int, msg:str, fatal:bool=False) -> None:
    """Output an error message and optionally exit the program

    Args:
        errno: A error number, these should be unique for each caller

        msg: The error message that you want the user to see

        fatal: if True, exit the program; otherwise, continue
    """

    abort = "[FATAL]" if fatal else ""
    print("",file=sys.stderr)
    print("Error #%s %s" % (errno,abort),file=sys.stderr)
    print(msg, file=sys.stderr)
    print("",file=sys.stderr)

    if fatal: sys.exit(errno)

    return None

#################################################################################################

def get_ip_address(host:str) -> str:
    """Return an IP address when given a hostname

    Args:
        host: the host name or IP address

        Return:
            The dotted quad ip address or None if the DNS name can not be resolved
    """

    try:
        ip = socket.gethostbyname(host)
    except:
        return None

    return ip

#################################################################################################

def run_device_commands(obj:dict, dtype:str) -> list:
    """Execute commands on a remote host via a SSH channel

    Args:
        obj: contains key-values sutiable for ConnectHandler
             these include device_type, ip, username, password, port (optional), secret (optional), verbose (optional)

        dtype: the device_type, used for the global device_commands dict

    Returns:
        A list of command outputs.  Any command that is prefixed with SAVE:: will be saved to this list
    """

    saved_output = []
    try:
        net_connect = ConnectHandler(**obj)
    except:
        msg = "%s\n%s" % (sys.exc_info()[0],sys.exc_info()[1])
        err(5926,msg)
        time.sleep(30)
        return []
    
    for raw_cmd in device_commands[dtype]:
        cmd = raw_cmd.split("SAVE::")[-1]
        if len(cmd) <= 1:
            err(7833,"Device command should be longer than 1 character: %s" %(cmd))
            net_connect.disconnect()
            return []
        if VERBOSE_OUTPUT: print("Sending: %s" % (cmd))
        
        output = net_connect.send_command(cmd)
        save = True if "SAVE::" in raw_cmd else False
        if save:
            saved_output.append(output)

    net_connect.disconnect()
    return saved_output

#################################################################################################

def replace_macros(orig:str, now:time.struct_time, section:str, device_name:str, device_type:str, ip:str, port:int ) -> str:
    """Substitue macros listed in the ini file's config_fname property for real values.
       See the ini documentation & example above

    Args:
        orig: the original string that includes the macros

        now: this time object will be used for the date & time substitutions (&Y &M %D &H &N &S)

        section: this will be used for the section substitution (&X)

        device_name: this will be used for the device_name substitution (&V)

        device_type: this will be used for the device_type substitution (&T)

        ip: this will be used for the ip address substitution (&I)

        port: this will be used for the port number substitution (&P)

    Returns:
        a string will all of the macros substituted for real informtation
    """

    year = time.strftime("%Y",now)
    month = time.strftime("%m",now)
    day = time.strftime("%d",now)

    hour = time.strftime("%H",now)
    minute = time.strftime("%M",now)
    second = time.strftime("%S",now)

    a = orig.replace("&X", section).replace("&V", device_name).replace("&T", device_type).replace("&I", ip).replace("&P", str(port)).replace("&O", os.sep)
    b = a.replace("&Y", year).replace("&M", month).replace("&D", day).replace("&H", hour).replace("&N", minute).replace("&S", second)
    return b

#################################################################################################

def database_insert(cfg:configparser.ConfigParser, section:str, device_name:str, device_type:str, username:str, ip:str, port:str, config_fname:str, sha1:str, fsize:int, same_as_prev_cfg:int) -> None:
    """Insert a record into the SQLite3 database. A record is saved each time a device is scanned for changes.

    Args:
        cfg: a configparser object containing a global section with a database file name

        section: this will be used for the "section" SQL column

        device_name: this will be used for the "device_name" SQL column

        device_type: this will be used for the "device_type" SQL column

        username: this will be used for the "username" SQL column

        ip: this will be used for the "ip" SQL column

        port: this will be used for the "port" SQL column

        config_fname: this will be used for the "config_fname" SQL column

        sha1: this will be used for the "config_sha1" SQL column

        config_fsize: this will be used for the "config_fsize" SQL column

        same_as_prev_cfg: this will be used for the "same_as_prev_cfg" SQL column
                          if 1, the config was the same as the previous config, 0 if they are different

    """
    dbname = cfg["global"]["database"]
    query = "insert into files (section,device_name,device_type,username,ip,port,config_fname,config_sha1,config_fsize,same_as_prev_cfg) values( ?,?,?,?,?,?,?,?,?,? )"
    try:
        conn = sqlite3.connect(dbname)
        c = conn.cursor()
        c.execute( query, (section,device_name,device_type,username,ip,port,config_fname,sha1,fsize,same_as_prev_cfg) )
        conn.commit()
        conn.close()
    except:
        msg = "%s\n%s" % (sys.exc_info()[0],sys.exc_info()[1])
        err(2929,msg,fatal=True)

    return None

#################################################################################################

def removed_previous_identical_config(cfg:configparser.ConfigParser, section:str,device_name:str,current_fname:str,current_sha1:str) -> tuple:
    dbname = cfg["global"]["database"]
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    query = "select config_fname, config_sha1 from files where section=? and device_name=? and same_as_prev_cfg=0 order by id desc limit 1"
    c.execute( query, (section, device_name) )
    result = c.fetchone()
    conn.close()

    if result:
        old_fname, old_sha1 = result
    else:
        return (False, None)
    
    if old_sha1 == current_sha1:
        if VERBOSE_OUTPUT: print("Removing identical config file: %s" % (current_fname))
        os.remove(current_fname)
        return (True,None)
    else:
        return (False, old_fname)
    
#################################################################################################

def verify_config_settings(cfg:configparser.ConfigParser) -> bool:
    """Validate the ini config file settings and ensure it contains all the required fields

    Args:
        cfg: a configfile parser object
             a config file name is given on the command line and transformed into a configfile object

    Returns:
        True if the config is valid
    """
    
    if "database" not in cfg["global"]:
        err(4020, "Section 'global' done not contain the required 'database' definition.", fatal=True)
    if "sleep_time" not in cfg["global"]:
        err(4020, "Section 'global' done not contain the required 'sleep_time' definition.", fatal=True)
    if "server" not in cfg["smtp"]:
        err(4021, "Section 'smtp' done not contain the required 'server' definition.", fatal=True)
    if "from" not in cfg["smtp"]:
        err(4022, "Section 'smtp' done not contain the required 'from' definition.", fatal=True)
    if "to_list" not in cfg["smtp"]:
        err(4023, "Section 'smtp' done not contain the required 'to_list' definition.", fatal=True)

    dbname = cfg["global"]["database"]
    if not os.path.exists(dbname):
        err(4160, "Database file not found: %s" %(dbname), fatal=True)

    return True

#################################################################################################

def get_smtp_settings(cfg:configparser.ConfigParser) -> tuple:
    """Return the smtp settings listed in the "global" section of the config file

    Args:
        cfg: the configparser object that includes the global section

        Returns:
            a tuple including: smtp_server,smtp_from,smtp_to_list
            the smtp_to_list can contain a comma-delimited list of email recipients
    """
    smtp_server = cfg["smtp"]["server"]
    smtp_from = cfg["smtp"]["from"]
    smtp_to = cfg["smtp"]["to_list"]
    smtp_server = smtp_server.strip()
    smtp_from = smtp_from.strip()

    tmp_list = smtp_to.split(",")
    smtp_to_list = []
    for addr in tmp_list:
        smtp_to_list.append(addr.strip())

    return (smtp_server,smtp_from,smtp_to_list)

#################################################################################################

def send_email_startup(cfg:configparser.ConfigParser, authkey:str, port:int) -> None:
    """Send an initial email containing credential information

    Args:
        cfg: the configparser object that includes the global section

        authkey: a randomly gennerated UUID

        port: the UDP port number this program is listening on
    """

    subj = "[sdc] startup credentials required on: %s" % (socket.gethostname())
    smtp_server,smtp_from,smtp_to_list = get_smtp_settings(cfg)

    if VERBOSE_OUTPUT: print("Emailing startup email to: %s" % (",".join(smtp_to_list)))

    body = """Please authenticate sdc with:\r\n\r\ncd c:\\sdc\\python sdc.py -c config.ini -a\r\nAuthentication:  %s,%s,SECRET_PASSWORD_HERE\r\n""" % (authkey,port)
    msg = MIMEText(body)
    msg['Subject'] = subj
    msg['From'] = smtp_from
	
    svr = smtplib.SMTP(smtp_server)
    for to in smtp_to_list:
        #part1 = MIMEText(body, 'text')
        msg['To'] = to
        #msg.attach(part1)

        svr.sendmail(smtp_from, to, msg.as_string())
        svr.quit()

    return None

#################################################################################################

def send_email_diff(cfg:configparser.ConfigParser, section:str, device_name:str, diff_name:str) -> None:
    """Send an email containing the html diff

    Args:
        cfg: the configparser object that includes the global section

        section: the config file section the device is listed in

        device_name: the host name of the device

        diff_name: the html diff file name created by create_html_diff()
    """

    subj = "Device config change for %s::%s" % (section,device_name)
    smtp_server,smtp_from,smtp_to_list = get_smtp_settings(cfg)

    if VERBOSE_OUTPUT: print("Emailing diff to: %s" % (smtp_to_list))

    html = open(diff_name).read()
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subj
    msg['From'] = smtp_from
    
    svr = smtplib.SMTP(smtp_server)
    for to in smtp_to_list:
        part1 = MIMEText(html, 'html')
        msg['To'] = to
        msg.attach(part1)
        svr.sendmail(smtp_from, to, msg.as_string())
        svr.quit()

    return None

#################################################################################################

def process_section(now:time.struct_time, crypto:Fernet, cfg:configparser.ConfigParser, section:str) -> int:
    """This is the main function used to process each ini section. It creates an object, obj, suitable for
       the ConnectHandler function. If a diff is detected, save the diff to a file (replacing any macros.
       Update the database with the obj information.  If the config is the same as the previous config, 
       remove the current config (as it is a duplicate). Also, tell the database via the same_as_prev_cfg
       variable that the current config is a duplicate. Finally, email the diff file

    Args:
        now: a time object conataining the current date and time.  We want the same date/time used for all
             devices in any given run

        crypto: the key used to decrypt the ini password field

        cfg: the configparser object that includes a section containing devices

        section: the current ini section to process

    Returns:
        the number of differences found in this ini section
    """

    if "config_fname" not in cfg[section]:
        err(9061, "Section '%s' done not contain the required 'config_fname' definition." % (section), fatal=True)
    if "device_type" not in cfg[section]:
        err(9062, "Section '%s' done not contain the required 'device_type' definition." % (section), fatal=True)
    if "device_list" not in cfg[section]:
        err(9063, "Section '%s' done not contain the required 'device_list' definition." % (section), fatal=True)
    if "username" not in cfg[section]:
        err(9064, "Section '%s' done not contain the required 'username' definition." % (section), fatal=True)
    if "password" not in cfg[section]:
        err(9065, "Section '%s' done not contain the required 'password' definition." % (section), fatal=True)
    
    if VERBOSE_OUTPUT: print(); print("section: %s" % (cfg[section]))
    device_type = cfg[section]["device_type"]
    all_devices =cfg[section]["device_list"].split(",")

    usr = cfg[section]["username"]
    try:
        pw = crypto.decrypt(str.encode(cfg[section]["password"]))
    except:
        msg = "%s\n%s" % (sys.exc_info()[0],sys.exc_info()[1])
        err(2956,msg,fatal=True)

    port = DEFAULT_PORT if "port" not in cfg[section] else cfg[section]["port"]
    verbose_str = "False" if "verbose" not in cfg[section] else cfg[section]["verbose"]
    verbose = False if "false" == verbose_str.lower() else True
    
    total = 0
    for device_name in all_devices:
        ip = get_ip_address(device_name)
        if not ip:
            err(8011,"Unable to resolve IP address: %s" % (device_name))
            continue
        
        obj = {}
        obj["device_type"] = device_type
        obj["ip"] = ip
        obj["username"] = usr
        obj["password"] = pw
        obj["port"] = port
        verbose = False
        # FIXME this is not working correctly...
        if verbose or 1:
            # obj["verbose"] = verbose
            obj["verbose"] = True
        #if VERBOSE_OUTPUT: print("o-type:", type(obj))

        results = run_device_commands(obj,device_type)  
        if len(results):
            try:
                fname = replace_macros(cfg[section]["config_fname"], now, section, device_name, device_type, ip, port)
            except:
                msg = "%s\n%s" % (sys.exc_info()[0],sys.exc_info()[1])
                err(7803,msg,fatal=True)

            if VERBOSE_OUTPUT: print("Creating dir: %s" % os.path.dirname(fname))
            os.makedirs( os.path.dirname(fname), mode=0o777, exist_ok=True)
            if VERBOSE_OUTPUT: print("Saving file: %s" % fname)
            with open(fname,"w") as fp:
                for entry in results:
                    fp.write("%s\n" % (entry))
            sha1 = hashlib.sha1(open(fname,'rb').read()).hexdigest()
            fsize = os.path.getsize(fname)
            identical, old_fname = removed_previous_identical_config(cfg,section,device_name,fname,sha1)
            
            same_as_prev_cfg = 1 if identical else 0
            database_insert(cfg,section, device_name, device_type, usr, ip, port, fname, sha1, fsize, same_as_prev_cfg )
            if old_fname:
                diff_name = create_html_diff(old_fname, fname)
                send_email_diff(cfg, section, device_name, diff_name)

            total += 1
        #end of if stmt
        
        if VERBOSE_OUTPUT: print()
        obj["username"] = ""
        obj["password"] = ""
        del(obj)
    # end of for loop    

    usr = ""
    pw = ""
    del(usr)
    del(pw)
       
    return total
                
#################################################################################################

def get_credentials(cfg:configparser.ConfigParser) -> Fernet:
    """Create a random UUID and UDP port number and email this information.
       Listen on this UDP port for an authentication key
       Validate each password in the ini file with the given key

    Args:
        cfg: a configfile parser containing smtp email settings and at least 
             one other config section

    Returns:
        a Fernet object that will be used to decrypt ini file password entries
    """

    random.seed()
    port = random.randint(2049,65535)
    authkey = uuid.uuid4()
    authkey = str(authkey)
    send_email_startup(cfg,port,authkey)

    auth_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    auth_socket.bind(("127.0.0.1",port))   
    data, client_addr = auth_socket.recvfrom(8192)
    data = data.decode("utf-8")
    data = data.strip()
    uuid_sent,pw_sent = data.split("\t")

    if uuid_sent != authkey:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b"[5492] Incorrect authorization", client_addr)
        err(5492,"Incorrect authorization", fatal=True)

    try:
        f = Fernet(pw_sent.encode("utf-8"))
    except:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b"[2595] Incorrect authorization", client_addr)
        msg = "Incorrect password.\n\n%s\n%s" % (sys.exc_info()[0],sys.exc_info()[1])
        err(2595,msg,fatal=True)

    for section in cfg.sections():
        if section in INTERNAL_INI_SECTIONS:
            continue
        try:
            pw = f.decrypt(str.encode(cfg[section]["password"]))
        except:
            msg = "\nSection: %s\n%s\n%s" % (section,sys.exc_info()[0],sys.exc_info()[1])
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(msg.encode("UTF-8"), client_addr)
            err(8672,msg,fatal=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(b"OK", client_addr)
    return f

#################################################################################################

def send_auth_string(auth:str) -> bool:
    """Used in client mode to send the authentication string (via UDP) to another instance of 
       this script which is running in server mode (listening on the UDP port)

    Args:
        Auth: a comma-delimited string containing: UDP port,random UUID,secret password

    Return:
        True upon a successful authentication key, False otherwise

    """
    slots = auth.split(",")
    if len(slots) != 3:
        err(2596,"Incorrect password", fatal=True)
    else:
        port,uuid,pw = slots

    port = int(port)
    data = "%s\t%s" % (uuid,pw)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(bytes(data, "utf-8"), ("127.0.0.1", port))

    sock.settimeout(15)
    try:
        response = str(sock.recv(1024), "utf-8")
    except socket.timeout:
        err(5503, "No response from server -- either success or failure.\nYou should have received 'OK'.")
        return False
    except ConnectionResetError:
        err(5505,"ConnectionResetError: are you possibly using the wrong port number?", fatal=True)

    if VERBOSE_OUTPUT: print("reponse: %s" % (response))

    return True

#################################################################################################

def main() -> int:
    """Parse command line arguments
       the -c option is required; a configparse object is created from the given .ini file
       get authentication credentials, verify the config file format,
       check each ini section for device config changes
       Loop forever pausing every sleep_time seconds before checking for more changes
    """

    parser = argparse.ArgumentParser(description="Save device config over SSH", epilog="%s, version: %s (%s)" % (pgm_name,pgm_version,pgm_date))
    parser.add_argument("-c", "--confname", help="ini config file name", required=True)
    parser.add_argument("-a", "--auth", help="client-mode authentication string",action="store_true")
    args = parser.parse_args()

    if args.auth:
        auth = getpass.getpass("Authentication:")
        send_auth_string(auth)
        return 0

    if args.confname:
        confname = args.confname

    config = configparser.ConfigParser()
    if os.path.exists(confname):
        config.read(confname)
        verify_config_settings(config)
    else:
        err(8552, "Unable to open file: %s" % (confname), fatal=True)

    creds = get_credentials(config)
    sleep_fname = "sleeping.txt"

    while True:
        localtime = time.localtime()

        for section in config.sections():
            if section in INTERNAL_INI_SECTIONS:
                continue
            process_section(localtime,creds,config,section)

        sleep_time = int(config["global"]["sleep_time"])
        if sleep_time < 10: sleep_time=10
        if VERBOSE_OUTPUT: 
            print()
            print("=" * 100)
            print("Sleeping for %s minutes at: %s" % (sleep_time,time.strftime("%x %X")))

        try:
            with open(sleep_fname,mode="a",encoding="utf-8") as fp:
                fp.write("Sleeping for %s minutes at: %s\n" % (sleep_time,time.strftime("%x %X")))
        except:
            pass
            
        time.sleep(60 * sleep_time)

    # end of while loop

    return None
#################################################################################################

if __name__ == "__main__":
    main()

# End of script
