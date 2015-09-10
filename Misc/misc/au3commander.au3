;
; au3commander.au3
; John Taylor
; last updated: May-04-2012
;
; an assorted set of hot-keys for various tasks
;
; use ctrl-comma for help

#NoTrayIcon

Opt("MustDeclareVars",1)
Opt("SendCapslockMode",0)

global $n = 10
global $hidden_win = ""
global $fs_title = "FastStone Editor"
global $memred_loop =  240 ; Run _ReduceMemory() every two minutes w/ a sleep time of 500

Func _ReduceMemory($i_PID = -1)
    If $i_PID <> -1 Then
        Local $ai_Handle = DllCall("kernel32.dll", 'int', 'OpenProcess', 'int', 0x1f0fff, 'int', False, 'int', $i_PID)
        Local $ai_Return = DllCall("psapi.dll", 'int', 'EmptyWorkingSet', 'long', $ai_Handle[0])
        DllCall('kernel32.dll', 'int', 'CloseHandle', 'int', $ai_Handle[0])
    Else
        Local $ai_Return = DllCall("psapi.dll", 'int', 'EmptyWorkingSet', 'long', -1)
    EndIf
    
    Return $ai_Return[0]
EndFunc

Func _GetCapsLock()
	Local $ret
	$ret = DllCall("user32.dll","long","GetKeyState","long",0x14)
	Return $ret[0]
EndFunc

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

func fsc_resize()
	local $tmp, $slots, $pos, $rv, $msg
	local $adder_width, $adder_height
	local $current_width, $current_height
	local $new_width, $new_height

	$rv = WinActivate($fs_title,"")
	if 0 == $rv then
		return
	else
		send("{CAPSLOCK OFF}")
		sleep(50)
	endif

	$tmp = StringLeft(@ScriptName,StringLen(@ScriptName)-4)
	$slots = StringSplit($tmp,"-")
	if ubound($slots) <> 4 then
		$msg = ""
		$msg &= "Rename " & @ScriptName & " to " & @ScriptName & "-w-h.exe" & @CRLF
		$msg &= "where w,h are additional width, height needed for FSCapture" & @CRLF & @CRLF
		$msg &= "Good values to try are:" & @CRLF
		$msg &= "28-140" & @CRLF
		$msg &= "36-158" & @CRLF
		MsgBox(16,"Error",$msg)
		return
	endif

	$adder_width = $slots[2]
	$adder_height = $slots[3]
	$pos = WinGetPos($fs_title,"")
	
	; pull up Resize Window
	ControlSend($fs_title,"", "TImageEnView1", "^r")
	sleep(50)
	
	; Resize - width input field
	ControlFocus("Resize", "", "TEdit2")
	sleep(50)
	ControlSend("Resize", "", "TEdit2", "^c")
	sleep(10)
	$current_width = ClipGet()
	
	; Resize - height input field
	ControlFocus("Resize", "", "TEdit1")
	sleep(50)
	ControlSend("Resize", "", "TEdit1", "^c")
	sleep(10)
	$current_height = ClipGet()

	; close Resize Window
	ControlSend("Resize", "", "TEdit2", "{ESC}")
	sleep(50)
	
	$new_width = $current_width + $adder_width
	$new_height = $current_height + $adder_height
	
	WinMove($fs_title,"",$pos[0],$pos[1],$new_width,$new_height)
endfunc

func edit()
	local $fname
	$fname = clipget()
	if StringLen($fname) < 2 then
		MsgBox(0,"GVim Edit Error", "Illegal file name: " & $fname)
		return
	endif

	Run("gvim.exe " & $fname)
	_ReduceMemory()
endfunc

func editempty()
	Run("gvim.exe")
	_ReduceMemory()
endfunc

func help()
	local $msg = ""
	$msg &= "ctrl ,                 ==  display this window" & @CRLF
	$msg &= @CRLF
	$msg &= "ctrl ~                ==  edit filename (on clipboard) with gvim" & @CRLF
	$msg &= "ctrl `                 ==  edit empty file with gvim" & @CRLF
	$msg &= "alt `                   ==  open dnsstuff.com for address on clipboard" & @CRLF
	$msg &= "ctrl-shift 2-10  == set window opacticty 20% - 90%, 0 = 100%" & @CRLF
	$msg &= "ctrl .                ==  open igate in Firefox" & @CRLF
	$msg &= "ctrl '                ==  swap focused window to other monitor" & @CRLF
	$msg &= "ctrl :/;              ==  toggle on: off; a window to 'always on top'" & @CRLF
	$msg &= @CRLF
	$msg &= @CRLF
	$msg &= "HKLM\Software\Microsoft\Windows\CurrentVersion\Run"
	$msg &= @CRLF
	MsgBox(0, "AU3 Commander Hot Keys " & $memred_loop, $msg, $n)
	_ReduceMemory()
endfunc

func dns()
	local $ip = ClipGet()
	ShellExecute("http://private.dnsstuff.com/tools/ipall.ch?ip=" & $ip)
	_ReduceMemory()
endfunc

func fgate()
	local $pgm = "C:\temp\FirefoxPortable\FirefoxPortable.exe"
	local $url = "https://igate/"
	if not fileexists( $pgm ) then
		MsgBox(0,"Error","Path not found: " & $pgm)
	else
		Run( $pgm & " " & $url )
	endif
	
	_ReduceMemory()
endfunc

Func monitor_resolutions()
	local $wmi_svc, $slots, $monitor
	local $h, $v
	local $i
	local $results[16][2]

	local $debug = 0

	$wmi_svc = ObjGet("winmgmts:\\.\root\CIMV2")
	if "" == $wmi_svc then
		if 1 == $debug then MsgBox(0,"WMI Error", "Can connect to WMI service")
		return -1
	endif

	$slots = $wmi_svc.ExecQuery("SELECT CurrentHorizontalResolution,CurrentVerticalResolution FROM Win32_VideoController", "WQL", (0x10 + 0x20) )

	if Not IsObj( $slots ) then 
		if 1 == $debug then MsgBox(0, "WMI Error", "No WMI objects found")
		return -2
	endif

	; count the number of monitors and
	; iterate through each monitor and populate the $results array
	$i = 0
	for $monitor in $slots
		$h = int($monitor.CurrentHorizontalResolution)
		$v = int($monitor.CurrentVerticalResolution)
		if $h <= 1 or $v <= 1 then ContinueLoop

		$i += 1
		if 1 = $debug then MsgBox(0, "Monitor " & $i, "Resolution : " & $h & "x" & $v)

		$results[$i][0] = $h
		$results[$i][1] = $v
	next
	$results[0][0] = $i

	return $results
EndFunc

func monswap()
	local $mon = monitor_resolutions()
	local $split = $mon[1][0] - 8
	local $win = WinGetPos("")
	local $new_x = $win[0]
	local $dest_mon_num = 0

	if($win[0] < $split ) then
		$new_x = $win[0] + $split
		$dest_mon_num = 2
	else
		$new_x = $win[0] - $split
		$dest_mon_num = 1
	endif
	WinMove("","", $new_x,$win[1])

	; if window width is greater than monitor width on the target monitor,
	; set window width to the size of the target monitor's width
	$win = WinGetPos("")
	if( $win[2] > $mon[$dest_mon_num][0] ) then
		winmove("","", $win[0],$win[1],$mon[$dest_mon_num][0])
	endif

	; TODO:
	; After swapping a windows, check to see:
	; 1) for Monitor #1, that the left side of the window is not bleeding over onto Monitor #2
	; 2) for Monitor #2, that the left side of the window is not past the edge of the screen

	_ReduceMemory()
endfunc

func enableontop()
	local $w
	$w = WinGetTitle("[active]")
	WinSetOnTop($w, "", 1 )
	_ReduceMemory()
endfunc

func disableontop()
	local $w
	$w = WinGetTitle("[active]")
	WinSetOnTop($w, "", 0 )
	_ReduceMemory()
endfunc

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

func On2()
	set_win_trans( .20 * 255 )
endfunc

func On3()
	set_win_trans( .30 * 255 )
endfunc

func On4()
	set_win_trans( .40 * 255 )
endfunc

func On5()
	set_win_trans( .50 * 255 )
endfunc

func On6()
	set_win_trans( .60 * 255 )
endfunc

func On7()
	set_win_trans( .70 * 255 )
endfunc

func On8()
	set_win_trans( .80 * 255 )
endfunc

func On9()
	set_win_trans( .90 * 255 )
endfunc

func On0()
	set_win_trans( 255 )
endfunc

func set_win_trans($t)
	WinSetTrans(WinGetTitle(""),"", int($t))
	_ReduceMemory()
endfunc

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

hotkeyset("^,", "help")
hotkeyset("^~", "edit")
hotkeyset("^`", "editempty")
hotkeyset("!`", "dns")
hotkeyset("^.", "fgate")
hotkeyset("^'", "monswap")
hotkeyset("^:", "enableontop")
hotkeyset("^;", "disableontop")

HotKeySet("+^2", "On2")    ; shift control 2
HotKeySet("+^3", "On3")    ; shift control 3
HotKeySet("+^4", "On4")    ; shift control 4
HotKeySet("+^5", "On5")    ; shift control 5
HotKeySet("+^6", "On6")    ; shift control 6
HotKeySet("+^7", "On7")    ; shift control 7
HotKeySet("+^8", "On8")    ; shift control 8
HotKeySet("+^9", "On9")    ; shift control 9
HotKeySet("+^0", "On0")    ; shift control 0

help()
$n=45

_ReduceMemory()
while 1
	if 0 == $memred_loop then
		_ReduceMemory()
		$memred_loop = 240
	endif
	$memred_loop -= 1

	if WinActive($fs_title,"") <> 0 and 1 == _GetCapsLock() then
		fsc_resize()
	endif
	sleep(500)
wend


