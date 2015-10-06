@echo off
setlocal

rem see also: http://social.technet.microsoft.com/wiki/contents/articles/8484.how-to-easily-change-a-dhcp-s-scope-subnet.aspx

set SVR=%1
if not defined SVR goto ERR1
set SCOPE=%2
if not defined SCOPE goto ERR1

:RUN
set OUT=scope_%SVR%_%SCOPE%.txt
netsh dhcp server \\%SVR% scope %SCOPE% dump > %OUT%
@echo.
dir | findstr /i "%OUT%"
@echo.
goto END


:ERR1
@echo.
@echo 1) Give DHCP server name on command-line, without leading backslashes
@echo 2) Give scope name on command-line
@echo.
@echo Example:
@echo get_scope.bat svr1 10.0.1.0
@echo.
goto END


:END
endlocal