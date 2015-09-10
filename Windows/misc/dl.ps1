#
# dl.ps1 (dl = download)
# -John Taylor
# Feb-10-2012
#
# Download file from the command line with power shell (similar to a basic wget)

Import-Module bitstransfer

$url   = $args[0]
write-host $url
$slots = $url.split("/")
$dest  = $slots[$slots.length - 1]
if ( ($url.startswith("http:") -eq $false) -and ($url.startswith("https:") -eq $false) -and ($url.startswith("ftp:") -eq $false) ) {
	$url = "http://" + $url
}

start-bitstransfer -source $url -destination $dest
