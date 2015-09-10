@echo off
for /f "usebackq tokens=1,2,3" %%i in (`net use^|findstr /i %~d1`) do @echo "%%k%~p1%~n1%~x1"
