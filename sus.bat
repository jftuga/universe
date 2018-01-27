@echo off
gsort -S 3000000 - | uniq -c | gsort -n -k1,1r -k2,2 -S 3000000
