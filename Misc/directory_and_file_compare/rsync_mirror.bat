@echo off
setlocal
setlocal ENABLEDELAYEDEXPANSION

rem part1
rem copy everything except Music1 
rem src: Elements  dst: Tera
rem
rem part2
rem copy only Music1
rem src: Elements  dst: Slave

set SRC=Elements
set DST=Tera
for /f "usebackq tokens=1,2,3,4,5,6,7 delims=/:. " %%a in (`echo %DATE% %TIME%`) do set NOW=%%d%%b%%c_%%e%%f%%g
set LOG=C:\rsync_mirror\logs\part1_%NOW%.log

for %%d in (d e f g h i j k l m n o p q r s t u v w x y z) do (
	if exist %%d:nul (
		vol %%d: | findstr "%SRC%"
		if not ERRORLEVEL 1 set SRC_DRV=%%d
	)
)

for %%d in (d e f g h i j k l m n o p q r s t u v w x y z) do (
	if exist %%d:nul (
		vol %%d: | findstr "%DST%"
		if not ERRORLEVEL 1 set DST_DRV=%%d
	)
)

if not defined SRC_DRV goto ERR1
if not defined DST_DRV goto ERR2
goto PART1

:ERR1
@echo. >> %LOG%
gdate >> %LOG%
@echo. >> %LOG%
@echo ERROR. >> %LOG%
@echo Source drive not found: %SRC% >> %LOG%
@echo. >> %LOG%
goto END

:ERR2
@echo. >> %LOG%
gdate >> %LOG%
@echo. >> %LOG%
@echo ERROR. >> %LOG%
@echo Destination drive not found: %DST% >> %LOG%
@echo. >> %LOG%
goto END

:PART1
gdate
@echo part1 log file: %LOG%
@echo. >> %LOG%
gdate >> %LOG%
@echo. >> %LOG%
set EXCLUDE=--exclude="System Volume Information" --exclude="$RECYCLE.BIN" --exclude="media/Music1"
rsync -a -v -v -W  %EXCLUDE% /cygdrive/%SRC_DRV%/ /cygdrive/%DST_DRV% >> %LOG% 2>&1
goto PART2

rem ***************************************************************************************************
rem ***************************************************************************************************
rem ***************************************************************************************************

:PART2
set SRC=Elements
set DST=Slave
for /f "usebackq tokens=1,2,3,4,5,6,7 delims=/:. " %%a in (`echo %DATE% %TIME%`) do set NOW=%%d%%b%%c_%%e%%f%%g
set LOG=C:\rsync_mirror\logs\part2_%NOW%.log

for %%d in (d e f g h i j k l m n o p q r s t u v w x y z) do (
	if exist %%d:nul (
		vol %%d: | findstr "%SRC%"
		if not ERRORLEVEL 1 set SRC_DRV=%%d
	)
)

for %%d in (d e f g h i j k l m n o p q r s t u v w x y z) do (
	if exist %%d:nul (
		vol %%d: | findstr "%DST%"
		if not ERRORLEVEL 1 set DST_DRV=%%d
	)
)

if not defined SRC_DRV goto ERR1
if not defined DST_DRV goto ERR2

gdate
@echo part2 log file: %LOG%
@echo. >> %LOG%
gdate >> %LOG%
@echo. >> %LOG%
rsync -a -v -v -W /cygdrive/%SRC_DRV%/media/Music1/ /cygdrive/%DST_DRV%/media/Music1/ >> %LOG% 2>&1
goto END


:END
gdate
endlocal
