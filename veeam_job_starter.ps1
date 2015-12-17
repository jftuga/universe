<#

veeam_job_starter.ps1
-John Taylor
Dec-17-2015
version 1.00

Start a Veeam backup job only if a VM's "Disk Write Bytes/sec" is low.
This prevents a large snapshot from being created on a busy VM by not starting the Veeam backup job.
The Veeam job may only contain one VM.

This script is not bullet proof.  It a VM starts writing a lot of data after the Veeam job has started,
then a large snapshot will still be created.

#>

# how many samples to take on the VM
$sample_count = 1

# time to wait in between each Get-Counter operation
$sample_interval_seconds = 2

# time to wait before checking the next veeam job in $veeam_job_names
$job_interval_seconds = 10

# threshold for "disk write bytes per sec"
# if the sample average is above this, then no backup will be performed
# each megabyte is 1024 * 1024
$cutoff = 2 * 1024 * 1024

# add Veeam jobs here...
$veeam_job_names = @("server1", "server2", "server3")

#########################################################################################################

# return True if "Run As Administrator" trust level is true
function is_admin  {  
    if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))  {  
        return $False
    }  
    else {  
        return $True
    }  
}

# return True is $cmdname is a valid, installed powershell cmdlet
function Check-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# return True if the average disk write speed is less than $cutoff
function check_server_write_speed($svr) {
	$total = 0
	for($i=0; $i -lt $sample_count; $i++) {
		$query = "\\" + $svr + "\PhysicalDisk(_total)\Disk Write Bytes/sec"
		$tmp = Get-Counter $query
        if( -not $tmp ) {
            write-host("Failed. Unable to determine write speed for {0}" -f $svr)
            return $False
        }
		$write_speed = $tmp.CounterSamples.CookedValue
        $write_speed = [int] $write_speed
        write-host("{0}`tsample`t{1:N0}" -f $svr,$write_speed )
        $total +=  $write_speed
        if( ($i+1) -lt $sample_count) {
            start-sleep $sample_interval_seconds
        }

	}
    $average = $total / $sample_count
    $average = [int] $average
    write-host("{0}`taverage`t{1:N0}" -f $svr,$average )

    if($average -ge $cutoff) {
        write-host("Failed. Average write speed of {0:N0} exceeded cutoff limit of {1:N0}" -f $average,$cutoff)
        return $False
    } elseif ($average -lt 1) {
         write-host("Failed. Average write speed of {0} is zero. Sampling may have failed." -f $svr)
        return $False
    } else {
        write-host("Success. Average write speed of {0:N0} is under cutoff limit of {1:N0}" -f $average,$cutoff)
        return $True
    }
}

# interrogate a Veeam job and return the VM it is backing up 
function get_vm_from_job($job_name) {
    $job_object = Get-VBRJob -Name $job_name
    if( -not $job_object ) {
        Write-Host("")
        Write-Host("Error: Veeam backup job does not exist: {0}" -f $job_name)
        Write-Host("")
        exit
    }

    if( $job_object.GetObjectsInJob().length -ne 1) {
        Write-Host("")
        Write-Host("Error: Multiple VMs exist in job: {0}" -f $job_object.Name)
        Write-Host("       Low 'Disk Write Bytes/sec' can not me measured if a job contains more than one VM.")
        for($i=0; $i -lt $job_object.GetObjectsInJob().length; $i++) {
            write-host("`t  vm: {0}" -f $job_object.GetObjectsInJob()[$i].Name)
        }
        Write-Host("")
        exit
    } else {
        return $job_object.GetObjectsInJob()[0].Name
    }
}

# actually start the Veeam job in the background
function start_veeam_job($job_name) {
    $job = Get-VBRJob -Name $job_name
    write-host("Starting Veeam job: {0}" -f $job.Name)
    Start-VBRJob -Job $job -RunAsync
    start-sleep 5
}

# perform some initial error checking and start processing Veeam jobs
function main() {
    # make sure this script has been "Run As Administrator"
    if( is_admin ) {
        Import-Module -Name "C:\Program Files\Veeam\Backup and Replication\Backup\Initialize-VeeamToolkit.ps1"
    } else {
        write-host("")
        write-host("Error: This script must be 'Run As Administrator'")
        write-host("")
        exit
    }

    # make sure Veeam cmdlets are installed
    if( ! (Check-Command("Get-VBRJob")) ) {
        write-host("")
        write-host("Error: Veeam powershell cmdlet could not be imported.")
        write-host("")
        exit
    } else {
        write-host("")
        write-host("Veeam powershell cmdlet has been imported.")
        write-host("")
    }

    # process each item in the $veeam_job_name array
    for( $i=0; $i -lt $veeam_job_names.length; $i++) {
        $job_name = $veeam_job_names[$i]
        $vm_name = get_vm_from_job($job_name)
        Write-Host("")
        Write-Host("---------------------------------------------------------------")
        Write-Host("")
        Write-Host("job name: {0}   vm name: {1}" -f $job_name.Name, $vm_name)
        Write-Host("")

        if( (check_server_write_speed($vm_name)) ) {
            start_veeam_job($job_name)
            if( ($i+1) -lt $veeam_job_names.length) {
                start-sleep $job_interval_seconds
            }
        }
    }

    write-host("")
    Write-Host("---------------------------------------------------------------")
    write-host("")
    write-host("Done: processed {0} Veeam job(s)." -f $veeam_job_names.length)
    write-host("")
}

# program execution begins here
main

# end of script
