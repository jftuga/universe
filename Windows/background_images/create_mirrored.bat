@echo off
setlocal

rem create_mirrored.bat
rem May-2-2012
rem
rem This batch file uses ImageMagick's convert.exe to create mirrored
rem background images suitable for dual monitors.
rem
rem This is good for a set of scenic backgrounds.  On Windows 7, set the 
rem Picture Position to Tile

rem this is an optional special effect...
rem set DITHER=-channel All -random-threshold 0x100%%

mkdir mirrored 2> nul
mkdir combined 2> nul

rem create a mirrored image
for %%f in (*.jpg) do (
	convert %%f -flop %DITHER% mirrored\mirrored_%%f
)


rem append mirrored image to the left of the original image
for %%f in (*.jpg) do (
	convert %%f mirrored\mirrored_%%f +append combined\combined_%%f
)

@echo.
@echo.
@echo Please review the .\combined folder for the results.
@echo.

:END
endlocal

