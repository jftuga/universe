
#cs 

get_day_from_cal.au3
-John Taylor
Feb-1-2016

Ask the user for a data and save it in YYYY-MM-DD format to the filename given on the
command line.

#ce 

#include <GUIConstantsEx.au3>
#include <WindowsConstants.au3>

Opt("GUIOnEventMode", 1) 
Opt('MustDeclareVars', 1)

Global $g_cal, $g_run, $g_cancel, $fname

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

Func save_date($entry)
    local $fp

	$fp = FileOpen($fname,2)
	FileWriteLine($fp,$entry)
	FileClose($fp)
EndFunc

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

func cancel_program()
    GUIDelete()
    FileDelete($fname)
    exit(173)
endfunc

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

func get_date_from_gui()
    local $tmp , $selected_date

    $tmp = GUICtrlRead( $g_cal )
    $selected_date = StringReplace($tmp,"/","-")
    save_date( $selected_date )
    GUIDelete()
    exit(0)
endfunc


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


Func main()
    if 1 <> $CmdLine[0] then
        MsgBox(16,"Error", "Give output file name on command line." & @CRLF & "This file will contain the selected date.")
        exit
    else
        $fname = $CmdLine[1]
        FileDelete( $fname )
    endif

    Local $hGUI

    $hGUI = GUICreate("Select a day", 400, 300)
    $g_cal = GUICtrlCreateMonthCal("Calendar",4, 4, $WS_BORDER)
    $g_run = GUICtrlCreateButton("Run", 10, 190, 90, 25)
    $g_cancel = GUICtrlCreateButton("Cancel", 100, 190, 90, 25)

    GUISetOnEvent($GUI_EVENT_CLOSE, "cancel_program")
    GUICtrlSetOnEvent($g_cancel, "cancel_program")
    GUICtrlSetOnEvent($g_run, "get_date_from_gui")

    GUISetState(@SW_SHOW)


    while 1
        sleep(111)
    wend

    GUIDelete()
EndFunc

;MsgBox(0,"test 1","test 2")
main()