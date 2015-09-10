
opt("MustDeclareVars",1)

#Include <ScreenCapture.au3>
#Include <File.au3>
#Include <Array.au3>
#Include <Array.au3>



Global $Dest = "c:\dl\dropbox\review\"
Global $fname

func get_new_fname($d)
	local $flist, $last, $slots, $i
	$flist = _FileListToarray($d,"*.jpg", 1)
	_ArraySort($flist,0,1)
	$last = $flist[ int($flist[0]) ]
	$slots = StringSplit($last,".")
	$i = int($slots[1]) + 1
	return $i & ".jpg"
endfunc

func trigger()
	$fname = get_new_fname($Dest)
	_ScreenCapture_Capture($Dest & $fname, 210,250,1415,845,False)
	beep(1000,10)
endfunc

hotkeyset("^`", "trigger")
hotkeyset("^q", "trigger")

while(True)
	sleep(200)
wend


