
#cs
mp.au3 (multi-process)
-John Taylor
May-01-2012

Documentation
-------------
mp will run a (command line) program in parallel on a group of similar files.
I have tested this with 2 CPU and 16 CPU systems.

cmd-line arguments:

1) the program executable to run in parallel
2) input pattern, in double quotes
	a) _input_    the filename plus extension matched by the wildcard file pattern in (4)
	b) _base_     the filename without the extension
	c) _ext_      only the file's extension without a leading dot
	f) _date_     date the program started, does not change
	g) _time_     time the program started, does not change
	h) _ip_       ip address of the 1st network interface
	h) _ip2_      ip address of the 2nd network interface
3) output pattern, use -- for no output (two dashes).
4) wildcard pattern #1, wildcard pattern #2, etc  If -fromfile:items.txt is used, for example,
   then files names are read from items.txt.

icon used: http://www.iconarchive.com/show/angry-birds-icons-by-fasticon/red-bird-icon.html

Examples
---------
mp.exe "C:\Program Files\ImageMagick\convert.exe" "_input_ _base_.tiff" -- *.png
This will convert all PNG files to tiff files, which will have the same base name.
No output files will be created.

mp.exe "bzip2 -9" "_input_" -- a*.txt
This will compress all text files starting with "a"
No output files will be created.

mp.exe "sha1sum" "_input_" "_base_.sha" *.dat
This will checksum all *.dat files and place the results in individual *.sha files.


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
#ce

#notrayicon
Opt("MustDeclareVars",1)
Opt("TrayMenuMode", 1)

#include <File.au3>
#include <Array.au3>
#include <Constants.au3>

; number of `threads' to use
global $cpu_count = EnvGet("NUMBER_OF_PROCESSORS")

; two dimensional array, first col=number of CPUs, second col=list of file to be processed on that CPU
; the second column will be ReDim'd
global $flist[$cpu_count][1]

; number of files in each of the $flist[$x] vectors
global $flist_count[$cpu_count]

; currently running PID on a given CPU
global $pid[$cpu_count]

; number of jobs that have been processed on a given CPU (as not to exceed $flist_count[cpu])
global $job[$cpu_count]

; the acutal command to be run
global $exe

; cmd line file replacement
global $in_pattern, $out_pattern

; total number of jobs send to the Run() function
global $finished = 0

; record all Run() PIDs so that their output can be captured
global $all_pids[1]

; the actual text output of each Run() operation
global $all_pids_output = ObjCreate("Scripting.Dictionary")

; lower right try icon, for status updates
global $tray

; total number of files that will be processed
global $total_jobs = 0

global $st_date = @YEAR & @MON & @MDAY
global $st_time = @HOUR & @MIN & @SEC

func create_file_lists()
	local $i, $curr, $count
	local $all[1]
	$all[0] = 0

	$count = 0
	for $i = 4 to $CmdLine[0] ; start at 4 b/c 1=exe 2=in_pattern 3=out_pattern 4,5,6,etc=filenames
		$curr = _FileListToArray(".", $CmdLine[$i], 1)
		if(@error) then
			continueloop
		endif
		$count += $curr[0]
		$all[0] = $count
		_ArrayConcatenate($all,$curr,1)
	next

	_ArrayDelete($all,0)
	$all = _ArrayUnique($all,1)
	
	return $all
endfunc

func multiprocess()
	global $cpu_count, $exe, $in_pattern, $out_pattern, $finished, $all_pids, $all_pids_output, $tray
	global $flist, $flist_count, $pid, $job, $total_jobs
	local $i, $curr, $args, $myin_pattern, $myout_pattern
	local $input, $base, $ext
	local $szDrive, $szDir, $base, $ext
	local $cmd, $fp
	global $st_date, $st_time

	for $i = 0 to $cpu_count-1
		if not ProcessExists( $pid[$i] ) then
			if int($job[$i]) < int($flist_count[$i]) then
				$args = $flist[$i][$job[$i]]
				$input = $flist[$i][$job[$i]]
				_PathSplit($input, $szDrive, $szDir, $base, $ext)
				$ext = StringMid($ext,2)

				$myin_pattern = $in_pattern
				$myin_pattern = StringReplace($myin_pattern,"_input_", $input)
				$myin_pattern = StringReplace($myin_pattern,"_base_", $base)
				$myin_pattern = StringReplace($myin_pattern,"_ext_", $ext)
				$myin_pattern = StringReplace($myin_pattern,"_date_", $st_date)
				$myin_pattern = StringReplace($myin_pattern,"_time_", $st_time)
				$myin_pattern = StringReplace($myin_pattern,"_ip_", @IPAddress1)
				$myin_pattern = StringReplace($myin_pattern,"_ip2_", @IPAddress2)


				$myout_pattern = $out_pattern
				$myout_pattern = StringReplace($myout_pattern,"_input_", $input)
				$myout_pattern = StringReplace($myout_pattern,"_base_", $base)
				$myout_pattern = StringReplace($myout_pattern,"_ext_", $ext)
				$myout_pattern = StringReplace($myout_pattern,"_date_", $st_date)
				$myout_pattern = StringReplace($myout_pattern,"_time_", $st_time)
				$myout_pattern = StringReplace($myout_pattern,"_ip_", @IPAddress1)
				$myout_pattern = StringReplace($myout_pattern,"_ip2_", @IPAddress2)

				$cmd = $exe & " " & $myin_pattern
				if $out_pattern == "--" then
					$curr = Run($cmd, "", @SW_HIDE)
				else
					$curr = Run($cmd, "", @SW_HIDE, $STDOUT_CHILD)
				endif
				_ArrayAdd($all_pids, $curr)

				; if you have a large number of files to process, PIDs can be duplicated
				if $all_pids_output.Exists($curr) then
					$all_pids_output.Remove($curr)
				endif
				$all_pids_output.Add($curr, $myout_pattern)
				$finished += 1
				$job[$i] += 1
				$pid[$i] = $curr
				TraySetToolTip( $finished & " jobs started, " & ($total_jobs - $finished) & " jobs remaining.")
			endif
		endif
	next
	
	; check for output on any completed Run() operations
	if $out_pattern <> "--" then
		local $line
		for $i = 1 to ubound($all_pids) - 1
			$line = StdOutRead($all_pids[$i])
			if StringLen($line) > 0 then
				FileWriteLine($all_pids_output.Item($all_pids[$i]), $line)
				$all_pids[$i] = - 1
			endif
		next
	endif
endfunc
	

func main()
	global $flist, $cpu_count, $pid, $exe, $finished, $all_pids, $tray, $total_jobs
	local $all_flist, $item, $from_fname

	if ( $CmdLine[0] < 4 ) then
		MsgBox(0,"Usage",@ScriptName & @CRLF & "mp - multiprocess" & @CRLF & "----------------------------" & @CRLF & "Runs a (command line) program in parallel on a group of similar files." & @CRLF & @CRLF & "Command line arguments:" & @CRLF & @CRLF & "(1) [ command-executable ]" & @CRLF &  "(2) [ input pattern ]" & @CRLF & "(3) [ output pattern ]   Use -- for no output files" & @CRLF & "(4) [ file mask 1] [ file mask 2] ..." & @CRLF & '      or use   -fromfile:"c:\pgm data\list.txt"   (file names are read from list.txt)' & @CRLF & @CRLF & "Patterns:" & @CRLF & @CRLF & "_input_    the filename plus extension matched by the wildcard file pattern in (4)" & @CRLF & "_base_     the filename without the extension" & @CRLF & "_ext_        only the file's extension without a leading dot" & @CRLF & "_date_     date the program started, YYYYMMDD (does not change)" & @CRLF & "_time_     time the program started, HHMMSS (does not change)" & @CRLF & "_ip_          ip address of 1st network interface" & @CRLF & "_ip2_        ip address of 2nd network interface" & @CRLF & @CRLF & "Examples:" & @CRLF & @CRLF & '1) mp "bzip2 -9"  _input_  --  a*.txt' & @CRLF & "    compress text files starting with 'a', no output files" & @CRLF & @CRLF & '2) mp  convert.exe  "_input_  _base_._date_._time_.tiff"  --  *.png' & @CRLF & "    convert PNG files to TIFF, which includes basename, date, time in filename " & @CRLF & @CRLF & '3) mp  "c:\pgm files\utils\sha1sum.exe"  _input_  _base_.sha  *.dat' & @CRLF & "    checksum all *.dat files, place results in individual *.sha files" & @CRLF & @CRLF & "** Hover over red bird system tray icon for status.")
		exit
	endif

	$exe = $CmdLine[1]
	$in_pattern = $CmdLine[2]
	$out_pattern = $CmdLine[3]

	$tray = TrayCreateItem("")
	TraySetState()

	if StringLeft($CmdLine[4],10) == "-fromfile:" then
		$from_fname = StringMid($CmdLine[4],11)
		_FileReadToArray($from_fname, $all_flist)
		if @error then
			MsgBox(16,"Error", "Unable to read file: " & $from_fname)
			exit
		endif
	else
		$all_flist = create_file_lists()
	endif

	if ubound($all_flist) == 0 then
		MsgBox(16,"Error", "No files matched your criteria.")
		exit
	endif

	$total_jobs = $all_flist[0]
	
	for $i = 0 to $cpu_count-1
		ReDim $flist[ubound($flist,1)][(ubound($all_flist) / $cpu_count) + 1]
		$flist_count[$i] = 0
		$pid[$i] = -1
		$job[$i] = 0
	next

	local $i = 0
	local $j = 0
	while ubound($all_flist) > 1
		$item = _ArrayPop($all_flist)
		$j=$flist_count[$i]
		$flist[$i][$j] = $item
		$flist_count[$i] += 1
		$i += 1
		if $i == $cpu_count then
			$i = 0
		endif
	wend
	
	do
		multiprocess()
		sleep(200)
	until $finished = $all_flist[0]

	; check for output on any outstanding Run() operations
	if $out_pattern <> "--" then
		local $line, $j
		for $j = 1 to  5
			for $i = 1 to ubound($all_pids) - 1
				$line = StdOutRead($all_pids[$i])
				if StringLen($line) > 0 then
					FileWriteLine($all_pids_output.Item($all_pids[$i]), $line)
					$all_pids[$i] = - 1
				endif
			next
			sleep(200)
		next
	endif
endfunc

main()

