#!/usr/bin/env python3

"""
plink-shim.py
-John Taylor
Dec-16-2015

Send ssh command(s) to a remote host via PuTTY's Plink

Instructions
------------
1) create a new PuTTY SSH session entry

2) configure a PuTTY entry to use public key authentication with PuttyGen
        see also: http://the.earth.li/~sgtatham/putty/0.66/htmldoc/Chapter8.html
        With PuttyGen, copy the "Public key for parting into OpenSSH authorized_keys file" to the clipboard
        On Linux: Paste & append to ~/.ssh/authorized_keys and then chmod 600 ~/.ssh/authorized_keys

3) set this: PuTTY -> Connection -> Data -> Auto-login username
4) set this: PuTTY -> Connection -> SSH -> Auth -> Private key file for authentication
5) to test: plink.exe your_server ls -l  (if there is no output, the configuration is incorrect)

Examples
---------
to use the local host's findstr:
plink-shim.py -s ubuntu du -k | findstr /i ".Ssh"

to use the remote host's grep (note the carrot character):
plink-shim.py -s ubuntu du -k ^| grep ".ssh"

usings multiple pipes:
plink-shim.py -s ubuntu "df | awk '{print $2}' | grep -v 1K-blocks"
same command without double-quotes
plink-shim.py -s ubuntu df ^| awk '{print $2}' ^| grep -v 1K-blocks

running commands for a HP Procurve switch, using plink.exe:
plink.exe -ssh -pw xxx procurve1 < cmds.txt > output.txt
(plink.exe -m file does not seem to work for these switches)
"""

#############################################################################

import sys, asyncio, argparse, getpass, shutil
from asyncio.subprocess import PIPE, STDOUT

pgm_name = "plink-shim.py"
pgm_version = "1.02"
pgm_date = "Dec-18-2015 9:45"

# this needs to be in the PATH
plink_cmd = "plink.exe" 

# how long to wait for a command to complete before timing out
# this can be a sub-second value such as 5.25
default_remote_cmd_timeout = 90

#############################################################################

# convert unicode characters to something that can be displayed
def safe_print(data):
    # can also use 'replace' instead of 'ignore' for errors= parameter
    print( str(data).encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding) )

#############################################################################

# convert raw data read from the process's output into an array of strings
def process_read(raw):
    data = raw.decode("utf-8")
    all_lines = data.splitlines()
    for line in all_lines:
        safe_print(line)    

#############################################################################

# adapted from: http://stackoverflow.com/a/34114767/452281
async def run_command(*args, timeout=None):
    # start child process
    # NOTE: universal_newlines parameter is not supported
    process = await asyncio.create_subprocess_exec(*args, stdout=PIPE, stderr=STDOUT)

    # read line (sequence of bytes ending with b'\n') asynchronously
    while True:
        try:
            data  = await asyncio.wait_for(process.stdout.read(), timeout)
        except asyncio.TimeoutError:
            print("Timeout occurred after %s seconds." % (timeout))
        else:
            if not data: # EOF
                break
            elif process_read(data): 
                continue # while some criterium is satisfied
        process.kill() # timeout or some criterium is not satisfied
        
        break
    return await process.wait() # wait for the child process to exit

#############################################################################

# parse command line arguments and perform some initial error checking
def main():
    parser = argparse.ArgumentParser(description="%s: send ssh command to remote host via PuTTY's Plink" %(pgm_name), epilog="version: %s (%s)" % (pgm_version,pgm_date))
    parser.add_argument("-s", "--session", help="PuTTY session name or remoter server name",  required=True)
    parser.add_argument("-P", "--port", help="remote server port")
    parser.add_argument("remote_cmd", nargs=argparse.REMAINDER, help="example: %s -s server1 df -h" % (pgm_name))
    parser.add_argument("-f", "--file", help="read remote command(s) from file")      
    parser.add_argument("-u", "--user", help="remote username")
    pw_group = parser.add_mutually_exclusive_group()
    pw_group.add_argument("-p", "--passwd", help="remote password")
    pw_group.add_argument("-a", "--ask", help="interactively prompt for password", action="store_true")
    parser.add_argument("-t", "--timeout", help="command timeout in seconds, default: %s" % (default_remote_cmd_timeout))
    
    args = parser.parse_args()
    if args.remote_cmd and args.file:
    	parser.error("argument -f/--file: not allowed with argument remote_cmd")
    	return 1

    if not shutil.which(plink_cmd):
    	print()
    	print("Error: file not on PATH, %s" %(plink_cmd)); 
    	print("       download Plink from http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html")
    	print()
    	return 1

    remote_cmd_line = " ".join(args.remote_cmd)
    remote_session = args.session
    remote_user = args.user if args.user else None
    remote_pass = args.passwd if args.passwd else None
    remote_port = args.port if args.port else None
    remote_cmd_timeout = float(args.timeout) if args.timeout else float(default_remote_cmd_timeout)
    remote_cmd_file = args.file if args.file else None

    group = [plink_cmd, remote_session, "-batch", "-ssh"]
    if args.ask:
    	remote_pass = getpass.getpass()
    if args.user: 
    	group.append("-l")
    	group.append(remote_user)
    if args.passwd or args.ask: 
    	group.append("-pw")
    	group.append(remote_pass)
    if args.port:
    	group.append("-P")
    	group.append(remote_port)
    if args.file:
    	group.append("-m")
    	group.append(remote_cmd_file)
    else:
    	group.append(remote_cmd_line)

    ################################################################################

    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop() # for subprocess' pipes on Windows
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    returncode = loop.run_until_complete(run_command(*group, timeout=remote_cmd_timeout))
    remote_cmd_line = remote_user = remote_pass = remote_port = remote_session = group = None
    loop.close()

    return 0

#############################################################################

# program executin begins here
if "__main__" == __name__:
    sys.exit( main() )

# end of script
