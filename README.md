# md2toc
Generate a TOC(Table Of Contents) from markdown files in the current directory for GitHubber.

## Demo
See [demo](demo) directory.

## Feature
* Filtering target files with white-list and black-list.
* Link to complicated section with explicit anchor name.
  * ex. Japanese section, Marks containing section.
* Inserting emoji.
* Section depth control.
  * ex. No-level, 1-level, All-level.

## Requirements
* Python 2.7
* Windows, Linux or Macintosh.
  * Mainly developed in Windows.

## How to use
0. Create markdown files.
  * If you want to insert hyper-links to TOC, you must write `<a name="(ANCHOR-NAME)">` tag to a section.
  * Ex. `# <a name="howtouse">How to use`
0. Change the current directory to TOC root directory.
0. Do `python md2toc.py (OPTIONS)`

## Usage

```
usage: md2toc.py [-h] [-w [WHITELIST [WHITELIST ...]]]
                 [-b [BLACKLIST [BLACKLIST ...]]]
                 [-e [EXCLUDE_DIR [EXCLUDE_DIR ...]]] [-o OUT] [--depth DEPTH]
                 [-s SPACE] [--file-emoji FILE_EMOJI] [--dir-emoji DIR_EMOJI]
                 [--header HEADER] [--footer FOOTER] [--print-filelist]
                 [--gitbucket]

Create a TOC file from markdown(*.md) files in the current directory.

optional arguments:
  -h, --help            show this help message and exit
  -w [WHITELIST [WHITELIST ...]], --whitelist [WHITELIST [WHITELIST ...]]
                        Markdown files which be white-filtered. You can use a
                        wildcard. (default: [])
  -b [BLACKLIST [BLACKLIST ...]], --blacklist [BLACKLIST [BLACKLIST ...]]
                        Markdown files which be excluded. You can use a
                        wildcard. (default: [])
  -e [EXCLUDE_DIR [EXCLUDE_DIR ...]], --exclude-dir [EXCLUDE_DIR [EXCLUDE_DIR ...]]
                        Folder names which be excluded from scanning files.You
                        CANNOT use a wildcard. (default: [])
  -o OUT, --out OUT     A output TOC filename. (default: index.md)
  --depth DEPTH         Max section depth which be parsed. Type `-1` for using
                        no limits. Type `0` for using no section output.
                        (default: -1)
  -s SPACE, --space SPACE
                        The number of space for list-nesting. (default: 2)
  --file-emoji FILE_EMOJI
                        A emoji of GFM for a markdown file. (default: :memo:)
  --dir-emoji DIR_EMOJI
                        A emoji of GFM for a directory. (default:
                        :file_folder:)
  --header HEADER       Prepend a content of a given markdown filepath.
                        (default: None)
  --footer FOOTER       Append a content of a given markdown filepath.
                        (default: None)
  --print-filelist      [FOR DEBUG] Print target filelist. (default: False)
  --gitbucket           If you use a GitBucket and want to use anchor link.
                        (default: False)
```

## Licence
[MIT](LICENSE)

## Author
[shouh](https://github.com/shouh)
