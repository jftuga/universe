@echo off
setlocal


mawk -F"{" "$0 ~ /\{/ {print $2'\t'$1}" %1 | tr -d "}" | gsort -n
