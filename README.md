# md2toc
Generate a TOC(Table Of Contents) from markdown files in the current directory for GitHubber.

## Demo
See [demo](demo) directory.

## Feature
* Filtering target files with white-list and black-list.
* Link to complicated section with explicit anchor name.
  * ex. Japanese section, Marks containing section.
* Inserting emoji.
* Section depth control
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
  * 

**NOTICE:** md2toc.py must be execute in TOC root directory like this.

* :o: `python md2toc.py (OPTIONS)`
* :x: `python dir\md2toc.py (OPTIONS)`
* :x: `python ..\md2toc.py (OPTIONS)`

## Licence
[MIT](LICENSE)

## Author
[shouh](https://github.com/shouh)
