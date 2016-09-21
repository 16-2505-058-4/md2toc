# coding:utf-8

import os
import fnmatch

class FileUtil:
    @staticmethod
    def get_directory(path):
        return os.path.dirname(path)

    @staticmethod
    def get_filename(path):
        return os.path.basename(path)

    @staticmethod
    def get_basename(path):
        return os.path.splitext(FileUtil.get_filename(path))[0]

    @staticmethod
    def get_extension(path):
        return os.path.splitext(FileUtil.get_filename(path))[1]

    @staticmethod
    def exists(path):
        return os.path.exists(path)

    @staticmethod
    def write(filepath, string_list):
        with open(filepath, 'w') as f:
            f.writelines([elm+'\n' for elm in string_list])

    @staticmethod
    def read(filepath):
        with open(filepath, 'r') as f:
            contents = f.readlines()
        return [line[:-1] for line in contents if line[-1]=='\n']

class FileWalker:
    def __init__(self, basedir=os.getcwd(), exclude_dirs=[]):
        self._basedir = basedir

        os.path.abspath(os.path.dirname(__file__))

        self._filelist = []
        for path, dirnames, filenames in os.walk(basedir):
            for filename in filenames:
                fullpath = os.path.join(path, filename)
                if self._apply_dir_exclusion(exclude_dirs, fullpath):
                    continue
                self._filelist.append(fullpath)

    def _apply_dir_exclusion(self, exclude_dirs, target_filename):
        for exclude_dir in exclude_dirs:
            if target_filename.find('{0}{1}'.format(exclude_dir, os.sep))!=-1:
                return True
        return False

    def get_filelist(self):
        return self._filelist

    def exclude_all(self, patterns):
        for pattern in patterns:
            self.exclude(pattern)

    def exclude(self, pattern):
        remove_targets = []
        for filepath in self._filelist:
            filename = FileUtil.get_filename(filepath)
            if fnmatch.fnmatchcase(filename, pattern):
                remove_targets.append(filepath)

        for remove_target in remove_targets:
            self._filelist.remove(remove_target)

    def whiltefilter_all(self, patterns):
        for pattern in patterns:
            self.whitefilter(pattern)

    def whitefilter(self, pattern):
        remove_targets = []
        for filepath in self._filelist:
            filename = FileUtil.get_filename(filepath)
            if not fnmatch.fnmatchcase(filename, pattern):
                remove_targets.append(filepath)

        for remove_target in remove_targets:
            self._filelist.remove(remove_target)

    def cut_basedir(self):
        basedir_len = len(self._basedir)
        for i in range(len(self._filelist)):
            self._filelist[i] = self._filelist[i][basedir_len:]
            if self._filelist[i][0]=='\\' or self._filelist[i][0]=='/':
                self._filelist[i] = self._filelist[i][1:]

    def separator_win2lin(self):
        for i in range(len(self._filelist)):
            self._filelist[i] = self._filelist[i].replace('\\','/')

    def separator_lin2win(self):
        for i in range(len(self._filelist)):
            self._filelist[i] = self._filelist[i].replace('/','\\')

class TOC:
    def __init__(self, filelist, basedir=os.getcwd(), max_sub_depth=-1, indent_unit=2, use_gitbucket_mode=False):
        # inputs
        self._basedir = basedir
        self._filelist = filelist
        self._indent_unit = indent_unit
        self._use_gitbucket_mode = use_gitbucket_mode

        # output
        self._ret_lines = []

        self._max_sub_depth = max_sub_depth # 負数なら制限無し.

        # statuses
        self._current_parsee_filepath = None
        self._is_in_codehilight = False

    def get_lines(self):
        return self._ret_lines

    # append and prepend
    # ------------------

    def append(self, s):
        self._ret_lines.append(s)

    def prepend(self, s):
        self._ret_lines.insert(0, s)

    # parse
    # -----

    def parse(self):
        self._parse_files(self._filelist)

    def _parse_files(self, filelist):
        for filepath in filelist:
            self.append('* [{0}]({1})'.format(
                    filepath, self._filepath2linkstring(filepath)))
            self._current_parsee_filepath = filepath
            self._parse_file(filepath)

    def _parse_file(self, filepath):
        print 'reading {0}...'.format(filepath),
        contents = FileUtil.read(os.path.join(self._basedir, filepath))
        print 'fin.'

        print 'parsing {0}...'.format(filepath),
        for line in contents:
            self._parse_line(line)
        print 'fin.'

    def _parse_line(self, line):
        # skip a blank line.
        if len(line)<=1:
            return
        if line=='\n':
            return

        # Do not interpret a section in a code hilight.
        #
        # ## Sample   <=== Do interpret
        #
        # ```python
        # # comment   <=== Do not interpret!
        # import os
        # ...
        # ```
        if len(line)>=3 and line[:3]=='```':
            if self._is_in_codehilight:
                self._is_in_codehilight = False
            else:
                self._is_in_codehilight = True
            return

        if self._is_in_codehilight:
            return

        # [Target format]
        #
        # (TARGET) = (PREFIX)(BODY)
        # (PREFIX) = # | ## | ### | ...
        # (BODY)   = (SPACES)(ANCHOR)(BODY-TEXT)
        # (ANCHOR) = <a name="(ANCHOR-NAME)">
        #
        # Exsamples
        # `# Feature`
        # `## Feature`
        # `### Feature`
        # `#Feature`
        # `# <a name="feature">Feature`

        # Determin a indent depth for TOC list.
        #
        # * Level1-section (No indent)
        #   * Level2-section (1-level-indent)
        #     * Level3-section(2-level-indent)
        sharp_count = 0
        while True:
            # @todo IndexError handling when a sharp string only(Ex: `#`, `## `)
            c = line[sharp_count]
            if c=='#':
                # 最大の深さより深い見出しは出力しない.
                if sharp_count==self._max_sub_depth:
                    return
                sharp_count += 1
                continue
            break
        if sharp_count==0:
            return
        indent_unit = ' '*self._indent_unit
        prefix = '{0}{1}'.format(indent_unit*sharp_count, '*')

        # Interpret a body text.
        body = line[sharp_count:].lstrip(' ')
        anchorlink = self._create_anchor_link_if_possible(body)
        if anchorlink:
            body = anchorlink

        # A list of Github Flavored Markdown must contains a space at first.
        #
        # OK  `* list`
        # NG  `*list`
        output_line = '{0} {1}'.format(prefix, body)
        self.append(output_line)

    def _filepath2linkstring(self, filepath):
        return filepath

    def _create_anchor_link_if_possible(self, body):
        if self._use_gitbucket_mode:
            return self._create_anchor_link_for_gitbucket(body)

        unicode_body = Encoding.to_unicode(body)
        unicode_linkstr = Encoding.to_unicode(
            self._filepath2linkstring(self._current_parsee_filepath))

        startmarks = u'<a name="'
        if len(unicode_body)<=len(startmarks):
            return None

        endmarks = u'">'
        startpos = len(startmarks)
        endpos = unicode_body.find(endmarks)
        if endpos == -1:
            return None

        anchorname = unicode_body[startpos:endpos]
        bodytext = unicode_body[endpos+len(endmarks):]
        ret = u'[{0}]({1}#{2})'.format(bodytext, unicode_linkstr, anchorname)

        return Encoding.unicode_to_utf8(ret)

    def _create_anchor_link_for_gitbucket(self, body):
        unicode_body = Encoding.to_unicode(body)
        unicode_linkstr = Encoding.to_unicode(
            self._filepath2linkstring(self._current_parsee_filepath))

        # cut `<a name="...">`
        anchor_endpos = unicode_body.find('>')
        if anchor_endpos!=-1:
            unicode_body = unicode_body[anchor_endpos+1:]

        # anchorname を作成していく.
        # GitBucket の複雑な変換ルールを **ある程度** 踏襲する.
        # Java の正規化ライブラリとか使ってるんで完全踏襲は面倒...
        anchorname = unicode_body

        # Rule1: skip
        skip_chars='!#&[]<>|~()\{}'
        def find_each(findee, findchars):
            pos = len(findee)
            for char in findchars:
                curpos = findee.find(char)
                if curpos==-1:
                    continue
                if curpos<pos:
                    pos = curpos
            if pos==len(findee):
                return -1
            return pos
        skip_start_pos =find_each(anchorname, skip_chars)
        if skip_start_pos!=-1:
            anchorname = anchorname[:skip_start_pos]

        # Rule2: to single hyphen.
        # chars から成る文字列の塊全てを単一の - で置き換える.
        # an...ch.,:o r
        # |
        # V
        # an-ch-o-r
        def replace_each(chars, beforestr, afterstr):
            ret = beforestr
            for char in chars:
                ret = ret.replace(char, afterstr)
            return ret
        chars = ' ;"$%\'+-,.:=@^'
        anchorname = replace_each(chars, anchorname, '-')
        while True:
            if anchorname.find('--')==-1:
                break
            anchorname = anchorname.replace('--', '-')

        # Rule3: UPPERCASE to LOWERCASE
        anchorname = anchorname.lower()

        ret = u'[{0}]({1}#{2})'.format(unicode_body, unicode_linkstr, anchorname)
        return Encoding.unicode_to_utf8(ret)

class IndentGenerator:
    """
    no-indent
      indent-down
        indent-down
        keep
        keep
      indent-up
    indent-up """

    def __init__(self, unit):
        self._unit = unit
        self._level = 0

    def get(self):
        if self._level==0:
            return ''
        return ' '*self._unit*self._level

    def set_level(self, level):
        self._level = level

    def reflect_level(self, s):
        self._level = self._get_level_from_string(s)

    def up(self):
        self._level -= 1

    def down(self):
        self._level += 1

    def _get_level_from_string(self, s):
        space_count = 0
        for c in s:
            if c==' ':
                space_count += 1
                continue
            break

        if space_count%self._unit != 0:
            raise RuntimeError('A Indent level is invalid. "%s"' % s)

        return space_count/self._unit

class Indentor:
    def __init__(self, indent_unit=2):
        """ indent_unit=2 means GFM indentation. """
        # statuses
        self._indentgen = IndentGenerator(unit=indent_unit)
        self._current_indent = ''

    def parse(self, toc_lines):
        self._new_lines = []
        for line in toc_lines:
            new_line = self._parse_line(line)
            self._new_lines.append(new_line)

    def _parse_line(self, line):
        """
        Lines Sample
        * [base.ext](base.ext)
          * sec-lv1
            * sec-lv2
        * [dir/base.ext](dir/base.ext)
          * sec-lv1
            * sec-lv2
          * [anchor](dir/base.ext#anchorname)

        Types
        - File Link
        - Section
        - Anchor Section
        """

        striped_line = line.strip(' ')

        # (Anchor) Section の場合,
        # 直前の File Link のインデントを継承する.
        if len(striped_line)<3 or \
           striped_line.find('#')!=-1 or \
           striped_line[:3]!='* [':
            return '{0}{1}'.format(self._current_indent, line)

        # File Link の場合,
        # ディレクトリ区切りの数だけインデントを下げる.

        # `* [path/to/base.ext](path/to/base.ext)`
        #     ^^^^^^^^^^^^^^^^
        #       Extract here.
        filepath = striped_line[3:].split(']')[0]

        nest_count = len(filepath.split('/')) - 1
        self._indentgen.set_level(nest_count)
        self._current_indent = self._indentgen.get()

        return '{0}{1}'.format(self._current_indent, line)

    def get_lines(self):
        return self._new_lines

class DirectoryInserter:
    def __init__(self, dir_emoji, indent_unit=2):
        self._indentgen = IndentGenerator(unit=indent_unit)
        self._curdir_stack = []

        self._dir_emoji = dir_emoji

    def parse(self, toc_lines):
        self._new_lines = []

        for line in toc_lines:
            self._parse_line(line)
            self._new_lines.append(line)

    def _parse_line(self, line):
        """
        Lines Sample
        * [base.ext](base.ext)
          * sec-lv1
            * sec-lv2
        * [dir/base.ext](dir/base.ext)
          * sec-lv1
            * sec-lv2
          * [anchor](dir/base.ext#anchorname)
        """

        striped_line = line.strip(' ')

        # (Anchor) Section の場合,
        # 無視する.
        if len(striped_line)<3 or \
           striped_line.find('#')!=-1 or \
           striped_line[:3]!='* [':
            return

        # File Link の場合,

        # `* [path/to/base.ext](path/to/base.ext)`
        #     ^^^^^^^^^^^^^^^^
        #       Extract here.
        filepath = striped_line[3:].split(']')[0]

        thisdir_stack = filepath.split('/')
        nest_count = len(thisdir_stack) - 1

        if nest_count==0:
            return

        for i in range(nest_count):
            if self._is_this_dir_in_stack(thisdir_stack, i):
                continue

            self._update_curdir_stack(thisdir_stack, i)

            self._indentgen.reflect_level(line)
            for downcount in range(nest_count-i):
                self._indentgen.up()

            appendee = '{0}* {1} {2}'.format(
                self._indentgen.get(),
                self._dir_emoji,
                thisdir_stack[i],
            )
            self._new_lines.append(appendee)

        return

    def _is_this_dir_in_stack(self, thisdir_stack, idx):
        this_dir = thisdir_stack[idx]

        try:
            stacked_dir = self._curdir_stack[idx]
        except IndexError:
            return False

        if this_dir!=stacked_dir:
            return False

        return True

    def _update_curdir_stack(self, thisdir_stack, i):
        thisdir = thisdir_stack[i]

        try:
            stacked_dir = self._curdir_stack[i]
        except IndexError:
            self._curdir_stack.append(thisdir)
            return

        def p(stacked_dir, curdir):
            print "stacked: %s" % stacked_dir
            print "curdir : %s" % curdir

        #print 'before'
        #p(stacked_dir, dirname)

        if stacked_dir!=thisdir:
            self._curdir_stack[i] = thisdir

        #print 'after'
        #p(stacked_dir, dirname)

    def get_lines(self):
        return self._new_lines

class TidyItemname:
    def __init__(self, indent_unit=2):
        self._indentgen = IndentGenerator(unit=indent_unit)

    def parse(self, toc_lines):
        self._new_lines = []
        for line in toc_lines:
            new_line = self._parse_line(line)
            self._new_lines.append(new_line)

    def _parse_line(self, line):
        striped_line = line.strip(' ')

        # (Anchor) Section の場合, 無視する.
        if len(striped_line)<3 or \
           striped_line.find('#')!=-1 or \
           striped_line[:3]!='* [':
            return line

        # File Link の場合, 以下のように変換する.
        #
        # `* [path/to/base.ext](path/to/base.ext)`
        #      ||
        #      VV
        # `* [base.ext](path/to/base.ext)`

        filepath = striped_line[3:].split(']')[0]
        filename = FileUtil.get_filename(filepath)

        p1 = line[:line.find('[')]
        p2 = filename
        p3 =line[line.find(']'):]
        return '{0}[{1}{2}'.format(p1, p2, p3)

    def get_lines(self):
        return self._new_lines

class FileEmojiPrepender:
    def __init__(self, emoji, indent_unit=2):
        self._indentgen = IndentGenerator(unit=indent_unit)
        self._emoji = emoji

    def parse(self, toc_lines):
        self._new_lines = []
        for line in toc_lines:
            new_line = self._parse_line(line)
            self._new_lines.append(new_line)

    def _parse_line(self, line):
        striped_line = line.strip(' ')

        # (Anchor) Section の場合, 無視する.
        if len(striped_line)<3 or \
           striped_line.find('#')!=-1 or \
           striped_line[:3]!='* [':
            return line

        # File Link の場合, 以下のように変換する.
        #
        # `* [base.md](path/to/base.md)`
        #      ||
        #      VV
        # `* :emoji_tag: [base.md](path/to/base.md)`

        filepath = striped_line[3:].split(']')[0]

        ext =FileUtil.get_extension(filepath)
        if ext.lower()!='.md':
            return line

        front, back = line.split('[')
        return '{0}{1} [{2}'.format(front, self._emoji, back)

    def get_lines(self):
        return self._new_lines

class ContentAdder:
    def __init__(self, appendfilepath=None, prependfilepath=None):
        self._appendfilepath = appendfilepath
        self._prependfilepath = prependfilepath

    def parse(self, toc_lines):
        self._new_lines = []

        if self._prependfilepath:
            self._new_lines = FileUtil.read(self._prependfilepath)

        self._new_lines.extend(toc_lines)

        if self._appendfilepath:
            self._new_lines.extend(FileUtil.read(self._appendfilepath))

    def get_lines(self):
        return self._new_lines

class Encoding:
    @staticmethod
    def to_unicode(bytestr):
        if not isinstance(bytestr, str):
            raise RuntimeError('Not a string.')

        codes = ['utf-8', 'sjis', 'cp932']
        for code in codes:
            try:
                return bytestr.decode(code)
            except UnicodeDecodeError:
                continue
        raise RuntimeError('Unsupported encoding...')

    @staticmethod
    def byte_to_utf8(bytestr):
        uni = Encoding.to_unicode(bytestr)
        return uni.encode('utf-8')

    @staticmethod
    def unicode_to_utf8(unistr):
        return unistr.encode('utf-8')

class ArgumentParser():
    def __init__(self):
        self.args = None

        self._parse()

    def _parse(self):
        import argparse

        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='Create a TOC file from markdown(*.md) files ' \
                        'in the current directory.')

        parser.add_argument('-w', '--whitelist', nargs='*', action='append',
            default=[],
            help='Markdown files which be white-filtered. '
                 'You can use a wildcard.')
        parser.add_argument('-b', '--blacklist', nargs='*', action='append',
            default=[],
            help='Markdown files which be excluded. '
                 'You can use a wildcard.')
        parser.add_argument('-e', '--exclude-dir', nargs='*', action='append',
            default=[],
            help='Folder names which be excluded from scanning files.'
                 'You CANNOT use a wildcard.')

        parser.add_argument('-o', '--out', default='index.md',
            help='A output TOC filename.')

        parser.add_argument('--depth', default='-1',
            help='Max section depth which be parsed. '
                 'Type `-1` for using no limits. '
                 'Type `0` for using no section output.')

        parser.add_argument('-s', '--space', default=2,
            help='The number of space for list-nesting.')

        parser.add_argument('--file-emoji', default=':memo:',
            help='A emoji of GFM for a markdown file.')
        parser.add_argument('--dir-emoji', default=':file_folder:',
            help='A emoji of GFM for a directory.')

        parser.add_argument('--header', default=None,
            help='Prepend a content of a given markdown filepath.')
        parser.add_argument('--footer', default=None,
            help='Append a content of a given markdown filepath.')

        parser.add_argument('--print-filelist', default=False, action='store_true',
            help='[FOR DEBUG] Print target filelist.')

        parser.add_argument('--gitbucket', default=False, action='store_true',
            help='If you use a GitBucket and want to use anchor link.')

        self.args =parser.parse_args()
        self.args.whitelist = self._nargs2list('whitelist')
        self.args.blacklist = self._nargs2list('blacklist')
        self.args.exclude_dir = self._nargs2list('exclude_dir')

        if self.args.header and not FileUtil.exists(self.args.header):
            print 'The header file "{0}" is not found.'.format(self.args.header)
            exit(0)
        if self.args.footer and not FileUtil.exists(self.args.footer):
            print 'The footer file "{0}" is not found.'.format(self.args.footer)
            exit(0)

    def _nargs2list(self, key):
        try:
            src = getattr(self.args, key)
            ret = []
            for addee in src:
                ret.extend(addee)
            return ret
        except:
            pass
        return []

def ________main________():
    pass

args = ArgumentParser().args

# 作業ディレクトリを指定するオプションは閉塞.
# 理由)これを考慮すると内部仕様が複雑になるから.
#      特に, ローカルパスは Github repo 上では有効ではないがゆえに
#      ローカルパスを相対パスに変換する処理等が必要になる.
# だったら, カレントディレクトリに固定した方がシンプル.
basedir = os.getcwd()

walker = FileWalker(basedir=basedir, exclude_dirs=args.exclude_dir)

# white and black list filtering
# ------------------------------

args.whitelist.append('*.md')
walker.whiltefilter_all(args.whitelist)

if args.blacklist:
    walker.exclude_all(args.blacklist)

if args.print_filelist:
    for line in walker.get_filelist():
        print line
    exit(0)

# normalize target filelists
# --------------------------

walker.cut_basedir()
walker.separator_win2lin()
targets = walker.get_filelist()

# generate a TOC
# --------------

space_num = int(args.space)
use_gitbucket_mode = args.gitbucket

toc = TOC(filelist=targets,
          basedir=basedir,
          max_sub_depth=int(args.depth),
          indent_unit=space_num,
          use_gitbucket_mode=use_gitbucket_mode)
toc.parse()
toc_lines = toc.get_lines()

indentor = Indentor(indent_unit=space_num)
indentor.parse(toc_lines)
toc_lines = indentor.get_lines()

inserter = DirectoryInserter(dir_emoji=args.dir_emoji, indent_unit=space_num)
inserter.parse(toc_lines)
toc_lines = inserter.get_lines()

tidyname = TidyItemname(indent_unit=space_num)
tidyname.parse(toc_lines)
toc_lines = tidyname.get_lines()

fileemoji = FileEmojiPrepender(emoji=args.file_emoji, indent_unit=space_num)
fileemoji.parse(toc_lines)
toc_lines = fileemoji.get_lines()

adder = ContentAdder(args.footer, args.header)
adder.parse(toc_lines)
toc_lines = adder.get_lines()

for i in range(len(toc_lines)):
    toc_lines[i] = Encoding.byte_to_utf8(toc_lines[i])

FileUtil.write(args.out, toc_lines)
