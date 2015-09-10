#cs

udp.au3
send arbitrary UDP packets
-John Taylor
Feb-01-2011

#ce

Opt("MustDeclareVars",1)

global const $VERSION = "20110201.1152"
global $sock, $payload, $payload_size
global $status, $i
global const $VK_CAPITAL = 0x14
global $packet_count=0            ; number of packets sent by this program
global $total_bytes = 0           ; number of bytes sent by this program


;; functions

func Usage() 
	MsgBox(0,"Usage for version: " & $VERSION, "Sends UDP packets with a given interval." & @CRLF & "Press CAPS LOCK to end the program." & @CRLF & @CRLF & @CRLF & _
		@ScriptName & " [max packet size] [dest ip] [dest udp port] [interval] [ 0|1 ]" & @CRLF & @CRLF & "interval is in milliseconds" & @CRLF & "last arg: 0=normal, 1=broadcast on 255.255.255.255")
endfunc

func Cleanup()
	UDPCloseSocket($sock)
	UDPShutdown()
endfunc

func _GetCapsLock()
	Local $ret
	$ret = DllCall("user32.dll","long","GetKeyState","long",$VK_CAPITAL)
	Return $ret[0]
endfunc


;; main program execution begins below

if $CmdLine[0] <> 5 then
	Usage()
	exit
endif

global $max = $CmdLine[1]
global $ip = $CmdLine[2]
global $port = int($CmdLine[3])
global $interval = int($CmdLine[4])
global $bcast = int($CmdLine[5])

If _GetCapsLock() Then
	MsgBox(0,"Error", "Turn off CAPS LOCK and rerun program.")
	exit
endif

UDPStartup()

; open UDP connection
$sock = UDPOpen($ip,$port,$bcast)
If @error <> 0 Then 
	MsgBox(0,"Error", "UDPOpen() failed on address " & $ip)
	exit
else
	OnAutoItExitRegister("Cleanup")
endif

; udp packet sending loop, continue until caps lock is pressed
while true
	If _GetCapsLock() Then ExitLoop

	; create a random payload for each packet of size $packet_size
	$payload_size = Random(1,$max,1)
	$i=0
	while $i < $payload_size
		$payload &= Chr(Random(Asc("a"), Asc("z"), 1))
		$i += 1
	wend
	;MsgBox(0,"args", "m:" & $max & "   i:" & $ip & "   p:" & $port & "   b:"  & $bcast & @CRLF & "p_size:" & $payload_size & @CRLF & "payload:" & @CRLF & $payload)

	; actually send the UDP packet with payload
	$status = UDPSend($sock, $payload)
	if @error then
		MsgBox(0, "Error", "Progam stopped." & @CRLF & "Error while sending UDP packet, error # " & @error & @CRLF & @CRLF & "See http://bit.ly/hqLitA for explanation of error code.")
		exitloop
	else
		sleep( $interval )
		$total_bytes += $status
		$packet_count += 1
	endif
wend

MsgBox(0, "Results", "Sent " & $total_bytes & " total bytes (" & $packet_count & " packets) to " & $ip & " on port " & $port & _
	@CRLF & @CRLF & "This dialog box will automatically close in 5 seconds.", 5)

;; now the Cleanup function will be called
;; end of script

