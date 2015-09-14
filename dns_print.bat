@echo off
setlocal

set DOMCOM=%LOGONSERVER%

for /f "usebackq tokens=1,2,3,4,5,6,7 delims=/:. " %%a in (`echo %DATE% %TIME%`) do set NOW=%%d%%b%%c_%%e%%f%%g

set OUT=dns_export_%NOW%.txt
rem dnscmd %DOMCOM:~2% /zoneexport %USERDNSDOMAIN% %OUT%
dnscmd %DOMCOM% /zoneexport %USERDNSDOMAIN% %OUT%

@echo %NOW%
@echo.
mawk "{printf('%%s,%%s\n',$NF,$1)}" \\%DOMCOM%\c$\windows\system32\dns\%OUT% | grep 172.16| tr "[A-Z]" "[a-z]" | gsort +1 | egrep -v "@|ws-broker|msdcs|age:" > dns_%NOW%.csv

del \\%DOMCOM%\c$\windows\system32\dns\%OUT%

:END
dir dns_%NOW%.csv | grep %NOW%

endlocal

