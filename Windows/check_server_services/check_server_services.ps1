#
# check_server_services.ps1
# -John Taylor
# Jun-23-2011
# Jun-29-2011 - added code to start a non-running service
# Jul-14-2011 - added code to ping DMZ servers, since those services
#               can't be checked
#
#
# This script is used in conjunction with the unique_server_services.ps1
# script.  It runs through a list of servers & services and will send an
# email alerting you to any services that are not running.  It will also
# send an email to report that all services are OK.  For services that
# are not running, it will attempt to restart them.

$warningPreference = "Continue"
$errorActionPreference = "Continue"

# change the $ping_list and $fname variables accordingly, include all of your servers, not just DMZ servers
# optional: use list_vm_servers.ps1 to append VMs to $ping_list
$ping_list = @( "ad1", "ad2", "exchange", "www", "sql1" )
$fname = "services.tsv"

function ping-ip($ip) {  
	trap {$false; continue}
	$timeout = 1000
	$object = New-Object system.Net.NetworkInformation.Ping
	(($object.Send($ip, $timeout)).Status -eq 'Success')
}


$not_running = @()
$collection = @(Import-Csv -Delimiter `t $fname)

$good = 0
$bad = 0
foreach( $i in $collection) {
	$svr = $i.Server_Name
	$name = $i.Short_Name
	$desc = $i.Service_Name

	$result = $null
	$result = gwmi win32_service -ComputerName $svr | Where-Object { $_.Name -eq $name }
	if ( $result.State -ne "Running" ) {
		$bad += 1
		$line = "$svr `t $name `t $desc"
		$not_running += $line

		# try to start the service...
		$restart = $null
		$restart = (gwmi -computername $svr -class win32_service | Where-Object { $_.Name -eq "$name" }).startservice()
		if ($restart -ne $null -and $restart.ReturnValue -eq 0 ) {
			$code = "successfully restarted"
			$bad -= 1
			$good += 1
		} else {
			$code = "could not restart service"
		}
		$line = "trying to restart $name on server $svr --> return-value: $code"
		$not_running += $line
		$not_running += ""
	} else {
		$good += 1
	}
}

$q = get-date
$output = "c:\temp\not_running.txt"
$file = New-Item -type file $output -force
if( $not_running.Length -gt 0 ) {
	$success = $false
	add-content $output "Services not running on: $q"
	add-content $output ""
	add-content $output "Server `t Name `t Description"
	add-content $output "-------- `t -------- `t ----------------------------"

	foreach($i in $not_running) {
		#write-host $i
		add-content $output $i
	}
} else {
	$success = $true
	add-content $output "All services are currently running on: $q"
	add-content $output " `r`n"
}

$num = $ping_list.Length
add-content $output ""
add-content $output "$good services are running, $bad services are not running."
add-content $output "Run the script by hand for more details on the services not running."
add-content $output ""
add-content $output ""
add-content $output "Ping Results ( $num servers )"
add-content $output "--------------------------------"

foreach($i in $ping_list) {
	$result = ping-ip $i
	if( $result -eq $false ) {
		$success = $false
	}
	add-content $output "$result `t $i"
}
add-content $output ""
add-content $output ""


$emailFrom = "InformationTechnologyDepartment@uhs.uga.edu"
#$emailTo = ""
if( $success -eq $false ) {
	$subject = "WARNING: Status of services"
} else {
	$subject = "SUCCESS: Status of services"
}

$body = ""
$temp = get-content $output
foreach( $line in $temp ) {
	$body += "$line `r`n"
}

$smtpServer = "smtp.uhs.uga.edu"
$smtp = new-object Net.Mail.SmtpClient($smtpServer)
$smtp.Send($emailFrom, "InformationTechnologyDepartment@uhs.uga.edu",  $subject, $body)

# end of script
