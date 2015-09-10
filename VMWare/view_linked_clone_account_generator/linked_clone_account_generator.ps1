
<#

linked_clone_account_generator.ps1
-John Taylor
Apr-19-2011

This script creates Active Directory entries for a VMWare View
linked-clone deployment.  It is geared for the use of Kiosk mode.

For each pool, an OU will be created.  This OU will contain users,
computers and one AD group.

You will need to create a tab-separated file (TSV) that contains entries
consisting of pool-name and computer name (which is also the user name).

In this environment, there is a dedicated user for each computer.
This user is not can only log into the computer, cannot change his
password, and his password never expires.

One modification for Teradici PCoIP terminals is that the user name must
start with "Custom-".  This becomes a problem for the *mandatory* LDAP
entry, sAMAccountName which is only used for pre-Windows 2000 systems.
Instead of using Custom-Username for this field, the script uses This
means that the longest user name length in the second column of the TSV
file can be 13.

For each pool, an AD group, called Pool-PoolName is created (where
PoolName) is the 1st column in the TSV file.  The user primary group
is set to this and they are deleted from the Domain Users group.

The last part of this script will create a list suitable for copying &
pasting into VM View.  These files are called pool_PoolName.txt.

#>

# modify these variables to your installation
$ifile = "vm_view_pools.tsv"
$base_ou = "OU=User Workstations,DC=example,DC=com"
$domain = "example.com"
# this is buggy...
# $view_conn_svrs = "SVRVIEW01,SVRVIEW02,SVRVIEW03,SVRVIEW04"  # comma-delimited, no spaces in between entries
$domain_users = "CN=Domain Users,OU=Security Groups,DC=example,DC=com"
$pool_user_pw = "xxxyyyzzz"



# create a dictionary containing ou/pool/computer name information, loaded from TSV file
function load_data($tsv) {
	$ou = @{}
	foreach( $line in $tsv ) {
		$slots = $line.split("`t") 
		$grp = $slots[0]
		$system = $slots[1]
		if( $ou[$grp] -eq $null ) {
			$ou[$grp] = @()
		}
		$ou[$grp] += $system
	}
	$ou
}

# IN ADU&C, you will want to manually check the "Protect From Accidental Deletion" for each OU
function create_ou($ou) {
	$debug = 0
	$myconn = "LDAP://$base_ou"

	if($debug -eq 1 ) { echo "checking OU=$ou,$base_ou" }
	$search = [System.DirectoryServices.DirectorySearcher] $myconn
	$search.Filter = "(&(name=$ou)(objectCategory=organizationalunit))"
	$result = $search.FindOne()
	if( $result ) {
		if($debug -eq 1) {echo "already exists!"}
	} else {
		if($debug -eq 1) {echo "does not exist, will create..."}

		$newou = ([ADSI] $myconn ).Create("organizationalUnit", "ou=$ou")
		$q = get-date
		$newou.Put("description","created on $q")
		$newou.SetInfo()
	}
}

# create a user in AD, assign it to the Pool-PoolName group, only log into
# the assigned VM (and view connection servers [required]), password does
# not expire, can't change password
function create_user($ou, $uname) {
	$debug = 0
	$myconn = "LDAP://OU=$ou,$base_ou"
	$q = get-date

	if($debug -eq 1) {
		echo ""
		echo "-------------------------------------------------------------------------"
		echo "create_user()..."
		echo "ou    : $ou"
		echo "uname : $uname"
		echo "myconn: $myconn"
	}

	# create the user account, SAMAccountName is mandatory
	$newusr = ([ADSI] $myconn ).Create("user", "cn=Custom-$uname")
	$newusr.Put("sAMAccountName", "Custom-$uname")  # this field must be 13 characters or less in length, if you use Teradici PCoIP firmware
	$newusr.Put("userPrincipalName", "Custom-$uname"+ "@" + "$domain")
	$newusr.put("description", "VMWare View Linked Clone Account, created on $q")
	# this seems buggy...
	#$newusr.put("userWorkstations", $uname + "," + $view_conn_svrs) # locks the user account so that it can only log onto this computer
	$newusr.SetInfo()

	# enable the user account & set the password
	$newusr = [ADSI] "LDAP://cn=Custom-$uname,OU=$ou,$base_ou"
	$newusr.psbase.invokeset("AccountDisabled", "False")
	$newusr.psbase.CommitChanges()
	$newusr.SetInfo()
	$newusr.SetPassword( $pool_user_pw )
	$newusr.SetInfo()

	# set account to never expire
	# http://powershell.com/cs/forums/p/2419/3270.aspx
	# http://www.powershellcommunity.org/Forums/tabid/54/aft/1361/Default.aspx
	$newusr = [ADSI] "LDAP://cn=Custom-$uname,OU=$ou,$base_ou"
	$current = [int]($newusr.userAccountControl.ToString())
	$uac =  $current -bor 65536
	$newusr.put("userAccountControl", 65536)
	$newusr.SetInfo()

	# set "user cannot change password"
	# set account so that user cannot change password
	# http://poshcode.org/682

	$Everyone      = [System.Security.Principal.SecurityIdentifier]'S-1-1-0'
	$self          = [System.Security.Principal.SecurityIdentifier]'S-1-5-10'
	$SelfDeny      = new-object System.DirectoryServices.ActiveDirectoryAccessRule ( $self,'ExtendedRight','Deny',      [guid] 'ab721a53-1e2f-11d0-9819-00aa0040529b')
	$SelfAllow     = new-object System.DirectoryServices.ActiveDirectoryAccessRule ( $self,'ExtendedRight','Allow',     [guid] 'ab721a53-1e2f-11d0-9819-00aa0040529b')
	$EveryoneDeny  = new-object System.DirectoryServices.ActiveDirectoryAccessRule ( $Everyone,'ExtendedRight','Deny',  [guid] 'ab721a53-1e2f-11d0-9819-00aa0040529b')
	$EveryOneAllow = new-object System.DirectoryServices.ActiveDirectoryAccessRule ( $Everyone,'ExtendedRight','Allow', [guid] 'ab721a53-1e2f-11d0-9819-00aa0040529b')

	$newusr.psbase.get_ObjectSecurity().AddAccessRule($selfDeny)
	$newusr.psbase.get_ObjectSecurity().AddAccessRule($EveryoneDeny)
	$newusr.psbase.CommitChanges()
	$newusr.SetInfo()
	
	if($debug -eq 1) {
		echo ""
		echo ""
	}
}

# create a group in AD, starting with Pool-
function create_group($ou) {
	$debug = 0
	$myconn = "LDAP://OU=$ou,$base_ou"
	$q = get-date

	if($debug -eq 1) {
		echo ""
		echo "-------------------------------------------------------------------------"
		echo "creating group: Pool-$ou"
	}

	$search = [System.DirectoryServices.DirectorySearcher] $base_ou
	$search.Filter = "(&(name=Pool-$ou)(objectCategory=group))"
	$result = $search.FindOne()
	if( $result ) {
		if($debug -eq 1) {echo "already exists!"}
	} else {
		if($debug -eq 1) {echo "does not exist, will create..."}
		$newgrp = ([ADSI] $myconn ).Create("group", "cn=Pool-$ou")
		$newgrp.put("sAMAccountName", "Pool-$ou" )
		$newgrp.put("description", "VMWare View Pool for $ou" + ", created on $q"  )
		$newgrp.SetInfo()
	}

	if($debug -eq 1) {
		echo ""
		echo ""
	}
}

function add_user_to_group($ou, $usr) {
	$debug = 0
	$myconn = "LDAP://CN=Pool-$ou,OU=$ou,$base_ou"
	$myusr  = "LDAP://CN=Custom-$usr,OU=$ou,$base_ou"

	if($debug -eq 1 ) {
		echo "adding user: $usr to $myconn"
		echo "myusr :      $myusr"
	}

	$grp = [ADSI] $myconn
	$grp.add($myusr)
	$grp.SetInfo()

	if($debug -eq 1) {
		echo ""
		echo ""
	}
}

function remove_user_from_group($ou, $usr) {
	$debug = 0
	$myusr  = "LDAP://CN=Custom-$usr,OU=$ou,$base_ou"
	$mydu   = "LDAP://$domain_users"

	if($debug -eq 1 ) {
		echo ""
		echo "-------------------------------------------------------------------------"
		echo "myusr :      $myusr"
		echo "mydu  :      $mydu"
	}
	$grp = [ADSI] $mydu
	$grp.remove($myusr)
	$grp.SetInfo()

	if($debug -eq 1) {
		echo ""
		echo ""
	}
}
	
function set_primary_user_group($ou, $usr) {
	$debug = 0
	$myconn = "LDAP://CN=Pool-$ou,OU=$ou,$base_ou"
	$myusr  = "LDAP://CN=Custom-$usr,OU=$ou,$base_ou"
	$mygrp  = "LDAP://CN=Pool-$ou,OU=$ou,$base_ou"

	if($debug -eq 1 ) {
		echo ""
		echo "-------------------------------------------------------------------------"
		echo "myconn: $myconn"
		echo "myusr : $myusr"
		echo "mygrp : $mygrp"
		echo ""
	}

	$grp = [ADSI] $mygrp
	$grp.GetInfoEx(@("primaryGroupToken"), 0)  
	$token = $grp.Get("primaryGroupToken")  

	$u = [ADSI] $myusr
	$u.Put("primaryGroupId", $token)
	$u.setinfo()

	if($debug -eq 1) {
		echo ""
		echo ""
	}
}


#######################################
##
## Main
##
#######################################

$data = gc $ifile
$pools = load_data($data)

echo ""
echo ""
echo "-------------------------------------------"
echo "  Creating OUs & Pool Groups (if needed)"
echo "-------------------------------------------"
foreach ($ou in $pools.keys) {
	echo "    $ou"
	create_ou($ou)
	create_group $ou
}
start-sleep -m 1000

echo ""
echo ""
echo "-----------------------------------"
echo "  Creating Pool Users"
echo "-----------------------------------"

foreach ($ou in $pools.keys) {
	foreach($usr in $pools[$ou]){
		echo "$ou :: $usr"
		create_user $ou $usr
		start-sleep -m 4500
		add_user_to_group $ou $usr
		set_primary_user_group $ou $usr
		remove_user_from_group $ou $usr
		start-sleep -m 1500
	}
}


echo ""
echo ""
echo "-----------------------------------"
echo "Creating VMWare View Creation Files"
echo "Named: pool_*.txt"
echo "-----------------------------------"

foreach ($ou in $pools.keys) {
	$name = "pool_$ou.txt"
	echo "    $name"
	$file = New-Item -type file "pool_$ou.txt" -force
	foreach($usr in $pools[$ou]){
		add-content $file "$usr,$domain\Custom-$usr"
	}
}




echo ""
echo ""
