@echo off
setlocal

rem possible formatters: [default=TerminalFormatter]
rem img.BmpImageFormatter img.GifImageFormatter html.HtmlFormatter img.PngImageFormatter img.JpgImageFormatter
rem rtf.RtfFormatter terminal256.Terminal256Formatter terminal.TerminalFormatter terminal256.TerminalTrueColorFormatter
rem
rem possible styles:
rem default emacs friendly colorful autumn murphy manni monokai perldoc pastie borland trac native fruity bw
rem vim vs tango rrt xcode igor paraiso-light paraiso-dark lovelace algol algol_nu arduino rainbow_dash abap

set OUTPUT=%TEMP%\%~n1--hless.%RANDOM%.htm
pygmentize -f html -O full,style=default,linenos=1 -g -o %OUTPUT% %1
if exist %OUTPUT% (
    %OUTPUT% && del %OUTPUT%
)

