I have written two VBS scripts to help our VMWare View Teradici PCoIP zero-client environment.  

The first one, **adm_printer_check.vbs** should be run by the SYSTEM
account and started with the Task Scheduler with a trigger of "at
Startup". It "cleans up" Win XP's printers section by deleting all
of the copy 1, copy 2, etc. printers and renaming the online printer
to a more sane name.

The second script, **printer_check.vbs**, is a lot more ambitious.
In our experience, USB printers attached to a terminal will
mysteriously get disconnected (sporadically) and then reconnected.
This happens with our Dell laser printers and our Dymo label printers.
When the printer gets "reconnected", Windows XP believes this is a
brand new printer that needs to be installed rather than the same
printer simply being "unplugged" and the "plugged in" again. These
old, stale printers show up as "Dell Printer (Copy 1)" [or Copy 2,
etc.] and are grayed out because they are offline.

This script is launched from our main network script. It runs forever
in the background.  Every two minutes, the script will wake up and
try to reset the default printer, if needed. The criteria for what
is considered to be the default printer is simple:

* The printer name starts with Dell (as opposed to Dymo, MidMark, etc.) 
* The printer is online

If the script determines this is the current OS's settings, it will
pause for 2 minutes and then check again.  If the script determines
that the default printer is either offline or does not start with
"Dell", then the script will change the default printer to one that
meets the above criteria.  This change is logged on our file server.
If the script cannot find a suitable printer that matches the above
criteria, then this is also logged and no changes to the default
printer is made.  This could happen if all printers happen to be
offline or if no Dell printers are installed.

If your terminals use network printers and users switch from terminal
to terminal without logging off and then back on, then the closet
printer may not be the default printer any more.  Create a CSV file
with the first column containing the dns name of the terminal
(recommended) or ip address (not recommended since terminals may
change IP addresses).  The second column will contain the network
printer path.  This script will wake up every 30 seconds and check
the VM's location to see if it has been connected to a different
terminal.  If it has, it will change the default printer.  One thing
to note is that the printer already must be installed.  Right now,
the feature does not do any logging.

If some of your VMs only use network printers and users are not
moving from place to place, which could be the case for an exam
room or computer lab, then place these VM names in the skip_list.txt
file.

