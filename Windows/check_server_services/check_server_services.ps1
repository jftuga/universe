#
# check_server_services.ps1
# -John Taylor
# Jun-23-2011
# Jun-29-2011 - added code to start a non-running service
# Jul-14-2011 - added code to ping DMZ servers, since those services can't be checked
# Jan-03-2012 - separated physical & virtual servers by using list_vm_servers.ps1 and add count to ping output
# Feb-13-2017 - added low disk space checking
#
#
# This script is used in conjunction with the unique_server_services.ps1
# script.  It runs through a list of servers & services and will send an
# email alerting you to any services that are not running.  It will also
# send an email to report that all services are OK.  For services that
# are not running, it will attempt to restart them.  Low disk space
# is checked for on any systems where a service is verified.  Either less 
# than 10 GB or less than 7% will trigger a low disk space warning.

$warningPreference = "Continue"
$errorActionPreference = "Continue"

# change the $ping_list and $fname variables accordingly, include all of your servers, not just DMZ servers
# optional: use list_vm_servers.ps1 to append VMs to $ping_list
$ping_list = @( "ad1", "ad2", "exchange", "www", "sql1" )
$fname = "services.tsv"

# Adapted from: https://binarynature.blogspot.com/2010/04/powershell-version-of-df-command.html
function Get-DiskFree
{
    [CmdletBinding()]
    param 
    (
        [Parameter(Position=0,
                   ValueFromPipeline=$true,
                   ValueFromPipelineByPropertyName=$true)]
        [Alias('hostname')]
        [Alias('cn')]
        [string[]]$ComputerName = $env:COMPUTERNAME,
        
        [Parameter(Position=1,
                   Mandatory=$false)]
        [Alias('runas')]
        [System.Management.Automation.Credential()]$Credential =
        [System.Management.Automation.PSCredential]::Empty,
        
        [Parameter(Position=2)]
        [switch]$Format
    )
    
    BEGIN
    {
        function Get-Status($size, $free)
        {

            if($free -le (10 * 1024 * 1024 * 1024)) {
                return "WARNING SIZE"
            }

            #Write-Warning "size: $size _" 
            #Write-Warning "free: $free _" 
            #Write-Warning "percent: $percent" 
            $percent = 100 * ($free / $size)
            if($percent -le 7.00) {
                return "WARNING PERCENTAGE"
            }

            return "OK"
        }
        function Format-HumanReadable 
        {
            param ($size)
            switch ($size) 
            {
                {$_ -ge 1PB}{"{0:#.#'P'}" -f ($size / 1PB); break}
                {$_ -ge 1TB}{"{0:#.#'T'}" -f ($size / 1TB); break}
                {$_ -ge 1GB}{"{0:#.#'G'}" -f ($size / 1GB); break}
                {$_ -ge 1MB}{"{0:#.#'M'}" -f ($size / 1MB); break}
                {$_ -ge 1KB}{"{0:#'K'}" -f ($size / 1KB); break}
                default {"{0}" -f ($size) + "B"}
            }
        }
        
        $wmiq = 'SELECT * FROM Win32_LogicalDisk WHERE Size != Null AND DriveType >= 2'
    }
    
    PROCESS
    {
        $today = Get-Date -format yyyyMMdd
        foreach ($computer in $ComputerName)
        {
            try
            {
                if ($computer -eq $env:COMPUTERNAME)
                {
                    $disks = Get-WmiObject -Query $wmiq `
                             -ComputerName $computer -ErrorAction Stop
                }
                else
                {
                    $disks = Get-WmiObject -Query $wmiq `
                             -ComputerName $computer -Credential $Credential `
                             -ErrorAction Stop
                }

                Write-Host "Disk Space Check: $computer"            

                # Create array for $disk objects and then populate
                $diskarray = @()
                $disks | ForEach-Object { $diskarray += $_ }
                
                $diskarray | Select-Object `
                    @{n='Date';e={$today}},
                    @{n='ComputerName';e={$_.SystemName}}, 
                    @{n='Vol';e={$_.DeviceID}},
                    @{n='Status';e={Get-Status $_.Size $_.FreeSpace}},
                    @{n='HumanSize';e={Format-HumanReadable $_.Size}},
                    @{n='HumanUsed';e={Format-HumanReadable (($_.Size)-($_.FreeSpace))}},
                    @{n='HumanFree';e={Format-HumanReadable $_.FreeSpace}},
                    @{n='PercentUsed';e={[int](((($_.Size)-($_.FreeSpace)) / ($_.Size) * 100))}},
                    @{n='PercentFree';e={[int](((($_.FreeSpace)) / ($_.Size) * 100))}},
                    @{n='ActualSize';e={$_.Size}},
                    @{n='ActualUsed';e={($_.Size) - ($_.FreeSpace)}},
                    @{n='ActualFree';e={$_.FreeSpace}},
                    @{n='FS';e={$_.FileSystem}},
                    @{n='Type';e={$_.Description}}
            }
            catch 
            {
                # Check for common DCOM errors and display "friendly" output
                switch ($_)
                {
                    { $_.Exception.ErrorCode -eq 0x800706ba } `
                        { $err = 'Unavailable (Host Offline or Firewall)'; 
                            break; }
                    { $_.CategoryInfo.Reason -eq 'UnauthorizedAccessException' } `
                        { $err = 'Access denied (Check User Permissions)'; 
                            break; }
                    default { $err = $_.Exception.Message }
                }
                Write-Warning "$computer - $err"
            } 
        }
    }
    
    END {}
}

function ping-ip($ip) {  
	trap {$false; continue}
	$timeout = 1000
	$object = New-Object system.Net.NetworkInformation.Ping
	(($object.Send($ip, $timeout)).Status -eq 'Success')
}


$not_running = @()
$collection = @(Import-Csv -Delimiter `t $fname)
$disk_space_servers =New-Object System.Collections.Generic.List[System.Object]

$good = 0
$bad = 0
foreach( $i in $collection) {
	$svr = $i.Server_Name
	$name = $i.Short_Name
	$desc = $i.Service_Name
	write-host "$svr `t $name"
    if( -not $disk_space_servers.Contains($svr) ) {
        $disk_space_servers.Add($svr)
    }

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

# initialize output file 
$q = get-date
$output = "c:\temp\check_servers_email_message.txt"
$file = New-Item -type file $output -force
$success_disk_check = $true

# run disk space check
$today = Get-Date -format yyyyMMdd
$ym = Get-Date -format "yyyy\\MM"
$fname = "disk_space--$today.csv"
$fname_disk_space = "disk_space\$ym"
$fname_disk_space = (Get-Item -Path ".\" -Verbose).FullName + $fname_disk_space
If (-not(Test-Path -Path $fname_disk_space)) {
    mkdir $fname_disk_space
    write-host ""
}
$fname_disk_space += "\" + $fname
$disk_space_servers.ToArray() | Get-DiskFree | Export-Csv -Path $fname_disk_space -NoTypeInformation
write-host "fname_disk_space: $fname_disk_space"
$warn = Select-String -Path $fname_disk_space -Pattern WARNING
if( $warn.length ) {
    $success_disk_check = $false
    add-content $output "Low Disk Warning(s):"
    add-content $output ""
    add-content $output "Date `t`t Computer Name `t Volume `t Status `t Human Size `t Human Used `t Human Free `t Percent Used `t Percent Free"
    #add-content $output "---- `t`t ------------- `t ------ `t ------ `t ---------- `t ---------- `t ---------- `t ------------ `t ------------"
    for( $i=0; $i -le $warn.length; $i++) {
        $x = ([string] $warn[$i]).Split('","')
        $human_size_tabs = if($x[13].length -le 5 ) {"`t`t"} else {"`t"}
        $human_used_tabs = if($x[16].length -le 5 ) {"`t`t"} else {"`t"}
        $human_free_tabs = if($x[19].length -le 5 ) {"`t`t`t"} else {"`t`t"}
        $warn_type = ([string] $x[10]).Replace("WARNING ","")
        add-content $output "$($x[1]) `t $($x[4]) `t`t $($x[7]) `t`t $warn_type `t $($x[13]) $human_size_tabs $($x[16]) $human_used_tabs $($x[19]) $human_free_tabs $($x[22]) `t $($x[25])"
    }
    add-content $output ""
    add-content $output ""
} else {
    $svr_count = $disk_space_servers.ToArray().length
    add-content $output "There are no systems with low disk space, $svr_count were checked."
    add-content $output ""
    add-content $output ""
}

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
	$marker = ""
	$result = ping-ip $i
	if( $result -eq $false ) {
		$success = $false
		$marker = "  <<<------------------"
	}
	add-content $output "$result `t $i `t $marker"
}
add-content $output ""
add-content $output ""


$emailFrom = "support@example.com"
#$emailTo = ""
if( $success -eq $false ) {
	$subject = "WARNING: Status of services"
} else {
	$subject = "SUCCESS: Status of services"
}

if( $success_disk_check -eq $false ) {
    $subject = "WARNING: Status of services"
} else {
    $subject_disk_check = "SUCCESS: Status of services"
}


$body = ""
$temp = get-content $output
foreach( $line in $temp ) {
	$body += "$line `r`n"
}

$smtpServer = "smtp.example.com"
$smtp = new-object Net.Mail.SmtpClient($smtpServer)
$smtp.Send($emailFrom, "support@example.com",  $subject, $body)

# end of script
