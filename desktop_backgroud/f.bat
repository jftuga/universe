@echo off
setlocal

for %%f in (*.jpg) do (
	@echo convert %%f -flop %%DITHER%% mirrored\mirrored_%%f
	rem echo convert %%f mirrored\mirrored_%%f +append combined\combined_%%f
)
