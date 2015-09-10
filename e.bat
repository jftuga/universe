@echo off
setlocal

set SHELL=C:\WINDOWS\explorer.exe

set DEST=%1
if not defined "DEST" goto DEFAULT 

:DEFAULT
%SHELL% .
goto END

%SHELL% %DEST%
:END

endlocal
