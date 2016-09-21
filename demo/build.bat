@echo off
setlocal

set bin=python ..\md2toc.py
set blacklist=-b "*toc*" -b "*README*"
set full_depth=--depth -1
set no_depth=--depth 0

%bin% %full_depth% %blacklist% --header README_header.md --footer README_footer.md -o README.md
