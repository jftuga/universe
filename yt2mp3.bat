@echo off
setlocal

rem converts a YouTube video to local MP3 file

set URL=%1
if not defined URL goto ERROR

:RUN
h:\bin\youtube-dl.exe -t --extract-audio --audio-format mp3 -k "%URL%"
goto END

:ERROR
@echo.
@echo Give YouTube URL on command line, within double-quotes
@echo.
goto END

:END
endlocal
