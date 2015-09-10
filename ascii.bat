@echo off

c:\Python26\python.exe h:\bin\ascii_py.py | egrep -i --binary-files=text "hex|===|%1"
