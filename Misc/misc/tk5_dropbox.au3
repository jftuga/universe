
opt("MustDeclareVars",1)

#Include <ScreenCapture.au3>
#Include <File.au3>
#Include <Array.au3>
#Include <Array.au3>

Global $Dest, $fname, $slots
Global $szDrive, $szDir, $szFName, $szExt
$slots = _PathSplit(@AutoItExe, $szDrive, $szDir, $szFName, $szExt)
$Dest = $slots[1] & $slots[2]

func get_new_fname($d)
	local $flist, $tmp, $last, $slots, $i, $tmp
	$flist = _FileListToarray($d,"*.jpg", 1)
	_ArrayDelete($flist,0)
	$tmp = _FileListToarray($d,"*.png", 1)
	_ArrayDelete($tmp,0)
	_ArrayConcatenate($flist,$tmp)
	_ArraySort($flist,0)

	if ubound($flist) == 0 then
		return "100"
	endif

	$tmp = ubound($flist) - 1
	$last = $flist[$tmp]
	$slots = StringSplit($last,".")
	$i = int($slots[1]) + 1
	return $i
endfunc

func trigger_question()
	local $current
	$fname = get_new_fname($Dest)
	$current = $fname & ".0.jpg"
	;MsgBox(0,"Q", $current)
	_ScreenCapture_Capture($Dest & $current, 210,250,1415,845,False)
	beep(1000,10)
endfunc

func trigger_answer()
	local $tmp, $current
	$tmp = $fname & ".0.jpg"
	if not fileexists($tmp) then
		MsgBox(0,"Error", "Question file does not exist: " & $tmp)
		return
	endif
	$current = $fname & ".1.jpg"
	;MsgBox(0,"A", $current)
	_ScreenCapture_Capture($Dest & $current, 210,250,1415,845,False)
	beep(1000,10)
endfunc

hotkeyset("^q", "trigger_question")
hotkeyset("^a", "trigger_answer")

while(True)
	sleep(200)
wend

