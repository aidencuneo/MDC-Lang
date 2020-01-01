def get_code(fname, fromline=0):
    try:
        with open(fname) as f:
            code = f.read()
        for a in range(fromline - 1):
            code = code[code.index('\n') + 1:]
        return process(code)
    except Exception as e:
        return e


def process(code):
    return code.replace('\n', '').split(';')


def count_lines(fname):
    try:
        with open(fname) as f:
            text = f.read()
        return text.count('\n')
    except Exception as e:
        return e
