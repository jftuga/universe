@echo off

rem create a Python virtual environment (venv)
rem https://docs.python.org/3/library/venv.html

set PRJ=%1
if not defined PRJ goto ERR

:RUN
@echo python -m venv %PRJ%
python -m venv %PRJ%
cd %PRJ%
@echo.
@echo Now running:
@echo    Scripts\activate.bat
call Scripts\activate.bat
@echo.
goto END

:ERR
@echo.
@echo Give project name on command line
@echo.
goto END

:END
