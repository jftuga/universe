@echo off
setlocal

set COUNT=0
set TOTAL=5

:LOOP
set /a COUNT=%COUNT% + 1
@echo %RANDOM%	%RANDOM%	%RANDOM%	%RANDOM%	%RANDOM%	%RANDOM%
if %COUNT% EQU %TOTAL% goto END
goto LOOP

:END
endlocal
