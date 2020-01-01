import sys
import string

alphabet = string.letters if sys.version_info[0] < 3 else string.ascii_letters
digits = string.digits
symbols = string.punctuation
whitespace = string.whitespace


def get_code(fname, fromline=0, setcode=None):
    try:
        if not setcode:
            with open(fname) as f:
                code = f.read()
        else:
            code = setcode
        for a in range(fromline - 1):
            code = code[code.index('\n') + 1:]
        return code
    except Exception as e:
        return e


def process(code):
    return tokenise_file(code.replace('\n', ''))


def count_lines(fname):
    try:
        with open(fname) as f:
            text = f.read()
        return text.count('\n')
    except Exception as e:
        return e


def tokenise(line):
    sq = False
    dq = False
    bt = False
    rb = False
    sb = 0
    cb = False
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
        sq or dq or bt or rb or (sb > 0) or cb or (lg > 0)):
            l.append(o.strip())
            o = ''
        if a == "'" and not dq:
            sq = not sq
        elif a == '"' and not sq:
            dq = not dq
        elif a == '`' and not (
        sq or dq or rb or sb or cb or lg):
            bt = not bt
        elif a == '(' and not (
        sq or dq or bt or sb or cb or lg):
            rb = True
        elif a == ')' and not (
        sq or dq or bt or sb or cb or lg):
            rb = False
        elif a == '[' and not (
        sq or dq or bt or rb or cb or lg):
            sb += 1
        elif a == ']' and not (
        sq or dq or bt or rb or cb or lg):
            sb -= 1
        elif a == '{' and not (
        sq or dq or bt or rb or sb or lg):
            cb = True
        elif a == '}' and not (
        sq or dq or bt or rb or sb or lg):
            cb = False
        elif a == '<' and not (
        sq or dq or bt or rb or sb or cb):
            lg += 1
        elif a == '>' and not (
        sq or dq or bt or rb or sb or cb):
            lg -= 1
        o += a
        t = a
    k = []
    pair = []
    for a in list(filter(None, l + [o])):
        pair.append(a)
        if pair[1:]:
            if pair[0] == '$' and pair[1] in digits:
                del k[-1]
                k.append('$' + pair[1])
            elif pair[0] == '-' and pair[1] in digits:
                del k[-1]
                k.append('-' + pair[1])
            elif pair[0] == '+' and pair[1] in digits:
                del k[-1]
                k.append('+' + pair[1])
            elif pair[0] == 'RE' and (pair[1].startswith('"') or pair[1].startswith("'")):
                del k[-1]
                k.append('RE' + pair[1])
            else:
                k.append(a)
            del pair[0]
        else:
            k.append(a)
    return k


def tokenise_file(code, split_at=';', dofilter=True):
    sq = False
    dq = False
    bt = False
    rb = False
    sb = 0
    cb = False
    lg = 0
    l = []
    o = ''
    p = ''
    t = ''
    for a in code:
        if a == "'" and not dq:
            sq = not sq
        elif a == '"' and not sq:
            dq = not dq
        elif a == '`' and not (
        sq or dq or rb or sb or cb or lg):
            bt = not bt
        elif a == '(' and not (
        sq or dq or bt or sb or cb or lg):
            rb = True
        elif a == ')' and not (
        sq or dq or bt or sb or cb or lg):
            rb = False
        elif a == '[' and not (
        sq or dq or bt or rb or cb or lg):
            sb += 1
        elif a == ']' and not (
        sq or dq or bt or rb or cb or lg):
            sb -= 1
        elif a == '{' and not (
        sq or dq or bt or rb or sb or lg):
            cb = True
        elif a == '}' and not (
        sq or dq or bt or rb or sb or lg):
            cb = False
        elif a == '<' and not (
        sq or dq or bt or rb or sb or cb):
            lg += 1
        elif a == '>' and not (
        sq or dq or bt or rb or sb or cb):
            lg -= 1
        if a == split_at and not (
        sq or dq or bt or rb or (sb > 0) or cb or (lg > 0)):
            l.append(o.strip(' \t\v\f\r'))
            o = ''
        else:
            o += a
    out = l + [o.strip(' \t\v\f\r')]
    if dofilter:
        return list(filter(None, out))
    return out
