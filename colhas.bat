@echo off
setlocal

set ARG=%1
set WANT_NR=%2
set FNAME=%3

if not defined ARG goto ERROR
if not defined WANT_NR goto STANDARD
rem would NF be a better choice then NR?

if "%WANT_NR%"=="1" goto WITH_NR
goto STANDARD

:WITH_NR
mawk "{ i=0; while(++i<=NF) if(index($i,'%ARG%')) print NR, $i }" %FNAME%
goto END

:STANDARD
mawk "{ i=0; while(++i<=NF) if(index($i,'%ARG%')) print $i }" %FNAME%
goto END

:ERROR
@echo.
@echo %0 [ search-string ] [ 0^|1 ] [ filename ]   (want NR is optional, filename is optional)
@echo.
@echo Locate the search-string in each field of a file,
@echo and only print the line number and that field
@echo.
goto END

:END
endlocal
