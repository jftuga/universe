#cs

Win_Trans
-John Taylor
Sept-9-2005

Hotkeys to set transparency of active windows

#ce

#notrayicon
Opt ("MustDeclareVars", 1)

Global $hidden_win = ""

HotKeySet("+^1", "On1")    ; shift control 1 ; 10% transparency is useless, so this is a toggle for hide window & show window 
HotKeySet("+^2", "On2")    ; shift control 2
HotKeySet("+^3", "On3")    ; shift control 3
HotKeySet("+^4", "On4")    ; shift control 4
HotKeySet("+^5", "On5")    ; shift control 5
HotKeySet("+^6", "On6")    ; shift control 6
HotKeySet("+^7", "On7")    ; shift control 7
HotKeySet("+^8", "On8")    ; shift control 8
HotKeySet("+^9", "On9")    ; shift control 9
HotKeySet("+^0", "On0")    ; shift control 0

_ReduceMemory()
while 1
	sleep(1000)
wend

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

func On1()
	global $hidden_win
	;MsgBox(0,"Hidden_Win", $hidden_win)
	if $hidden_win == "" then
		$hidden_win = WinGetTitle("")
		if "Program Manager" == $hidden_win then
			$hidden_win = ""
			return
		endif
		WinSetState( $hidden_win, "", @SW_HIDE )
	else
		WinSetState( $hidden_win, "", @SW_SHOW )
		$hidden_win = ""
	endif
endfunc

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

Func _ReduceMemory($i_PID = -1)
    If $i_PID <> -1 Then
        Local $ai_Handle = DllCall("kernel32.dll", 'int', 'OpenProcess', 'int', 0x1f0fff, 'int', False, 'int', $i_PID)
        Local $ai_Return = DllCall("psapi.dll", 'int', 'EmptyWorkingSet', 'long', $ai_Handle[0])
        DllCall('kernel32.dll', 'int', 'CloseHandle', 'int', $ai_Handle[0])
    Else
        Local $ai_Return = DllCall("psapi.dll", 'int', 'EmptyWorkingSet', 'long', -1)
    EndIf
    
    Return $ai_Return[0]
EndFunc;==> _ReduceMemory()

