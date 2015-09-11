@echo off

rem sumcol.bat
rem -John Taylor
rem Aug-23-2007
rem
rem Computes the numeric sum of a given column of data
rem mawk.exe is from: http://www.klabaster.com/freeware.htm#mawk
rem
rem Example:
rem         cd c:\windows\system32
rem         dir *.dll | findstr /i /e ".dll" | sumcol 4
rem         ----
rem         now compare this to the output of:
rem         dir *.dll | findstr "File(s)"

setlocal

set COL=%1
set FNAME=%2

if not defined COL goto USAGE

:RUN
rem for debugging...
rem mawk.exe "{ gsub(/,/, '', $%COL%); SUM += int($%COL%); print NR' 'SUM} END { print 'sum: 'SUM }" %FNAME%
mawk.exe "{ gsub(/,/, '', $%COL%); SUM += int($%COL%) } END { printf('%%15.0f\n', SUM) }" %FNAME%
goto END

:USAGE
@echo.
@echo Usage:
@echo %0 [ column # ] [ filename ]
@echo    column numbers start at 1
@echo    filename is optional, this will otherwise read from standard-in
@echo.
@echo    you can also use NF for the column #, which means the last column
@echo    (NF-1) means the 2nd to the last column, (NF-2) means the 3rd to the last column, etc.
@echo.
goto END

:END
endlocal
