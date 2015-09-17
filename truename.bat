@echo off

rem use %%k for normal shares and %%j for unc shares
for /f "usebackq tokens=1,2,3" %%i in (`net use^|findstr /i %~d1`) do @echo "%%j%~p1%~n1%~x1"
