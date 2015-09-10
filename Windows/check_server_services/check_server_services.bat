@echo off
setlocal

rem batch file wrapper is for the check_server_services.ps1 script
rem run this from the Task Scheduler each morning

set PS=C:\WINDOWS\system32\windowspowershell\v1.0\powershell.exe
set MYCMD=C:\check_server_services\check_server_services.ps1

%PS% -Command "& '%MYCMD%' "
