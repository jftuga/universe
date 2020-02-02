@echo off
setlocal

rem arg1: cmd
rem arg2: file glob
rem example1 : margs.bat code *.yaml
rem result:  code r:\code\a.yaml r:\code\test\b.yaml
rem pipe this result to 'clip' and then right click to paste into cmd prompt
rem or pipe straight to cmd
rem
rem example 2: margs.bat "zip -9r test.zip" *.bat | cmd

dir %2 /s/b | mawk "{ a =sprintf('%%s %%s',a,$0)} END { printf('%%s %%s\n',p,substr(a,2)) }" p=%1
