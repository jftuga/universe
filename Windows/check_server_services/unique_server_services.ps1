#
# unique_server_services.ps1
# -John Taylor
# June-22-2011
#
#
# Compile a list of semi-unique services running on a list of given servers.
# By semi-unique, we mean $max servers or less.  For example, SQL Server is
# semi-unique in that it is important and it runs on multiple servers.

# change accordingly
$svr_list = @( "ad1", "ad2", "exchange", "www", "sql1" )
$max = 5

$service_name = @{}
$service_short = @{}

function inventory($svr) {
	$list = gwmi win32_service -ComputerName $svr | Where-Object { $_.State -eq "Running" }
	$list | foreach-object {
			$disp = $_.DisplayName
			$short = $_.Name
			if ( $service_name[$disp] -eq $null ) {
					$service_name[$disp] = @()
			}
			$service_name[$disp] += $svr

			if( $service_short[$svr] -eq $null ) {
				$service_short[$svr] = @{}
			}

			$service_short[$svr][$disp] = $short
	}
}

function service_is_running_on_N_number_of_servers($n,$file) {
	foreach( $q in $service_name.keys ) {
		if ( $service_name[$q].Length -eq $n ) {
			write-host "$n ) $q"
			$i=0
			while($i -lt $service_name[$q].Length) {
				# $service_short is a 2-D array...
				# (1) $service_name[$q][$i] is a server name, (2) $q is the service name
				$result = $service_name[$q][$i] + "`t" + $service_short[$service_name[$q][$i]][$q] + "`t" + $q
				add-content $file $result
				$i += 1
			}
		}
	}
}

#
# Main program execution begins here...
#

foreach( $svr in $svr_list) {
	write-host "inventory: $svr"
	inventory($svr)
}

# output results to a tab delimited file
$i=1
$fname = "services.tsv"
$file = New-Item -type file $fname -force
add-content $file "Server Name`tShort Name`tService Name"
while( $i -le $max ) {  # a service is not all that unique if running on more than this number of servers
	service_is_running_on_N_number_of_servers $i $file
	$i += 1
}

# end of script

