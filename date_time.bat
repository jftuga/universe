@echo off
setlocal

rem native batch file...
for /f "usebackq tokens=1,2,3,4 delims=/ " %%w in (`echo %DATE%`) do set YMD=%%z%%x%%y
for /f "usebackq tokens=1,2,3,4 delims=:." %%x in (`echo %TIME%`) do set HMS=%%x%%y%%z
set NOW=%YMD%_%HMS%

rem external gdate.exe program...
for /f "usebackq" %%g in (`gdate +"%%Y%%m%%d_%%H%%M%%S"`) do set GDATE=%%g


@echo batch : %NOW%
@echo gdate : %GDATE%

rem Use zero-padding when hour is than 10...
for /f "usebackq tokens=1,2,3,4,5,6,7 delims=/:. " %%a in (`echo %DATE% %TIME%`) do if %%e lss 10 (set NOW=%%d%%b%%c_0%%e%%f%%g) else (set NOW=%%d%%b%%c_%%e%%f%%g)
@echo now   : %NOW%
