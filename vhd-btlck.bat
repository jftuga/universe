@echo off
setlocal

rem vhd-btlck.bat
rem -John Taylor
rem Dec-13-2015
rem
rem Mount and unmount a bitlocker encrypted VHD file as a drive letter
rem Modify VDISK and VHDDRIVE accordingly

set VDISK="C:\example.vhd"
set VHDDRIVE=v:
set TMPFILE=%TEMP%\dpart.%RANDOM%.%RANDOM%.tmp 

set OP=%1
if not defined OP goto USAGE

net session > nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    @echo.
    @echo You did not "Run as Administrator"
    @echo.
    goto END 
)

if "%OP%"=="mount" (

	if exist %VHDDRIVE%\nul (
		@echo.
		@echo Drive already mounted: %VHDDRIVE%
		@echo.
		goto END
	)

	@echo select vdisk file=%VDISK%>> %TMPFILE%
	@echo attach vdisk >> %TMPFILE%

	diskpart.exe /s %TMPFILE%
	del %TMPFILE%

:BITLOCK
	manage-bde.exe -unlock %VHDDRIVE% -password
	if not exist p:\nul goto BITLOCK
	goto END
)

if "%OP%"=="unmount" (
	manage-bde.exe -lock %VHDDRIVE%
	@echo.

	@echo select vdisk file=%VDISK% >> %TMPFILE%
	@echo detach vdisk >> %TMPFILE%

	diskpart.exe /s %TMPFILE%
	del %TMPFILE%
	goto END
)

:USAGE
@echo.
@echo %~n0%~x0 [ mount ^| unmount ]
@echo.
goto END

:END
endlocal
