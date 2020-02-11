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


def remove_comments(lst):
    o = []
    bcomment = False
    for a in lst:
        if a == '/*':
            print(lst)
            exit()
    return lst


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
    rb = False
    bcomment = False
    sb = 0
    cb = 0
    lg = 0
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
            t == '.' and p in 'D'
        ) and not (
            t in ('-', '+') and p in 'D'
        ) and not (
            t == '=' and a == '='
        ) and not (
            t == '=' and a == '>'
        ) and not (
            sq or dq or bt or rb or sb > 0 or cb > 0 or lg > 0 or bcomment
        ):
            l.append(o.strip())
            o = ''
        if a == "'" and not (
            dq or bt or rb or sb > 0 or cb > 0 or lg > 0 or bcomment
        ):
            sq = not sq
        elif a == '"' and not (
            sq or bt or rb or sb > 0 or cb > 0 or lg > 0 or bcomment
        ):
            dq = not dq
        elif a == '`' and not (
            sq or dq or rb or sb > 0 or cb > 0 or lg > 0
        ):
            bt = not bt
        elif a == '(' and not (
            sq or dq or bt or sb > 0 or cb > 0 or lg > 0
        ):
            rb = True
        elif a == ')' and not (
            sq or dq or bt or sb > 0 or cb > 0 or lg > 0
        ):
            rb = False
        elif a == '[' and not (
            sq or dq or bt or rb or cb > 0 or lg > 0
        ):
            sb += 1
        elif a == ']' and not (
            sq or dq or bt or rb or cb > 0 or lg > 0
        ):
            sb -= 1
        elif a == '{' and not (
            sq or dq or bt or rb or sb > 0 or lg > 0
        ):
            cb += 1
        elif a == '}' and not (
            sq or dq or bt or rb or sb > 0 or lg > 0
        ):
            cb -= 1
        elif a == '<' and not (
            sq or dq or bt or rb or sb > 0 or cb > 0
        ):
            lg += 1
        elif a == '>' and not (
            sq or dq or bt or rb or sb > 0 or cb > 0
        ):
            lg -= 1
        elif t == '/' and a == '*' and not (
            sq or dq or bt or rb or sb > 0 or cb > 0
        ):
            l = l[:-1]
            bcomment = True
        elif t == '*' and a == '/' and not (
            sq or dq or bt or rb or sb > 0 or cb > 0
        ):
            a = ''
            bcomment = False
        if not bcomment:
            o += a
        t = a
    k = []
    pair = []
    for a in list(filter(None, l + [o])):
        pair.append(a)
        if pair[1:]:
            if pair[0] == '$' and isnum(pair[1]):
                del k[-1]
                k.append('$' + pair[1])
            elif pair[0] == 'RE' and (pair[1].startswith('"') or pair[1].startswith("'")):
                del k[-1]
                k.append('RE' + pair[1])
            elif isnum(pair[0]) and pair[1][0] == '.' and isnum(pair[1][1:]):
                del k[-1]
                k.append(pair[0] + pair[1])
            else:
                k.append(a)
            del pair[0]
        else:
            k.append(a)
    return remove_comments(k)


def tokenise_file(code, split_at=';', dofilter=True):
    sq = False
    dq = False
    bt = False
    rb = False
    bcomment = False
    sb = 0
    cb = 0
    lg = 0
    l = []
    o = ''
    p = ''
    t = ''
    for a in code:
        if a == "'" and not (
            dq or bt or rb or sb > 0 or cb > 0 or lg > 0 or bcomment
        ):
            sq = not sq
        elif a == '"' and not (
            sq or bt or rb or sb > 0 or cb > 0 or lg > 0 or bcomment
        ):
            dq = not dq
        elif a == '`' and not (
            sq or dq or rb or sb > 0 or cb > 0 or lg > 0 or bcomment
        ):
            bt = not bt
        elif a == '(' and not (
            sq or dq or bt or sb > 0 or cb > 0 or lg > 0 or bcomment
        ):
            rb = True
        elif a == ')' and not (
            sq or dq or bt or sb > 0 or cb > 0 or lg > 0 or bcomment
        ):
            rb = False
        elif a == '[' and not (
            sq or dq or bt or rb or cb > 0 or lg > 0 or bcomment
        ):
            sb += 1
        elif a == ']' and not (
            sq or dq or bt or rb or cb > 0 or lg > 0 or bcomment
        ):
            sb -= 1
        elif a == '{' and not (
            sq or dq or bt or rb or sb > 0 or lg > 0 or bcomment
        ):
            cb += 1
        elif a == '}' and not (
            sq or dq or bt or rb or sb > 0 or lg > 0 or bcomment
        ):
            cb -= 1
        elif a == '<' and not (
            sq or dq or bt or rb or sb > 0 or cb > 0 or bcomment
        ):
            lg += 1
        elif a == '>' and not (
            sq or dq or bt or rb or sb > 0 or cb > 0 or bcomment
        ):
            lg -= 1
        elif t == '/' and a == '*' and not (
            sq or dq or bt or rb or sb > 0 or cb > 0
        ):
            bcomment = True
        elif t == '*' and a == '/' and not (
            sq or dq or bt or rb or sb > 0 or cb > 0
        ):
            bcomment = False
        if a == split_at and not (
            sq or dq or bt or rb or sb > 0 or cb > 0 or lg > 0 or bcomment
        ):
            l.append(o.strip(' \t\v\f\r'))
            o = ''
        else:
            o += a
        t = a
    out = l + [o.strip(' \t\v\f\r')]
    if dofilter:
        return list(filter(None, out))
    return remove_comments(out)
