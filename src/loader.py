'''

MDCL created by Aiden Blishen Cuneo.
First Commit was at: 1/1/2020.

'''

import re
import sys
import string

alphabet = string.letters if sys.version_info[0] < 3 else string.ascii_letters
digits = string.digits
symbols = string.punctuation
whitespace = string.whitespace


def get_code(fname, fromline=0, specificline=0, specificindex=None, setcode=None):
    try:
        if not setcode:
            with open(fname) as f:
                code = f.read()
        else:
            code = setcode
        for a in range(fromline - 1):
            code = code[code.index('\n') + 1:]
        if specificline > 0:
            code = code.split('\n')[specificline - 1]
        if specificindex is not None:
            code = code.split('\n')[specificindex]
        return code
    except Exception as e:
        return e


def process(code):
    return tokenise_file(code)#.replace('\n', ''))


def count_lines(fname):
    try:
        with open(fname) as f:
            text = f.read()
        return text.count('\n')
    except Exception as e:
        return e


def isnum(num):
    return re.match('^(-|\+)*[0-9]+$', num)


def isfloat(num):
    return re.match('^(-|\+)*[0-9]*\.[0-9]+$', num)


def isword(word):
    return all([b in alphabet for b in word])


def tokenise(line):
    sq = False
    dq = False
    bt = False
    bcomment = False
    rb = 0
    sb = 0
    cb = 0
    l = []
    o = ''
    p = ''
    t = ''
    for a in line.strip():
        q = p
        if a in alphabet:
            p = 'A'
        elif a in digits:
            p = 'D'
        elif a in symbols:
            p = 'S'
        elif a in whitespace:
            p = 'W'
        if (q != p and p != 'W' or p == 'S') and not (
            t in ('-', '+') and p == 'D'
        ) and not (
            t == '=' and a == '='
        ) and not (
            t == '=' and a == '>'
        ) and not (
            t == '>' and a == '='
        ) and not (
            t == '<' and a == '='
        ) and not (
            t == '+' and a == ':'
        ) and not (
            t == '-' and a == ':'
        ) and not (
            t == '*' and a == ':'
        ) and not (
            t == '/' and a == ':'
        ) and not (
            t == '_' and p == 'A'
        ) and not (
            q == 'A' and a == '_'
        ) and not (
            t == '_' and a == '_'
        ) and not (
            t == 'x' and (a in '"\'')
        ) and not (
            sq or dq or bt or rb > 0 or sb > 0 or cb > 0 or bcomment
        ):
            l.append(o.strip())
            o = ''
        if a == "'" and not (
            dq or bt or rb > 0 or sb > 0 or cb > 0 or bcomment
        ):
            sq = not sq
        elif a == '"' and not (
            sq or bt or rb > 0 or sb > 0 or cb > 0 or bcomment
        ):
            dq = not dq
        elif a == '`' and not (
            sq or dq or rb > 0 or sb > 0 or cb > 0
        ):
            bt = not bt
        elif a == '(' and not (
            sq or dq or bt or sb > 0 or cb > 0
        ):
            rb += 1
        elif a == ')' and not (
            sq or dq or bt or sb > 0 or cb > 0
        ):
            rb -= 1
        elif a == '[' and not (
            sq or dq or bt or rb > 0 or cb > 0
        ):
            sb += 1
        elif a == ']' and not (
            sq or dq or bt or rb > 0 or cb > 0
        ):
            sb -= 1
        elif a == '{' and not (
            sq or dq or bt or rb > 0 or sb > 0
        ):
            cb += 1
        elif a == '}' and not (
            sq or dq or bt or rb > 0 or sb > 0
        ):
            cb -= 1
        elif t == '/' and a == '*' and not (
            sq or dq or bt or rb > 0 or sb > 0 or cb > 0
        ):
            l = l[:-1]
            bcomment = True
        elif t == '*' and a == '/' and not (
            sq or dq or bt or rb > 0 or sb > 0 or cb > 0
        ):
            a = ''
            bcomment = False
        if not bcomment:
            o += a
        t = a
    out = list(filter(None, l + [o]))
    return post_tokenise(out)


def tokenise_file(code, split_at=';', dofilter=True):
    sq = False
    dq = False
    bt = False
    bcomment = False
    rb = 0
    sb = 0
    cb = 0
    l = []
    o = ''
    p = ''
    t = ''
    for a in code:
        if a == "'" and not (
            dq or bt or rb > 0 or sb > 0 or cb > 0 or bcomment
        ):
            sq = not sq
        elif a == '"' and not (
            sq or bt or rb > 0 or sb > 0 or cb > 0 or bcomment
        ):
            dq = not dq
        elif a == '`' and not (
            sq or dq or rb > 0 or sb > 0 or cb > 0 or bcomment
        ):
            bt = not bt
        elif a == '(' and not (
            sq or dq or bt or sb > 0 or cb > 0 or bcomment
        ):
            rb += 1
        elif a == ')' and not (
            sq or dq or bt or sb > 0 or cb > 0 or bcomment
        ):
            rb -= 1
        elif a == '[' and not (
            sq or dq or bt or rb > 0 or cb > 0 or bcomment
        ):
            sb += 1
        elif a == ']' and not (
            sq or dq or bt or rb > 0 or cb > 0 or bcomment
        ):
            sb -= 1
        elif a == '{' and not (
            sq or dq or bt or rb > 0 or sb > 0 or bcomment
        ):
            cb += 1
        elif a == '}' and not (
            sq or dq or bt or rb > 0 or sb > 0 or bcomment
        ):
            cb -= 1
            o += a
            a = split_at
        elif t == '/' and a == '*' and not (
            sq or dq or bt or rb > 0 or sb > 0 or cb > 0
        ):
            bcomment = True
        elif t == '*' and a == '/' and not (
            sq or dq or bt or rb > 0 or sb > 0 or cb > 0
        ):
            bcomment = False
        if a == split_at and not (
            sq or dq or bt or rb > 0 or sb > 0 or cb > 0 or bcomment
        ):
            l.append(o.strip(' \t\v\f\r'))
            o = ''
        else:
            o += a
        t = a
    out = l + [o.strip(' \t\v\f\r')]
    if dofilter:
        out = list(filter(None, out))
    return out


def post_tokenise(lst):
    if 'do' in lst:
        i = lst.index('do')
        lst[i] = '{' + ' '.join(lst[i + 1:]) + '}'
        del lst[i + 1:]
    return lst
