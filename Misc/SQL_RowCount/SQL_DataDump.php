<?php

/*

SQL_DataDump.php
-John Taylor
Aug-30-2007

The program returns all rows in each table of each database
from the sql server passed in from the command-line.  It excludes the
the sql system tables.  You can exclude other databases by modifying
the $db_excludes variable.

It was tested with php 4.4.2 on Windows XP (SP2) on a SQL Server 2005
server.

*/

set_time_limit(0);

$db_server = "";
$db_excludes = array( "master", "tempdb", "model", "msdb", "pubs", "Northwind", "ReportServer", "ReportServerTempDB" );
	//"MediSpan", "PncApptDb", "PncClinicalDb", "PncHL7Db", "PncImageDb", "PncImportDb", "PncProviderEntryDb", "PncRegDb" );

$db = 0;
$output_file = "";
$using_output_file = 0;
$fp = 0;

$current_col_count = 0;
$one_gig_a = pow(1024,3) - 2;
$one_gig_z = pow(1024,3) + 2;
$two_gig_a = $one_gig_a * 2;
$two_gig_z = 2147483647;

$line = "=============================================================================";
$hdr = "Column Name\t\tData Type, Nullable, Precision [Length], def: Default";

// display program command-line options
function Usage() {
	global $_SERVER;

	print "\n";
	print "Usage: " . $_SERVER["argv"][0] . " [ sql-server ] [ output file ]\n";
	print "       [ output file ] is optional\n\n";
	print "\n";
	print "The program returns the number of rows in each table of each database\n";
	print "from the sql server passed in from the command-line.  It excludes the\n";
	print "the sql system tables.\n";
}

// adapted from Klaus's comments, http://www.php.net/manual/en/function.mssql-get-last-message.php
function get_sql_error() {
	global $db;

	$sql    = "select @@ERROR as code";
	$result = @sqlsrv_query($db, $sql);
	if( FALSE == $result ) {
		return "[???] Unknown error.";
	}

	$row    = sqlsrv_fetch_array($result);
	$code  = $row["code"]; // error code

	// to get the correct msglangid, pick a value with this select stmt:
	// select name,msglangid from master.dbo.syslanguages order by 1,2
	// here are a few values...
	// us_english=1033, britsh=1033, deutsch=1031, espanol=3082, francais=1036, italiano=1040, nederlands=1043, polski=1045
	$sql = "select cast (description as varchar(255)) as errtxt from master.dbo.sysmessages where error = $code and msglangid = 1033";

	$result = @sqlsrv_query($db, $sql);
	if( FALSE == $result ) {
		return "[???] Unknown error.";
	}

	$row = sqlsrv_fetch_array($result);
	if($row) {
		$text  = $row["errtxt"]; // error text (with placeholders)
	} else {
		$text  = "[???] Unknown error.";
	}
	sqlsrv_free_stmt($result);
	return "[$code] $text";
}

// filenames can contain these 2 macros, useful if you periodically run this script from a Scheduled Task
// replace __NOW__ with the current date & time in
// this format: [year][month][day]_[hour][min][sec]
// replace __SERVER__ with $_SERVER["argv"][1]
function ExpandMacros($fname) {
	global $_SERVER;

	$now = strftime("%Y%m%d_%H%M%S");
	$result = ereg_replace("__NOW__", $now, $fname);
	return ereg_replace("__SERVER__", $_SERVER["argv"][1], $result);
}

// given a handle to a database, return an array of database names
function GetDatabaseNames() {
	global $db, $db_excludes;

	$query = "select name from master.dbo.sysdatabases";
	$result = sqlsrv_query( $db, $query );
	do {
		while ($row = sqlsrv_fetch_array($result)) {
			$databases[] = $row[0];
		}
	} while ( sqlsrv_next_result($result));
	sqlsrv_free_stmt($result);

	return array_diff( $databases, $db_excludes);
}

// given a database name, return an array including filename and filesize
// this will work only if you run the script directly from the database server itself
function GetDatabaseMetaData($name) {
	global $db;
	$fsize = -1;

	$query = "select FILENAME from MASTER.DBO.SYSDATABASES where NAME=\"$name\"";
	$result = sqlsrv_query( $db, $query );
	do {
		while ($row = sqlsrv_fetch_array($result)) {
			$fname = $row[0];
			if(file_exists($fname)) {
				$fsobj = new COM("Scripting.FileSystemObject");
				$data = $fsobj->GetFile($fname);
				$fsize = ($data->Size) + 1 - 1;
				$data=0;
			}
		}
	} while ( sqlsrv_next_result($result));
	sqlsrv_free_stmt($result);

	return array($fname, $fsize);
}


// given a handle to a database, return an array of table names within that database
function GetTableNames() {
	global $db;
	$query = "select TABLE_NAME from INFORMATION_SCHEMA.TABLES where TABLE_TYPE = 'BASE TABLE' order by TABLE_NAME";
	$result = sqlsrv_query( $db, $query );
	do {
			while ($row = sqlsrv_fetch_array($result)) {
			if("FIL" == strtoupper($row[0])) {
				continue;
			}
			$tables[] = $row[0];
		}
	} while ( sqlsrv_next_result($result));
	sqlsrv_free_stmt($result);

	return $tables;
}


// given an individual table, return the number of rows in that table
function DataDump($tbl, $db_name) {
	global $db, $fp;
	$count=0;

	$query = "select * from $tbl";
	$result = @sqlsrv_query( $db, $query );

	if( FALSE == $result ) {
		$err_msg = get_sql_error();
		print "\n";
		print "In database: " . $db_name . "\n";
		print "Can not query table: " . $tbl . "\n";
		print $err_msg . "\n";
		print "Will return -1 for the # of rows, but this will not effect overall row counts.\n\n";
		return -1;
	}
	do {
		while ($row = sqlsrv_fetch_array($result)) {
			fwrite($fp, implode("\t", $row) . "\n");
			$count++;
		}
	} while ( sqlsrv_next_result($result));

	sqlsrv_free_stmt($result);

	return $count;
}

// given a list of tables, return the length of the longest table name
// this is used to format the output & make it look nice
function GetMaxTableNameLength($arr) {
	$max = -1;
	foreach($arr as $a) {
		$l = strlen($a);
		if( $l > $max ) {
			$max = $l;
		}
	}

	return $max;
}

// output that displays pertinent info about a database, it's tables and a row count for each table
function PrintDataDump($now, $db_name, $tables, $max_len) {
	global $db_server, $line, $output_file, $using_output_file, $fp;
	global $db_file_size, $current_col_count, $hdr;

	$db_file_size = 0;

	$metadata = GetDatabaseMetaData($db_name);
	$fname = $metadata[0];
	$db_file_size = $metadata[1];

	fwrite( $fp, "\n");
	fwrite( $fp, "date        : " . $now . "\n");
	fwrite( $fp, "server      : " . $db_server . "\n");
	fwrite( $fp, "database    : " . $db_name . "\n");
	fwrite( $fp, "# of tables : " . sizeof($tables) . "\n");
	if( $db_file_size >= 0 ) {
		fwrite( $fp, "file path   : " . $fname . "\n");
		fwrite( $fp, "file size   : " . number_format($db_file_size) . "\n");
	}
	fwrite( $fp, "\n");
/*
	fwrite( $fp, "rows\t\ttable name\n");
	$short_line = substr($line,0,$max_len);
	fwrite( $fp, "====\t\t$short_line\n");
*/

	fwrite( $fp, $hdr . "\n\n");
	$total_rows=0;
	foreach( $tables as $t ) {
		$cols = ColNames($t, $db_name);
		$line_tbl_name = substr("-------------------------------------------------------------------------------",0,strlen($db_name)+1+strlen($t)+5+strlen($current_col_count));
		fwrite( $fp, $line_tbl_name . "\n");
		fwrite( $fp, $db_name . "." . $t . " { " . $current_col_count . " }\n");
		fwrite( $fp, $line_tbl_name . "\n");
		fwrite( $fp, "$cols\n" );

		$count = DataDump($t, $db_name);
		if( $count >= 1000000 ) {
			fwrite( $fp, number_format($count) . "\t$t\n");
		} else {
			fwrite( $fp, number_format($count) . "\t\t$t\n");
		}
		// -1 is returned when an error occurs, but don't want to skew the results
		if ( -1 == $count ) $count = 0;

		$total_rows += intval($count);
		fwrite( $fp, "\n\n");
	}
	fwrite( $fp, "====================$short_line\n");
	fwrite( $fp, number_format($total_rows) . " total rows.\n");
	fwrite( $fp, "\n");
	fwrite( $fp, "$line\n$line\n");

	fflush($fp);
	return $total_rows;
}

// given an individual table, return the column information
function ColNames($tbl, $db_name) {
	global $db, $current_col_count;
	global $one_gig_a, $one_gig_z, $two_gig_a, $two_gig_z;

	$col_names = "";
	$current_col_count = 0;

	$query = "sp_columns $tbl";
	$result = @sqlsrv_query( $query, $db );

	if( FALSE == $result ) {
		$err_msg = get_sql_error();
		print "\n";
		print "In database: " . $db_name . "\n";
		print "Can not query table: " . $tbl . "\n";
		print $err_msg . "\n";
		return -1;
	}
	do {
		while ($row = sqlsrv_fetch_array($result)) {
			$name = trim($row[3]);
			$dtype = trim($row[5]);
			$precision = intval(trim($row[6]));
			if( $precision >= $one_gig_a && $precision <= $one_gig_z ) {
				$precision = "1 Gig";
			}
			if( $precision >= $two_gig_a && $precision <= $two_gig_z ) {
				$precision = "2 Gigs";
			}
			if( $precision > $one_gig_a ) {
				$precision = number_format($precision);
			}

			$length = trim($row[7]);
			if( $length >= $one_gig_a && $length <= $one_gig_z ) {
				$length = "1 Gig";
			}
			if( $length >= $two_gig_a && $length <= $two_gig_z ) {
				$length = "2 Gigs";
			}
			if( $length > $one_gig_a ) {
				$length = number_format($length);
			}

			//$nullable = trim($row[10]);
			$column_def = trim($row[12]);
			$is_nullable = trim($row[17]);
			if( 0 == strlen($is_nullable) ) {
				$is_nullable = "UNKNOWN";
			}
			$current_col_count += 1; 

			if( strlen($name) <= 7 ) {
				$tab = "\t\t\t\t\t";
			} elseif( strlen($name) <= 15 ) {
				$tab = "\t\t\t\t";
			} elseif( strlen($name) <= 23 ) {
				$tab = "\t\t\t";
			} elseif( strlen($name) <= 31 ) {
				$tab = "\t\t";
			} else {
				$tab = "\t";
			}
			
			$last_comma = (strlen($column_def)) ? ", def: " : "";
			$col_names = sprintf("%s\n%s%s%s, %s, %s [%s]%s %s", $col_names, $name, $tab, $dtype, $is_nullable, $precision, $length, $last_comma, $column_def);
		}
	} while ( sqlsrv_next_result($result));

	sqlsrv_free_stmt($result);

	$col_names = substr($col_names,strlen("\n")) . "\n\n";
	return $col_names;
}


// program exectuion starts here
function main() {
	global $_SERVER;
	global $db, $db_server,  $output_file, $using_output_file, $fp;
	global $db_file_size;

	$dbg = 0; // default is 0, set to 1 to turn on debugging

	if( $_SERVER["argc"] != 2 && $_SERVER["argc"] != 3 ) return Usage();
	
	$db_server = $_SERVER["argv"][1];
	if( 3 == $_SERVER["argc"] ) {
		$using_output_file = 1;
		$output_file = $_SERVER["argv"][2];
		$output_file = ExpandMacros($output_file);
		$fp = fopen( $output_file, "w");
	} else {
		$fp = fopen("php://output", "w");
	}

	$db_total_rows = 0;
	$db_total_tables = 0;
	$db_total_file_size = 0;
	$now = strftime("%Y-%m-%d %H:%M:%S");

	// connect to server and select the database
	// could also use something like: $db = sqlsrv_connect( "\\\\$db_server\\pipe\\sql\\query", "ExampleReports", "" );
	//$db = sqlsrv_connect( "\\\\$db_server\\pipe\\sql\\query", "PROPHARM", "" );
	$db = @sqlsrv_connect( $db_server, array( "Database" => "master" ));
	if( FALSE == $db ) {
		print "\n";
		print "Unable to make database connection to host: " . $db_server . "\n\n";
		fclose($fp);
		return;
	}

	$db_list = GetDatabaseNames();
	if( 1 == $dbg) {
		print "\nDatabases:\n";
		print   "==========";
		print "\n";
		var_dump($db_list);
		print "\n\n";
	}
	sqlsrv_close($db);

	fwrite( $fp, $line . "\n");
	foreach( $db_list as $current_db ) {
		$db = sqlsrv_connect( $db_server, array( "Database" => $current_db) );
		$tables = GetTableNames();
		if( 1 == $dbg) {
			print "\n($current_db) tables:\n";
			print   "================================================";
			print "\n";
			var_dump($db_list);
			print "\n\n";
		}
		$db_total_tables += sizeof($tables);
		$max_tbl_len = GetMaxTableNameLength($tables);
		$db_total_rows += PrintDataDump($now, $current_db, $tables, $max_tbl_len);
		$db_total_file_size += $db_file_size;
		sqlsrv_close($db);
	}

	fwrite( $fp, "Total number of databases    : " . sizeof($db_list) . "\n");
	fwrite( $fp, "Grand total number of tables : " . number_format($db_total_tables) . "\n");
	fwrite( $fp, "Grand total number of rows   : " . number_format($db_total_rows) . "\n");
	if( $db_total_file_size ) {
		fwrite( $fp, "Grand total file size        : " . number_format($db_total_file_size) . "\n");
	}
	fwrite( $fp, "\n");

	return;

	if( 1 == $using_output_file) {
		fflush($fp);
		fclose($fp);
	}
}

date_default_timezone_set('America/New_York');
main();

?>
