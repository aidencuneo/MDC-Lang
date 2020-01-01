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
    return list(filter(None, code.replace('\n', '').split(';')))


def count_lines(fname):
    try:
        with open(fname) as f:
            text = f.read()
        return text.count('\n')
    except Exception as e:
        return e
