@echo off
setlocal

set TMP=c:\temp\urlname.%RANDOM%RANDOM%.txt
@echo %~f1 | grep -c -i t: > %TMP%
set /p LAME=<%TMP%
if "%LAME%" == "1" goto NOWAY

@echo.
@echo file:///%~f1|sed -e "s,\\,/,g" -e "s/ /%%20/g"
@echo.
goto END

:NOWAY
@echo.
@echo You have T: in your URL
@echo Did you mean:  "S:\Departmental\Information Technology"
@echo.
goto END

:END
del %TMP% 2> nul
endlocal

