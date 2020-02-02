@echo off
setlocal

rem arg1: cmd
rem arg2: file glob
rem example: margs.bat code *.yaml
rem result:  code r:\code\a.yaml r:\code\test\b.yaml
rem pipe this result to 'clip' and then right click to paste into cmd prompt

dir %2 /s/b | mawk "{ a =sprintf('%%s %%s',a,$0)} END { printf('%%s %%s\n',p,substr(a,2)) }" p="%1"
