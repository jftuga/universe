#
# list_vm_snapshots.ps1
# -John Taylor
# Jan-9-2012
#
# You need VMWare PowerCLI installed.
#
# Iterates through your vCenter server and creates a tab-delimited report
# of snapshot usage.
# If you associate Excel with the .tsv extension, this will import cleanly.


if ($args.length -eq 0) {
	write-host
	write-host "Please give vCenter server name on command line"
	write-host
	exit
}

$vctr = $args[0]
$conn = Connect-VIServer -Server $vctr
$now = get-date -format yyyyMMdd.HHmmss
$output = "snapshots--" + $now + "--" + $vctr + ".tsv"

$SnapObj = New-Object psobject
$SnapObj | Add-Member -MemberType NoteProperty srvr -Value $null
$SnapObj | Add-Member -MemberType NoteProperty name -Value $null
$SnapObj | Add-Member -MemberType NoteProperty size_in_MB -Value $null
$SnapObj | Add-Member -MemberType NoteProperty date -Value $null
$SnapObj | Add-Member -MemberType NoteProperty desc -Value $null

$servers = @()
$mylist = Get-VM |? {$_.PowerState -eq "PoweredOn"}
foreach( $obj in $mylist ) {
	$tmp = [String] $obj.Name
	$servers += $tmp.ToUpper()
}

$count = 0
$table = @()
$servers = $servers | sort-object

foreach( $str in $servers) {
	$str
	$meta = get-snapshot $str
	if( $meta.Name.length -gt 0 ) {
		$entry = $SnapObj | select-object *
		$entry.srvr = $str
		$entry.size_in_MB = $meta.sizeMB
		$entry.date = $meta.Created
		$entry.name = $meta.Name
		$entry.desc = $meta.Description
		$entry
	
		$table += $entry
		$count += 1
	}
}

Disconnect-VIServer -server $vctr -confirm:$false

if( $count -eq 0 ) {
	Write-Host
	Write-Host "No VMs have snapshots."
	Write-Host
	exit
}

$table | export-csv -path $output -delimiter `t -NoTypeInfo
Write-Host
Write-Host "$count VMs have snapshots."
Write-Host "tab-delimited output file: $output"
Write-Host
