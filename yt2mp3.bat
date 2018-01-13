@echo off
setlocal enabledelayedexpansion

:LOOP
if "%~1" neq "" (
	@echo.
	@echo =====================================================================
	@echo %1 
	@echo =====================================================================
	@echo.
	youtube-dl.exe -k -x --audio-format mp3 --audio-quality 2 %1
	shift
	goto :LOOP
)


