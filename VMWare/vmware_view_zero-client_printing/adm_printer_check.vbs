'
' adm_printer_check.vbs
' Aug-5-2010
' -John Taylor
' 
' 
' This script "cleans up" the Win XP's printers section by deleting all of
' the copy 1, copy 2, etc. printers and renaming the online printer to a
' more sane name.
'
' For example,

' Dell 2330dn (offline)                      1st entry
' Dell 2330dn (Copy 1)                       2nd
' Dell 2330dn (Copy 2) offline               3rd

' will get "fixed" so that the 1st & 3rd entries are deleted and the 2nd
' entry is renamed to just Dell 2330dn.

' This script it run as a Scheduled Task by SYSTEM at boot time (startup).
' Run: c:\Windows\System32\cscript.exe //B //Nologo c:\bin\adm_printer_check.vbs
' Start in: c:\bin
' Run as: SYSTEM  (no password)
' Schedule Task: At System Startup
' Uncheck "Stop the task if it runs for X hours"
'
' Adjust the preferred_name hash-table as needed.
'
' This script runs forever, checking the printers every 2 minutes.

'

On Error Resume Next
		
Const ErrorLogPath = "\\MyServer\apps\terminal_errors"

Const wbemFlagReturnImmediately = &h10
Const wbemFlagForwardOnly = &h20
Const ForAppending = 8

Set preferred_name = CreateObject("Scripting.Dictionary")
preferred_name.Add "Dymo", "DYMO LabelWriter"
preferred_name.Add "Dell", "Dell 2330dn Laser Printer"

function log_error(msg)
	Set WshNetwork = WScript.CreateObject("WScript.Network")
	ComputerName = WshNetwork.ComputerName 

	msg = ComputerName & vbTab & Date & vbTab & Time & vbTab & msg

	Set objFSO = CreateObject("Scripting.FileSystemObject")
	fname = ErrorLogPath & "\" & ComputerName & ".tsv"
	Set objTextFile = objFSO.OpenTextFile (fname, ForAppending, True)
	objTextFile.WriteLine(msg)
	objTextFile.Close
end function

function change_default_ptr(ptr)
	Set objPrinter = CreateObject("WScript.Network")
	objPrinter.SetDefaultPrinter ptr
end function

function delete_ptr(comp, ptr)
	Set o = GetObject("winmgmts:\\" & comp & "\root\cimv2")
	Set candidates =  o.ExecQuery ("Select * from Win32_Printer Where Name='" & ptr & "'")
	for each objptr in candidates
		objptr.Delete_
	next
end function

function rename_printers(comp)
	prefer = preferred_name.Keys

	Set o = GetObject("winmgmts:\\" & comp & "\root\cimv2")
	Set candidates = o.ExecQuery("SELECT * FROM Win32_Printer where Network=FALSE ", "WQL", wbemFlagReturnImmediately + wbemFlagForwardOnly)

	wscript.echo
	wscript.echo
	wscript.echo "Printers to rename (if any)"
	wscript.echo "==========================="

	for each objptr in candidates
		PtrName = objPtr.Name
		for each ptrkey in prefer
			if InStr(1, PtrName, ptrkey, vbTextCompare) > 0 then
				good_name = preferred_name.Item(ptrkey)
				if good_name <> PtrName then
					wscript.echo "Rename from: " & PtrName  & "    to: " & good_name
					objptr.RenamePrinter( good_name )
					exit for
				end if
			end if
		next
	next
end function

function modify_service(action)
	strServiceName = "Spooler"
	Set objWMIService = GetObject("winmgmts:{impersonationLevel=impersonate}!\\.\root\cimv2")
	Set colListOfServices = objWMIService.ExecQuery ("Select * from Win32_Service Where Name ='" & strServiceName & "'")
	For Each objService in colListOfServices
		if "start" = action then
			objService.StartService()
			WScript.Sleep 300
			objService.StartService()
			WScript.Sleep 400
			objService.StartService()
			WScript.Sleep 500
			objService.StartService()
			WScript.Sleep 200
		end if
		if "stop" = action then
			objService.StopService()
		end if
	Next
end function

function old_spooler_files
	spooler_path = "C:\Windows\System32\spool\PRINTERS"
	min = 99999
	count = 0
	wscript.echo 
	wscript.echo "old spooler files (age in minutes) (if any)"
	wscript.echo "==========================================="


	Set fso = CreateObject("Scripting.FileSystemObject")
	Set oFolder = fso.GetFolder(spooler_path)

	for each oFile in oFolder.files
		curr = DateDiff("n", oFile.DateCreated,Now)
		wscript.echo curr
		if curr < min then
			min = curr
		end if
		count = count + 1
	next 
	wscript.echo "-  Job Count: " & count
	if count > 0 then
		wscript.echo "-  Minimum age: " & min
	end if
	wscript.echo 
	wscript.echo 
	if count > 0 and min > 5 then
		wscript.echo "Stopping Spooler"
		modify_service("stop")
		WScript.Sleep 500

		wscript.echo "-  Deleting Spooler files"
		for each oFile in oFolder.files
			wscript.echo "   " & oFile.Name
			fso.DeleteFile spooler_path & "\" & oFile.Name, True
		next

		WScript.Sleep 500
		wscript.echo "Starting Spooler"
		modify_service("start")
	end if

	wscript.echo 
	wscript.echo 
end function

function main()
	If Wscript.Arguments.Count = 0 Then
		strComputer = "."
	else
		strComputer = Wscript.Arguments(0)
	end if

	
	Set offline_dict = CreateObject("Scripting.Dictionary")
	Set objWMIService = GetObject("winmgmts:\\" & strComputer & "\root\CIMV2")
	Set colItems = objWMIService.ExecQuery("SELECT * FROM Win32_Printer where Network=FALSE", "WQL", wbemFlagReturnImmediately + wbemFlagForwardOnly)
	wscript.echo "Default" & vbTab & "Status" & vbTab & "Name"
	wscript.echo "=======" & vbTab & "======" & vbTab &  "==============================="
	
	For Each objItem In colItems
		PtrName = objItem.Name
		IsDefaultPtr = objItem.Default
		WorkOffline = objItem.WorkOffline
	
		PtrStatus = "Online"
		if True = WorkOffline then
			PtrStatus = "Offline"
			prefer = preferred_name.Keys
			for each ptrkey in prefer
				if InStr(1, PtrName, ptrkey, vbTextCompare) > 0 then
					offline_dict.Add PtrName, PtrName
					exit for
				end if
			next
		end if
	
		DefaultPtr = "No"
		if True = IsDefaultPtr then
			DefaultPtr = "Yes"
		end if
	
		wscript.echo DefaultPtr & vbTab & PtrStatus & vbTab & PtrName
	Next
	
	wscript.echo
	wscript.echo

	if len(strComputer) > 1 then
		wscript.echo "Can not change printers for remote computers, quitting"
		wscript.quit
	end if

	old_spooler_files

	if offline_dict.Count > 0 then
		wscript.echo "Offline printers to delete"
		wscript.echo "=========================="
		offline_array = offline_dict.Items
		for each ptr in offline_array
			wscript.echo ptr
			delete_ptr strComputer, ptr
		next
	else
		wscript.echo "There are no offline printers to delete"
		wscript.echo
	end if

	rename_printers strComputer

	wscript.echo
end function

' pause a few seconds at initial startup
WScript.Sleep 12 * 1000

do
	main()
	WScript.Sleep 2 * 60 * 1000  ' 2 minutes
loop while True


