@echo off
@echo "\\%COMPUTERNAME%\%~d1%~p1%~n1%~x1" | tr : $ 
rem | tr -s \"
