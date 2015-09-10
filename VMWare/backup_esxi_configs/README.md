To backup the configs of the ESXi servers:
 
1.	Log into your backup server that has PowerCLI installed

2.	Start - > All Programs -> Vmware -> VMWare vSphere PowerCLI -> Vmware vSphere PowerCLI (right click to Run as administrator)

3.	cd c:\bin  (or the location of your script)

4.	.\backup_esxi_configs.ps1 V:\net_backups\YYYYMMDD [change this to current date]

5.	You should see this output from the script: 

6.	[Screen Shot](https://github.com/jftuga/VMWare/raw/master/backup_esxi_configs/screenshot.png)

7.	To restore a ESXi server, read the comments from within the backup_esxi_configs.ps1 script.

8.	If you get a failure of "(404) Not Found.", you will need to first create a scratch directory on the ESXi server itself:

	a.	cd /

	b.	Example: ln -s /vmfs/volumes/4c35a3d1-a835de9e-1c28-00219ba27a93/.locker scratch

	c.	See also: http://communities.vmware.com/thread/307919

