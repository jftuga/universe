The goal of this project is to build a transparent network bridge that resides in between the Internet and your firewall (not inside of your firewall). This bridge will block network packets based on geographic origin and/or destination.
 
You will need a server with 3 network interfaces. Two will be used to pass Internet traffic and the third interface will be used for management of the server itself via SSH. Only this third interface will have an IP address. Traffic passing through the two bridged interfaces will be transparent and therefore will not need an IP address. No changes to any network addresses, netmasks, gateways, etc. will be necessary.
 
The document assumes you have already installed OpenBSD 5.0, installed all of the errata patches, and the root password has been set.

> ______________________________________________

**Step 1 – Network Setup**

Assign the server a hostname:

    /etc/myname
    bridge.example.com

Assign the server a gateway which will only be used on the 3rd interface:

    /etc/mygate
    192.168.1.1

Add internal DNS servers:

    /etc/resolv.conf
    lookup file bind
    nameserver 192.168.1.21
    nameserver 192.168.1.22

Run “ifconfig –a” to identify the 3 network interfaces that you will be using. 

Ex: em0, em1 and alc0

* em0 will be connected to the firewall
* em1 will be connected to the Internet
* alc0 will be the management interface

Create files in /etc for the 3 interfaces: hostname.alc0, hostname.em0, hostname.em1

	/etc/hostname.alc0
	inet 192.168.1.2 255.255.255.0 NONE description mgmt_port

	/etc/hostname.em0
	description to_firewall
	up

	/etc/hostname.em1
	description to_internet
	up

Create a bridge between the two interfaces

	/etc/hostname.bridge0
	add em0
	add em1
	blocknonip em1
	maxaddr 800
	fwddelay 4
	description block_filter
	up

Block everything except SSH:

	/etc/hosts.deny
	ALL:ALL
	 
	/etc/hosts.allow
	sshd: 192.168.1.0/24
 
Your /etc/pf.conf should look something like this:

	set skip on lo
 
	# interface 'em0' should be connected to the your firewall
	# interface 'em1' should be connected to the internet demarcation switch
	 
	to_internet="em1"
	 
	# use only if you want to block IPv6
	block in quick inet6
	 
	table <block_filter> persist file "/etc/pf.block.txt"
	block quick on $to_internet from <block_filter> to any

All of the networking has now been configured. Make sure you can SSH into your server from your management network.

> ______________________________________________
 
**Step 2 – blocking configuration**

You will need these two scripts from [github](https://github.com/jftuga/Networking/tree/master/OpenBSD_Geographic_Based_Packet_Filter):

	/root/block/Get_Countries.sh 
 
	/root/block/Create_PF_Table.sh 


> ______________________________________________

**Step 3 – Activate Rules**

Edit & run Get_Countries.sh to include the countries that you wish to block. You will need to enter in each 2 letter country code in all caps. This script will download files and they will contain network ip blocks for each country.
 
Run Create_PF_Table.sh. This will create a new file, /etc/block.txt. It will contain all of the countries that you want to block. The /etc/pf.conf files uses the file.
 
To flush the current rules, run this command:

	/sbin/pfctl -F all
 
To load rules, run this command:

	/sbin/pfctl -f /etc/pf.conf ; /sbin/pfctl –e
 
To view all rules, run this command:

	/sbin/pfctl -v -t block_filter -T show | less

> ______________________________________________
 
**Step 4 - Test Rules**

Try going to a web site in one of these countries. It should be blocked. If so, you have successfully installed a geographic based packet filter.

