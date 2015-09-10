<?php

/*

SQL_RowCount.php
-John Taylor
Feb-12-2006
Sep-13-2006 - update #1
Sep-28-2006 - update #2
Dec-21-2011 - update #3 PHP v5.3.8 and added date_default_timezone_set();

The program returns the number of rows in each table of each database
from the sql server passed in from the command-line.  It excludes the
the sql system tables.  You can exclude other databases by modifying
the $db_excludes variable.

It was tested with php 4.4.2 on Windows XP (SP2) on a SQL Server 2000
(SP3) server.  It has also been tested with php 5.3.8 on Windows 7 (SP1)
against a SQL Server 2008 server.

*/

set_time_limit(0);

$db_server = "";
$db_excludes = array( "master", "tempdb", "model", "msdb", "pubs", "Northwind" );
$db = 0;
$output_file = "";
$using_output_file = 0;
$fp = 0;

$line = "=============================================================================";

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
			$tables[] = $row[0];
		}
	} while ( sqlsrv_next_result($result));
	sqlsrv_free_stmt($result);

	return $tables;
}


// given an individual table, return the number of rows in that table
function RowCount($tbl, $db_name) {
	global $db;

	$query = "select count(*) from $tbl";
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
			$count = $row[0];
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
function PrintRowCount($now, $db_name, $tables, $max_len) {
	global $db_server, $line, $output_file, $using_output_file, $fp;
	global $db_file_size;

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

	fwrite( $fp, "rows\t\ttable name\n");
	$short_line = substr($line,0,$max_len);
	fwrite( $fp, "====\t\t$short_line\n");

	$total_rows=0;
	foreach( $tables as $t ) {
		$count = RowCount($t, $db_name);
		if( $count >= 1000000 ) {
			fwrite( $fp, number_format($count) . "\t$t\n");
		} else {
			fwrite( $fp, number_format($count) . "\t\t$t\n");
		}
		// -1 is returned when an error occurs, but don't want to skew the results
		if ( -1 == $count ) $count = 0;

		$total_rows += intval($count);
	}
	fwrite( $fp, "====================$short_line\n");
	fwrite( $fp, number_format($total_rows) . " total rows.\n");
	fwrite( $fp, "\n");
	fwrite( $fp, "$line\n$line\n");

	fflush($fp);
	return $total_rows;
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

	$connectionInfo = array( "Database"=>"master");
	$db = sqlsrv_connect( $db_server, $connectionInfo );
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
	sqlsrv_close( $db );


	fwrite( $fp, $line . "\n");
	foreach( $db_list as $current_db ) {
		// is there really no way to change databases with the same connection?
		//$valid = sqlsrv_select_db($current_db, $db);

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
		$db_total_rows += PrintRowCount($now, $current_db, $tables, $max_tbl_len);
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
