#
# backup_esxi_configs.ps1
# -John Taylor
# Aug-04-2011
#
# You will need this installed: VMWare vSphere PowerCLI
#
# 1) Iterate through all vCenter servers listed in $vctr_list
# 2) Create a configuration backup of each ESXi server
# 3) These backups are saved in a folder given on the command line
#
# If you need to restore, right click on VMWare vSphere PowerCLI and run:
# get-help Set-VMHostFirmware -detailed
# 

set-strictmode -version Latest

# You must include domain names
$vctr_list = @( "vcenter1.example.com", "vcenter2.example.com")

$backup_dir = ""
$bundle = ":configBundle-"

function get_esxi_svrs($vctr) {
	$conn = connect-viserver -Server $vctr
	$objs = Get-View -ViewType HostSystem |? {$_.config.product.ProductLineId -eq "embeddedEsx" -and $_.Runtime.ConnectionState -eq "connected"}

	$hosts = @()

	foreach( $h in $objs ) {
		$hosts += [String] $h.Name
	}
	$hosts
}

function make_esxi_backup($esx) {
	$ret = $Null
	$ret = Get-VMHostFirmware -VMHost $esx -BackupConfiguration -DestinationPath $backup_dir
	[String] $ret
}


function backup_vcenter_svr($vctr) {
	$errors = 0
	$a = get_esxi_svrs $vctr
	foreach ($e in $a) {
			write-host "backing up: $e"
			$rv = make_esxi_backup $e
			$j = "$e$bundle$e.tgz"
			if( $rv -ne $j ) {
				$errors += 1
				write-host ""
				write-host ""
			}
	}
	$errors
}

function usage() {
	write-host ""
	write-host ""
	write-host "Usage:"
	write-host "backup_esxi_configs.ps1 [ backup folder ]"
	write-host ""
	write-host ""
	write-host ""
}


if( $args.Length -ne 1 ) {
	usage
	exit
}

$rewt = $args[0]
$backup_dir = "$rewt\ESXi_config_backups"

if( (Test-Path -path $backup_dir -pathType Container) -ne $True ) {
	$rv = New-Item $backup_dir -type directory
	if( $rv -eq $Null ) {
		Write-Host ""
		Write-Host "Error: Could not create directory: $backup_dir"
		Write-Host "Exiting script."
		Write-Host ""
		exit
	}
}


$err_count = 0
foreach( $item in $vctr_list ) {
	$err_count += backup_vcenter_svr $item
}

write-host ""
write-host "Config backups saved under: $backup_dir"
write-host "$err_count errors detected."
write-host ""

