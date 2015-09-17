@echo off

rem use %%k for normal share names and %%j for DFS share names such as \\my.domain\apps
for /f "usebackq tokens=1,2,3" %%i in (`net use^|findstr /i %~d1`) do @echo "%%j%~p1%~n1%~x1"
