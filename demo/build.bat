@echo off
setlocal

set bin=python ..\md2toc.py
set blacklist=-b "*toc*" -b "*README*"
set full_depth=--depth -1

%bin% %full_depth% %blacklist% --header README_header.md --footer README_footer.md -o README.md

%bin% %blacklist% --depth 0 -o toc_no_depth.md
%bin% %blacklist% --depth 1 -o toc_1_depth.md
%bin% %blacklist% -w "file1.md" -o toc_file1_only.md
%bin% %blacklist% -b "file1.md" -o toc_file1_excluded.md
%bin% %blacklist% -e "dir2" -o toc_dir2_excluded.md
%bin% %blacklist% --file-emoji ":smile:" --dir-emoji ":rage:" -o toc_changing_emoji.md
