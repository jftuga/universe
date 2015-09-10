@echo off
gsort -S 100000 - | uniq -c | gsort -nr
