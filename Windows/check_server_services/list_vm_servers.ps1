#
# list_vm_servers.ps1
# -John Taylor
# Jan-3-2012
#
# Outputs VMs attached to a vCenter server as a
# powershell array.

# You need VMWare PowerCLI installed.

# Don't redirect to a file as PS outputs to Unicode.
# Instead, copy and paste with the mouse.

$vctr = "vcenter.example.com"
$conn = connect-viserver -Server $vctr

$servers = @()
$mylist = Get-VM |? {$_.PowerState -eq "PoweredOn"}
foreach( $obj in $mylist ) {
	$tmp = [String] $obj.Name
	$servers += $tmp.ToUpper()
}

$servers = $servers | sort-object

$max = $servers.length - 1
$curr = 1

$answer = "`$ping_list += @( "
foreach( $str in $servers) {
	if( $curr -le $max ) {
		$answer += "`"$str`", "
	} else {
		$answer += "`"$str`""
	}
	$curr += 1
}

$answer += " )"
$answer
