
# vsphere_ssh.ps1
# -John Taylor
# Jan-17-2012

# Give two options on the command: (1) vcenter server or an ESXi host (2) 'start' or 'stop'
# This will start/stop all esxi hosts if you give it a vcenter server
# Adapted from http://www.virtu-al.net/2010/11/23/enabling-esx-ssh-via-powercli/

$service = "TSM-SSH"

$cmd = $args[1]
if( $cmd -ne "start" -and $cmd -ne "stop" ) {
	""
	"Usage: vpshere_ssh.ps1 [vcenter or esxi host] [start|stop]"
	""
	"Give two options on the command:"
	"  1) vcenter server (will then run on all managed hosts) or an ESXi host"
	"  2) 'start' or 'stop'"
	""
	exit
}

$conn = Connect-VIServer $args[0]
if( $conn -eq $null ) {
	""
	"Can not connect to: " + $args[0]
	""
	exit
}
get-vmhost | foreach { 
	$_.name
	$ssh = "$cmd" + '-VMHostService -confirm:$false -HostService ($_ | Get-VMHostService | Where { $_.Key -eq "$service"} )'
	$result = invoke-expression $ssh

}
Disconnect-VIServer -server $conn -confirm:$false
