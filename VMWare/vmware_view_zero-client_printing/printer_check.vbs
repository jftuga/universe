'
' printer_check.vbs
' -John Taylor
'
' Aug-4-2010
' Dec-7-2010   (ver 2, use netstat to see if a terminal is connected on UDP port 4172)
' Dec-22-2010  (ver 3, added terminal location aware printing)
' 
' VMWare View in conjunction with PCoIP terminals have a known issue with
' USB printers.  Printers attached to a terminal will sporadically  get
' mysteriously disconnected and then reconnected.  This happens with our
' Dell laser printers and our Dymo label printers.  When the printer gets
' "reconnected", Windows XP believes this is a brand new printer that needs
' to be installed rather than the same printer simply being "unplugged"
' and the "plugged in" again. These old, stale printers show up as "Dell
' Printer (Copy 1)" [or Copy 2, etc.] and are grayed out because they
' are offline. Until Teradici and/or VMWare release a proper fix for this
' problem, Gunnar & I have devised a workaround.
' 
' This VBScript is launched from the main network logon script for these
' terminals.  It runs forever in the background.  Every two minutes, the
' script will wake up and try to reset the default printer, if needed.
' The criteria for what is considered to be the default printer is simple:
' [1] The printer name starts with Dell (as opposed to Dymo, MidMark, etc.)
' [2] The printer is online
' 
' If the script determines this is the current OS's settings, it will
' pause for 2 minutes and then check again.  If the script determines that
' the default printer is either offline or does not start with "Dell",
' then the script will change the default printer to one that meets the
' above criteria.  This change is logged on our file server.  If the
' script cannot find a suitable printer that matches the above criteria,
' then this is also logged and no changes to the default printer is made.
' This could happen if all printers happen to be offline or if no Dell
' printers are installed.

' version 2 enhancements
' ----------------------
' The script checks to see if a PCoIP terminal is attached by checking
' for an active UDP connection on port 4172.  If there is no connection,
' no message is written to the error log.  When the error occurs & a
' terminal is attached, then there will also be an email sent to notify IT
' about the error.  The contents of the error log file will be the body
' of the email.  A zip file attachment will include the pcoip log files.
' During non-business hours (8-5) and on the weekends, a message is still
' written to the log file, but no email is sent.  Once an email is sent,
' there will be a very long delay before another email is sent.
'
' Version 2 requires two external dependencies:
' a) blat.exe  from http://www.blat.net/
' b) zip.exe   from http://www.info-zip.org/
'
' version 3 enhancements
' ----------------------
' If your terminals use network printers and users switch from terminal to
' terminal without logging off and then back on, then the closet printer
' may not be the default printer any more.  Create a CSV file with the
' first column containing the dns name of the terminal (recommended) or
' ip address (not recommended since terminals may change IP addresses).
' The second column will contain the network printer path.  This script
' will wake up every 30 seconds and check the VM's location to see if it
' has been connected to a different terminal.  If it has, it will change
' the default printer.  One thing to note is that the printer already must
' be installed.  Right now, the feature does not do any logging.

' future enhancements
' -------------------
' I just discovered that the terminal information dynamically updates
' this registry location, HKCU\Volatile Environment.  Using this instead
' of netstat will be more efficient and less prone to potential problems.
' I also plan on added logging the the version 3 enhancement.

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

On Error Resume Next

' version 1 variables
Const DesiredDefaultPtr = "Dell"
Const ErrorLogPath = "\\MyServer\apps\terminal_errors"
Const wbemFlagReturnImmediately = &h10
Const wbemFlagForwardOnly = &h20
Const ForReading = 1
Const ForAppending = 8

' version 2 variables
Const NetstatPgmUDP = "c:\WINDOWS\system32\netstat.exe -a -n -p UDP"
Const BlatPgm = "\\MyServer\apps\terminal_errors\blat.exe"
Const ZipPgm = "\\MyServer\apps\terminal_errors\zip.exe"
Const TerminalLogPath = "c:\Documents and Settings\All Users\Application Data\VMware\VDM\logs\pcoip*txt"
Const SkipList = "\\MyServer\apps\terminal_errors\skip_list.txt"
Const Email_Svr = "smtp.example.com"
Const Email_From = "sender@example.com"
Const Email_To   = "alerts@example.com"
Const Email_Subj = "automatated terminal printer error detected on: "
SendEmail = 1

' version 3 variables
Const MappingFile="\\MyServer\apps\terminal_errors\location_aware_printing.csv"
Const NetstatPgmTCP = "c:\WINDOWS\system32\netstat.exe -a -p TCP"  ' add -n to use by IP address only, which is much faster & also good for testing
Const Domain = ".EXAMPLE.COM"   ' must be in all upper case and begin with a dot
Dim mapping(100)

' version 1 & 2 functions

function DateTime()
	sHour = Hour(Now())
	if len(sHour) = 1 then sHour = "0" & sHour
	sMin = Minute(Now())
	if len(sMin) = 1 then sMin = "0" & sMin
	sSec = Second(Now())
	if len(sSec) = 1 then sSec = "0" & sSec 
	sTime = sHour & sMin & sSec

	sDay = Day(Now()) 
	If Len(sDay) = 1 Then sDay = "0" & Day(Now()) 
	sMonth = Month(Now()) 
	If Len(sMonth) = 1 Then sMonth = "0" & Month(Now()) 
	sYear = Year(Now()) 
	sDate = sYear & sMonth & sDay 

	DateTime =  sDate & "_" & sTime
end function

function log_error(msg, noemail_flag)
	q = chr(34)

	Set WshNetwork = WScript.CreateObject("WScript.Network")
	ComputerName = WshNetwork.ComputerName 
	Set WshNetwork = Nothing

	msg = ComputerName & vbTab & Date & vbTab & Time & vbTab & msg

	Set objFSO = CreateObject("Scripting.FileSystemObject")
	fname_log = ErrorLogPath & "\" & ComputerName & ".tsv"
	Set objTextFile = objFSO.OpenTextFile (fname_log, ForAppending, True)
	objTextFile.WriteLine(msg)
	objTextFile.Close

	set objFSO = Nothing

	if SendEmail <> 1 then
		exit function
	end if

	if noemail_flag = 1 then
		exit function
	end if

	' don't send email on Sat. or Sun.
	if Weekday(Now()) = 1 or Weekday(Now()) = 7 then
		exit function
	end if

	' don't send email during non-business hours
	h = Hour(Now)
	if h < 8 or h > 17 then
		exit function
	end if

	' build zip command line
	Set oShell = CreateObject( "WScript.Shell" )
	temp_dir=oShell.ExpandEnvironmentStrings("%TEMP%")
	Set oShell = Nothing

	dt = DateTime()
	fname_zip = temp_dir & "\terminal_logs--" & ComputerName & "--" & dt & ".zip"
	
	zip_opts = "-9r " & q & fname_zip & q & " " & q & TerminalLogPath & q 
	cmd = ZipPgm & " " & zip_opts
	wscript.echo cmd
	wscript.echo
	Set WshShell = WScript.CreateObject("WScript.Shell")
	WshShell.Run cmd,6,True
	Set WshShell = Nothing
	

	' build blat command line
	blat_opts = q & fname_log & q & " -priority 1 -attach " & q & fname_zip & q & " -to " & Email_To & " -subject " & q & Email_Subj & ComputerName &  q & " -f " & Email_From & " -server " & Email_Svr
	cmd = BlatPgm & " " & blat_opts
	wscript.echo cmd
	wscript.echo
	Set WshShell = WScript.CreateObject("WScript.Shell")
	WshShell.Run cmd,6,True
	Set WshShell = Nothing

	SendEmail = 0

end function

function change_default_ptr_v1(ptr)
	Set objPrinter = CreateObject("WScript.Network")
	objPrinter.SetDefaultPrinter ptr
end function

function load_skip_list()
	my_list = ""

	Set objFSO = CreateObject("Scripting.FileSystemObject")
	Set objTextFile = objFSO.OpenTextFile (SkipList, ForReading)

	do while objTextFile.AtEndOfStream <> True
		line = objTextFile.ReadLine
		my_list = my_list & "|" & line
	loop

	objTextFile.Close

	load_skip_list = my_list
end function

function main()
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo
	wscript.echo "In main()"
	wscript.echo
	If Wscript.Arguments.Count = 0 Then
		strComputer = "."
	else
		strComputer = Wscript.Arguments(0)
	end if

	' if VM is not connected to PCoIP terminal, exit function now & do not check for printers
	connected = 0
	if "." = strComputer then
		set objShell = CreateObject("WScript.Shell")
		set objWshScriptExec = objShell.Exec( NetstatPgmUDP )
		set objStdOut = objWshScriptExec.StdOut

		while not objStdOut.AtEndOfStream
			data = objStdOut.ReadLine
			if 0 = connected then
				Wscript.echo "netstat:" & data
				if InStr(data,":4172") then
					wscript.echo "pcoip connection detected!"
					connected = 1
				end if
			end if
		wend
	end if

	set objStdOut = Nothing
	set objWshScriptExec = Nothing
	set objShell = Nothing
	wscript.echo "Connected1: " & connected

	if 0 = connected then
		exit function ' not connected to a terminal, so exit main() function
	end if

	' if VM is in the skip list file, exit function now & do not check for printers
	' this is useful when the terminal prints to a network printers ( only local printers have issues )
	vm_skip_list = load_skip_list()
	vm_skip_list = ucase(vm_skip_list)
	
	my_name = strComputer
	if my_name = "." then
		set wshnetwork=createobject("wscript.network")
		my_name=wshnetwork.computername
		set wshnetwork=nothing
	end if
	my_name = ucase(my_name)

	if InStr(vm_skip_list, my_name) then
		wscript.echo "skip? yes"
		exit function ' vm is on the skip list, exit
	end if


	' WMI queries to get a list of printers
	DesiredDefaultPtrName = ""
	DefaultPtrName = ""

	Set objWMIService = GetObject("winmgmts:\\" & strComputer & "\root\CIMV2")
	Set colItems = objWMIService.ExecQuery("SELECT * FROM Win32_Printer where Default='True'", "WQL", wbemFlagReturnImmediately + wbemFlagForwardOnly)
	For Each objItem In colItems
		DefaultPtrName = objItem.Name
	Next
	
	wscript.echo
	wscript.echo "Default Printer"
	wscript.echo "==============================="
	wscript.echo DefaultPtrName
	wscript.echo
	wscript.echo
	
	
	Set colItems = objWMIService.ExecQuery("SELECT * FROM Win32_Printer", "WQL", wbemFlagReturnImmediately + wbemFlagForwardOnly)
	wscript.echo "Default" & vbTab & "Status" & vbTab & "Desired Deflt" & vbTab & "Name"
	wscript.echo "=======" & vbTab & "======" & vbTab & "=============" & vbTab &  "==============================="
	
	For Each objItem In colItems
		PtrName = objItem.Name
		IsDefaultPtr = objItem.Default
		WorkOffline = objItem.WorkOffline
	
		PtrStatus = "Online"
		if True = WorkOffline then
			PtrStatus = "Offline"
		end if
	
		DefaultPtr = "No"
		if True = IsDefaultPtr then
			DefaultPtr = "Yes"
		end if
	
		IsDesiredDefaultPtr = "No"
		if InStr(PtrName, DesiredDefaultPtr) > 0 and "Online" = PtrStatus then
			IsDesiredDefaultPtr = "Yes"
			DesiredDefaultPtrName = PtrName
		end if
	
		wscript.echo DefaultPtr & vbTab & PtrStatus & vbTab & IsDesiredDefaultPtr & vbTab & vbTab & PtrName
	Next
	
	wscript.echo
	wscript.echo

	if len(strComputer) > 1 then
		wscript.echo "Can not change default printer for remote computers, quitting"
		wscript.quit
	end if

	if DesiredDefaultPtrName = "" then
		rv = search_for_network_printer()
		wscript.echo "search for network ptr : " & rv
		if 0 <> rv then
			msg = "No desired default printer found: " & DesiredDefaultPtr & vbcrlf & "Sending email to: " & Email_To
			wscript.echo msg
			wscript.echo rv
			wscript.echo "Writing error log into folder: " & ErrorLogPath
			log_error msg, 0 ' send an email
		end if
		exit function
	end if
	
	if DefaultPtrName <> DesiredDefaultPtrName then
		wscript.echo "Change Default Ptr To"
		wscript.echo "==============================="
		wscript.echo DesiredDefaultPtrName
		change_default_ptr_v1 DesiredDefaultPtrName
		msg = "Changed default printer from: " & DefaultPtrName & "    to: " & DesiredDefaultPtrName
		log_error msg, 1 ' don't need to send an email here
		exit function
	else
		wscript.echo "Desired default printer is already set as the computer's default printer"
		wscript.echo "No printer changes needed"
		' reset SendEmail to 1, to allow it to send email immediately
		SendEmail = 1
	end if
	wscript.echo

end function

' version 3 functions
function search_for_network_printer()
	wscript.echo 
	wscript.echo "In search_for_network_printer()"
	wscript.echo 
	network_printer = 0
	term = ucase(get_terminal_name)
	if InStr(term,".") then
		wscript.echo "fixing term        : " & term
		slots = split(term,".")
		term = slots(0)
	end if
	term_with_domain = term & Domain
	wscript.echo "final term            : " & term
	wscript.echo "final term with domain: " & term_with_domain
	max = mapping(0)
	wscript.echo "max: " & max
	for i = 1 to int(max)
		if InStr(mapping(i),term) or Instr(mapping(i),term_with_domain) then
			wscript.echo "m:" & mapping(i) & " " & i
			slots = split(mapping(i),",")
			network_ptr = slots(1)
			exit for
		end if
	next
	wscript.echo "*** network ptr:" & network_ptr
	change_default_ptr_v4(network_ptr)
end function

function load_mappings()
	Set objFSO = CreateObject("Scripting.FileSystemObject")
	Set objTextFile = objFSO.OpenTextFile (MappingFile, ForReading)

	i=1
	do while objTextFile.AtEndOfStream <> True
		line = objTextFile.ReadLine
		wscript.echo "f:" & line
		mapping(i) = line
		i = i + 1
	loop

	objTextFile.Close
	
	mapping(0) = i
end function

function extract_host(line)
	'TCP    10.1.44.22:4172        pcoip22:43975          ESTABLISHED	
	answer = ""
	start_looking = 0
	slots = split(line)
	'wscript.echo slots(2)
	for each s in slots
			if start_looking = 1 and InStr(s,":") then
				answer = s
				wscript.echo "ans: " & answer
				exit for
			end if
			if Instr(s,":4172") then
				start_looking = 1
			end if
	next
	if len(answer) > 1 then
		slots = split(answer,":")
		pcoip_host = slots(0)
		wscript.echo "ans2:" & pcoip_host
	end if
	extract_host = pcoip_host
end function

function get_terminal_name()
	set objShell = CreateObject("WScript.Shell")
	set objWshScriptExec = objShell.Exec( NetstatPgmTCP )
	set objStdOut = objWshScriptExec.StdOut

	connected = 0
	while not objStdOut.AtEndOfStream
		data = objStdOut.ReadLine
		if 0 = connected then
			Wscript.echo "netstat:" & data
			if InStr(data,":4172") and InStr(data,"ESTABLISHED") then
				set objStdOut = Nothing
				set objWshScriptExec = Nothing
				set objShell = Nothing

				wscript.echo "pcoip connection detected:" & data

				terminal_host = extract_host(data)
				wscript.echo "h1:" & terminal_host
				get_terminal_name = terminal_host
				exit function
			end if
		end if
	wend

	set objStdOut = Nothing
	set objWshScriptExec = Nothing
	set objShell = Nothing
	wscript.echo "Connected2: " & connected
	get_terminal_name = 0
end function

' return 0 on failure
function change_default_ptr_v4(desired_ptr)
	wscript.echo "aaa : " & desired_ptr
	if len(desired_ptr) > 1 then
		Set objPrinter = CreateObject("WScript.Network")
		objPrinter.AddWindowsPrinterConnection desired_ptr
		objPrinter.SetDefaultPrinter desired_ptr
		Set objPrinter = Nothing
	end if
end function

function change_default_ptr_v3(desired_ptr)
	desired_ptr = ucase(desired_ptr)
	wscript.echo "===================================================="
	wscript.echo "des: _" & desired_ptr & "_"
	found = 0

	' get the pre-existing default printer
	Set objWMIService = GetObject("winmgmts:\\.\root\CIMV2")
	Set colItems = objWMIService.ExecQuery("SELECT * FROM Win32_Printer where Default='True'", "WQL", wbemFlagReturnImmediately + wbemFlagForwardOnly)
	PreExisting = 0
	For Each objItem In colItems
		PreExisting = UCASE(objItem.Name)
		exit for
	next

	Set colItems = objWMIService.ExecQuery("SELECT * FROM Win32_Printer", "WQL", wbemFlagReturnImmediately + wbemFlagForwardOnly)
	For Each objItem In colItems
		wscript.echo "- try: _" & ucase(objItem.Name) & "_"
		if ucase(objItem.Name) = desired_ptr then
			wscript.echo "*** match: _" & desired_ptr & "_"
			found = 1
			if desired_ptr <> PreExisting then
				Set objPrinter = CreateObject("WScript.Network")
				objPrinter.SetDefaultPrinter desired_ptr
				Set objPrinter = Nothing
				exit for
			else
				wscript.echo "*** no changes needed, correct ptr was already default: " & PreExisting
				exit for
			end if
		end if
	Next

	set colItems = Nothing
	set objWMIService = Nothing

	change_default_ptr_v3 = 1
	if 0 = found then
		wscript.echo "xxx no match for: " & desired_ptr
		change_default_ptr_v3 = 0
	end if
end function

' pause a few seconds at initial startup
WScript.Sleep 15 * 1000

load_mappings
email_wait_counter = 0

log_error "Script started.", 1

do
	'version 1&2...
	email_wait_counter = email_wait_counter + 1
	main()
	WScript.Sleep 1 * 900 * 1000  ' pause for 15 minutes, 900 seconds=15 minutes
	if email_wait_counter = 180 then      ' computed
		SendEmail = 1
		email_wait_counter = 1
	end if

loop while True


