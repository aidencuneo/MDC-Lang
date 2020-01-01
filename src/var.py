import ast
import os
import re
import sys
import string

from functools import partial
from pprint import pformat

import compact
import loader

alphabet = string.letters if sys.version_info[0] < 3 else string.ascii_letters
digits = string.digits
symbols = string.punctuation
whitespace = string.whitespace

input_func = 'raw_input' if sys.version_info[0] < 3 else 'input'
get_input = raw_input if sys.version_info[0] < 3 else input


class Function:

    def __init__(self, arg_count, ret):
        self.arg_count = arg_count
        self.ret = ret
    
    def call(self, args, ex_args=None):
        if ex_args:
            args += ex_args
        return evaluate(self.ret, args=args[:self.arg_count])


class BuiltinFunction(Function):

    def call(self, args, ex_args=None):
        if ex_args:
            ex_args = replacekeys(ex_args)
        return self.ret(evaluate(args[:self.arg_count], args=ex_args))


class Procedure:

    def __init__(self, action):
        self.action = action

    def call(self):
        evaluate(self.action)


class BuiltinProcedure(Procedure):

    def call(self):
        self.action()


class Datatype:

    def __init__(self, value):
        self.value = value

    def do_action(self, action, args):
        if action == 'ADD':
            r = self.ADD(*args)
        elif action == 'SUB':
            r = self.SUB(*args)
        elif action == 'MULT':
            r = self.MULT(*args)
        elif action == 'DIV':
            r = self.DIV(*args)
        elif action == 'PWR':
            r = self.PWR(*args)
        elif action == 'EQ':
            r = self.EQ(*args)
        elif action == 'LT':
            r = self.LT(*args)
        elif action == 'GT':
            r = self.GT(*args)
        elif action == 'LE':
            r = self.LE(*args)
        elif action == 'GE':
            r = self.GE(*args)
        elif action == 'INDEX':
            r = self.INDEX(*args)
        else:
            raise AttributeError
        return r


class Integer(Datatype):

    def __init__(self, value):
        self.value = int(value)

    def __repr__(self):
        return pformat(self.value)

    def __bool__(self):
        return bool(self.value)

    def ADD(self, other):
        mdc_assert(self, other, (Integer, Float), 'ADD')
        return self.value + other.value, type(other)

    def SUB(self, other):
        mdc_assert(self, other, (Integer, Float), 'SUB')
        return self.value - other.value, type(other)

    def MULT(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'SUB')
        if isinstance(other, (Integer, Float)):
            return self.value * other.value, type(other)
        if isinstance(other, String):
            return self.value * other.value, String
        if isinstance(other, Boolean):
            return self.value * other.value.value, Integer

    def LT(self, other):
        mdc_assert(self, other, (Integer, Float), 'LT')
        return self.value < other.value, Boolean

    def LE(self, other):
        mdc_assert(self, other, (Integer, Float), 'LE')
        return self.value <= other.value, Boolean


class Float(Datatype):

    def __init__(self, value):
        self.value = float(value)

    def ADD(self, other):
        mdc_assert(self, other, (Float, Integer), 'ADD')
        return self.value + other.value, Float


class String(Datatype):

    def __init__(self, value):
        self.value = str(value)

    def __repr__(self):
        return pformat(self.value)

    def __str__(self):
        return self.value

    def ADD(self, other):
        mdc_assert(self, other, String, 'ADD')
        return self.value + other.value, String

    def SUB(self, other):
        mdc_assert(self, other, (Integer, String), 'SUB')
        if isinstance(other, Integer):
            return self.value[:-Integer.value()], String
        if isinstance(other, String):
            return self.value.replace(other.value, '', 1), String

    def MULT(self, other):
        mdc_assert(self, other, (Integer, Boolean), 'MULT')
        if isinstance(other, Integer):
            return self.value * other.value, String
        if isinstance(other, Boolean):
            return self.value * other.value.value, String

    def DIV(self, other):
        mdc_assert(self, other, (String, Boolean), 'DIV')
        if isinstance(other, String):
            return self.value.count(other.value), Integer
        if isinstance(other, Boolean):
            return self.value if other.value.value else '', String

    def EQ(self, other):
        mdc_assert(self, other, String, 'EQ')
        return self.value == other.value, Boolean

    def INDEX(self, other):
        mdc_assert(self, other, Integer, 'INDEX')
        a = int(BFList.get_length(self).value)
        if int(other.value) > a - 1:
            call_error('String index out of range, ' + str(other) + ' > ' + str(a - 1) + '.', error_type='argerr')
        return self.value[other.value], String


class RegexString(Datatype):

    def __init__(self, value):
        self.value = re.compile(value)

    def __repr__(self):
        return pformat(self.value)

    def __str__(self):
        return 'RE' + pformat(self.value.pattern)

    def EQ(self, other):
        mdc_assert(self, other, String, 'EQ')
        return bool(self.value.match(other.value)), Boolean


class Boolean(Datatype):

    def __init__(self, value):
        if isinstance(value, str):
            value = value.lower()
            if value == 'true':
                self.value = Integer(1)
            elif value == 'false':
                self.value = Integer(0)
        else:
            self.value = Integer(bool(value))

    def __repr__(self):
        return self.value.__repr__()

    def __str__(self):
        return self.value.__repr__()

    def __bool__(self):
        return bool(self.value)


class Null(Datatype):

    def __init__(self, *args):
        self.value = 'null'

    def __repr__(self):
        return 'null'

    def __str__(self):
        return 'null'


def initialise_path(path):
    if not os.path.isdir(path):
        call_error("The path: '" + str(path) + "' could not be found.", error_type='ioerr')
    os.chdir(path)


def call_error(text, line=None, error_type=None):
    if isinstance(line, (list, tuple)):
        line = ' '.join([str(a) for a in line])
    print(end='\n')
    if error_type == 'eval':
        print('ERROR attempting to run an eval statement:')
    elif error_type == 'exp':
        print('ERROR attempting to evaluate expression:')
    elif error_type == 'ioerr':
        print('IOERROR:')
    elif error_type == 'argerr':
        print('ARGUMENT ERROR:')
    elif error_type == 'assert':
        print('ASSERTION ERROR:')
    elif error_type == 'var':
        print('VAR ERROR:')
    elif error_type == 'syntax':
        print('SYNTAX ERROR:')
    elif error_type == 'attr':
        print('ATTRIBUTE ERROR:')
    else:
        print('ERROR:')
    if line:
        print('  -> ' + line)
    print('  :: ' + text)
    sys.exit()


def mdc_assert(first, second, types, action):
    if not isinstance(types, (list, tuple)):
        types = types,
    if not isinstance(second, types):
        types = '(' + ', '.join([a.__name__ for a in types]) + ')'
        call_error(type(first).__name__ + ' operand type for ' + action + ' must fit into: ' + types + '. "' + type(second).__name__ + '" is invalid.',
            error_type='assert')


def eval_statement(code, args, error):
    try:
        args = [evaluate([z]) for z in args]
        out = eval(code, {'args': args})
        return eval_datatypes([out])[0]
    except BaseException as e:
        if isinstance(e, SystemExit):
            print('\nThe following error occurred as a result of the above error:')
        call_error(str(e), error, 'eval')


def run(code, filename=None, tokenised=False, oneline=False, echo=True, raw=False):
    global current_file
    global current_code
    if filename != 'keep':
        current_file = '<EVAL>' if filename is None else filename
        current_code = current_code if filename is None else code
    if raw:
        code = loader.process(code)
    if oneline:
        code = [code]
    o = ''
    i = 0
    while i < len(code):
        if not code[i]:
            i += 1
            continue
        if tokenised:
            a = replacekeys(code[i])
        else:
            a = replacekeys(tokenise(code[i]))
        #print(a)
        if ':' in a:
            if a[0] == 'NEW' and len(a) > 4:
                name = a[1]
                try:
                    arg_count = int(a[2])
                except ValueError:
                    call_error('Invalid argument count "' + a[2] + '" for function declaration, should be an integer.', code[i])
                ret = a[a.index(':') + 1:]
                create_function(name, arg_count, ret)
            elif a[0] == 'PROC' and len(a) > 3:
                name = a[1]
                action = a[a.index(':') + 1:]
                create_procedure(name, action)
            elif a[0] == 'IF' and len(a) > 3:
                condition = a[1:a.index(':')]
                if evaluate(condition):
                    a = run(a[a.index(':') + 1:], 'keep', True, True, False)
                    if a:
                        o += str(a)
                        if echo:
                            print(a, end='')
            elif a[0] == 'GOTO':
                if current_file == '<EVAL>':
                    call_error('GOTO statement does not work on evaluated expressions.', code[i])
                if not a[1:]:
                    call_error('GOTO statement requires at least one argument.', code[i], 'argerr')
                line = evaluate(a[1:a.index(':')])
                condition = evaluate(a[a.index(':') + 1:])
                try:
                    line = int(line.value)
                    assert line <= current_code.count('\n')
                except ValueError:
                    call_error('GOTO statement argument must be a valid line number.', code[i])
                except AssertionError:
                    call_error('GOTO statement argument must be lower than the line count of the current file.', code[i])
                if condition:
                    code = loader.process(loader.get_code('', line, current_code))
                    filename = 'keep'
                    tokenised = False
                    oneline = False
                    i = 0
                    continue
            else:
                key = ''.join(a[:a.index(':')])
                if key.startswith('array[(') and key.endswith(')]'):
                    key = ast.literal_eval(key[6:-1])
                else:
                    call_error('Invalid variable key. Variable keys must be surrounded by parentheses.',
                        code[i], 'var')
                value = evaluate(a[a.index(':') + 1:], code[i])
                array[key] = value
        elif a[0] == 'IMPORT':
            if len(a) < 2:
                call_error('IMPORT statement requires at least one argument.', code[i], 'argerr')
            fname = str(evaluate([a[1]]))
            old = current_file
            run(loader.get_code(fname), fname)
            current_file = old
        elif a[0] == 'DEFINE':
            if len(a) < 3:
                call_error('DEFINE statement requires two arguments, KEY and VALUE.', code[i], 'argerr')
            key = a[1].strip()
            if not key:
                call_error('DEFINE statement key must not be empty.', code[i], 'argerr')
            if key in global_vars:
                call_error('Constant with key ' + pformat(key) + ' already exists. Constants can not be redefined.', code[i], 'syntax')
            value = evaluate(a[2:])
            global_vars[key] = value
        elif a[0] in procedures:
            procedures[a[0]].call()
        else:
            a = evaluate(a)
            if type(a) in builtin_types:
                o += str(a)
                if echo:
                    sys.stdout.write(str(a))
                    if '\n' in str(a):
                        sys.stdout.flush()
        i += 1
    return o


def create_function(name, arg_count, ret):
    functions[name] = Function(arg_count, ret)


def create_procedure(name, action):
    procedures[name] = Procedure(action)


def eval_datatypes(exp):
    if not exp:
        return exp
    new = [a for a in exp]
    a = 0
    while a < len(new):
        if isinstance(new[a], builtin_types):
            a += 1
            continue
        if isinstance(new[a], str):
            if new[a].startswith('array[(') and new[a].endswith(')]'):
                try:
                    new[a] = eval(new[a])
                except KeyError:
                    call_error('Variable key does not exist.', '(' + new[a][9:-3] + ')', 'var')
        if isinstance(new[a], tuple([b for b in datatypes_switch.keys() if b != str])):
            new[a] = datatypes_switch[type(new[a])](new[a])
        if not isinstance(new[a], str):
            pass
        elif re.match('^(-|\+)*[0-9]+', new[a]): # Is new[a] an integer? If so, assign Integer() class.
            new[a] = Integer(new[a])
        elif re.match('^RE(\'|").+(\'|")', new[a]): # Is new[a] a Regex String? If so, assign Regex() class.
            try:
                new[a] = RegexString(ast.literal_eval(new[a][2:]))
            except Exception:
                call_error('Invalid Regex String.', revertkeys(exp), 'syntax')
        elif re.match("^'.+'", new[a]) or new[a] == "''": # Is new[a] a string with single quotes? If so, assign String() class using RAW value.
            new[a] = String(new[a][1:-1])
        elif re.match('^".+"', new[a]) or new[a] == '""': # Is new[a] a string with double quotes? If so, assign evaluated String() class.
            try:
                new[a] = String(ast.literal_eval(new[a]))
            except Exception:
                call_error('Invalid String.', revertkeys(exp), 'syntax')
        elif new[a] in ('TRUE', 'FALSE', 'True', 'False'): # Is new[a] a boolean? If so, assign Boolean() class.
            new[a] = Boolean(new[a])
        a += 1
    return new


def eval_functions(exp, args=None):
    if not exp:
        return exp
    new = [a for a in exp]
    a = 0
    while a < len(new):
        if new[a] in functions:
            limit = functions[new[a]].arg_count
            new[a] = functions[new[a]].call(new[a + 1:a + 1 + limit], ex_args=args)
            #new[a] = eval_datatypes([pformat(new[a])])[0]
            del new[a + 1:a + 1 + limit]
            a -= limit
        a += 1
    return new


def evaluate(exp, error=None, args=None):
    if not exp:
        return Null()
    reps = (
        'ADD',
        'SUB',
        'MULT',
        'DIV',
        'PWR',
        'EQ',
        'LT',
        'GT',
        'LE',
        'GE',
        'INDEX',
    )
    new = [a for a in exp]
    new = eval_functions(eval_datatypes(new))
    #print(new, [type(b) for b in new])
    a = 0
    while a < len(new):
        #print(new[a], type(new[a]))
        if isinstance(new[a], builtin_types):
            pass
        elif new[a] in reps:
            if a - 1 < 0:
                call_error('Missing first argument for ' + new[a] + ' method.', revertkeys(exp), 'syntax')
            if a + 1 >= len(new):
                call_error('Missing second argument for ' + new[a] + ' method.', revertkeys(exp), 'syntax')
            try:
                vals = new[a - 1].do_action(new[a], (evaluate([new[a + 1]]),))
                settype = vals[1] if isinstance(vals, tuple) else type(new[a - 1])
                new[a] = settype(vals[0])
                del new[a + 1]
                del new[a - 1]
                a -= 1
            except AttributeError:
                call_error('Type ' + type(new[a - 1]).__name__ + ' does not have a method for handling ' + new[a], revertkeys(exp), 'attr')
        elif (new[a].startswith('[') or new[a].endswith(']')) and not new[a].startswith('args['):
            if not new[a].startswith('['):
                print(new, new[a])
                call_error('Right square braces without left square braces.', revertkeys(exp), 'syntax')
            if not new[a].endswith(']'):
                call_error('Left square braces without right square braces.', revertkeys(exp), 'syntax')
            new[a] = evaluate(replacekeys(tokenise(new[a][1:-1].strip())))
        elif new[a].startswith('<') or new[a].endswith('>'):
            if not new[a].startswith('<'):
                call_error('Right angle bracket without left angle bracket.', revertkeys(exp), 'syntax')
            if not new[a].endswith('>'):
                call_error('Left angle bracket without right angle bracket.', revertkeys(exp), 'syntax')
            if not a > 0:
                call_error('Shorthand condition requires a left hand argument.', revertkeys(exp), 'argerr')
            if not a <= len(new):
                call_error('Shorthand condition requires a right hand argument.', revertkeys(exp), 'argerr')
            condition = evaluate(replacekeys(tokenise(new[a][1:-1].strip())))
            left = new[a - 1]
            right = new[a + 1]
            del new[a + 1]
            del new[a - 1]
            a -= 1
            new[a] = left if condition else right
        elif new[a].startswith('args[') and new[a].endswith(']'):
            key = int(new[a][5:-1])
            if args:
                if key >= len(args):
                    call_error('Argument list index out of range, ' + str(key) + ' > ' + str(len(args) - 1) + '.', revertkeys(exp), 'argerr')
                new[a] = args[key]
            else:
                if key >= len(global_args):
                    call_error('Argument list index out of range, ' + str(key) + ' > ' + str(len(global_args) - 1) + '.', revertkeys(exp), 'argerr')
                new[a] = global_args[key]
        elif new[a].startswith('<EVAL>') and new[a].endswith('</EVAL>'):
            new[a] = new[a][6:-7]
            b = new[a].split('\n\\')
            new[a] = eval_statement(b[0], args, b[1])
        elif new[a] in global_vars:            
            new[a] = global_vars[new[a]]
        elif new[a] not in functions and new[a] not in procedures:
            token = new[a]
            if len(token) > 100:
                token = token[:97] + '...'
            raise Exception
            call_error('Invalid or Undefined Token: ' + token, revertkeys(exp), 'syntax')
        a += 1
    code = ','.join([(type(a).__name__ + '(' + pformat(a) + ')') if isinstance(a, builtin_types) else a for a in new])
    out = code
    if code and code != ',':
        try:
            out = eval(code)
            return out
        except Exception as e:
            print(exp)
            print(new)
            print(out)
            call_error(str(e), revertkeys(exp), 'exp')
    return out


def replacekeys(line):
    for a in range(len(line)):
        if line[a].startswith('(') and line[a].endswith(')'):
            values = []
            for b in line[a][1:-1].split(','):
                hx = b.strip().upper()
                if not all([c in digits + 'ABCDEF' for c in hx]):
                    call_error('Invalid variable key. Variable keys must be in Hexadecimal form, including commas and: "0123456789ABCDEF".',
                        line, 'var')
                values += ['0x' + hx]
            line[a] = 'array[(' + ','.join(values) + ',)]'
        elif line[a].startswith('$'):
            b = line[a][1]
            c = ''
            line[a] = line[a][2:]
            for z in range(len(line[a])):
                if line[a][z] in digits:
                    b += line[a][z]
                else:
                    c += line[a][z]
            line[a] = 'args[' + b + ']'
            if c:
                line.insert(a + 1, c)
        elif line[a].startswith('`') and line[a].endswith('`'):
            line[a] = '<EVAL>' + replaceargs(line[a][1:-1]) + '\n\\' + pformat(line[a]) + '</EVAL>'
    return line


def revertkeys(line):
    for a in range(len(line)):
        if line[a].startswith('array[(') and line[a].endswith(')]'):
            values = []
            for b in line[a][7:-2].split(','):
                hx = b.strip().upper()
                values += [hx[2:]]
            line[a] = '(' + ','.join(filter(None, values)) + ')'
        elif line[a].startswith('args[') and line[a].endswith(']'):
            line[a] = '$' + line[a][5:-1]
    return line


def replaceargs(code):
    code = list(code)
    new = ''
    arg = 0
    index = 0
    current = ''
    i = 0
    while i < len(code):
        if code[i] == '$' and not arg:
            arg = 1
            index = i
        elif arg == 1 and code[i] == '{':
            arg = 2
        elif arg == 2 and code[i] in digits:
            current += code[i]
        elif arg == 2 and code[i] == '}':
            code[index:i + 1] = 'args[' + current + ']'
            arg = 0
            index = 0
            current = ''
            i = index
        else:
            arg = 0
            index = 0
            current = ''
        i += 1
    return ''.join(code)


def tokenise(line):
    sq = False
    dq = False
    bt = False
    rb = False
    sb = False
    cb = False
    lg = False
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
        sq or dq or bt or rb or sb or cb or lg):
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
            sb = True
        elif a == ']' and not (
        sq or dq or bt or rb or cb or lg):
            sb = False
        elif a == '{' and not (
        sq or dq or bt or rb or sb or lg):
            cb = True
        elif a == '}' and not (
        sq or dq or bt or rb or sb or lg):
            cb = False
        elif a == '<' and not (
        sq or dq or bt or rb or sb or cb):
            lg = True
        elif a == '>' and not (
        sq or dq or bt or rb or sb or cb):
            lg = False
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


def split_list(s, split_at):
    o = []
    c = []
    for a in s:
        if a == split_at:
            o += [c]
            c = []
        else:
            c += [a]
    return list(filter(None, o + [c]))


#
# BUILTINS
#


class BFList:

    def read(*args):
        return String(get_input(*args)
            if [a for a in args if type(a) is not Null]
            else get_input())

    def get_length(*args):
        if not args:
            call_error('LEN must have at least one argument', error_type='argerr')
        if isinstance(args[0], builtin_types):
            return Integer(len(args[0].value))
        return Integer(len(args[0]))

    def readfile(*args):
        if not args:
            call_error('READFILE must have at least one argument.', error_type='argerr')
        if not isinstance(args[0], String):
            call_error('READFILE first argument must be of type String.', error_type='argerr')
        try:
            with open(args[0].value, 'rb') as f:
                data = f.read()
            data = data.decode('utf-8')
            return String(data)
        except UnicodeDecodeError:
            call_error('READFILE failed to decode file encoding from: ' + str(args[0]), error_type='ioerr')
        except FileNotFoundError:
            call_error('READFILE failed to find a file at path: ' + str(args[0]), error_type='ioerr')


#
# VARIABLES
#

current_file = ''
current_code = ''
global_args = [String(a) for a in sys.argv[1:]]

datatypes_switch = {
    str: String,
    int: Integer,
    float: Float,
    bool: Boolean,
    type(None): Null,
}
builtin_types = tuple(datatypes_switch.values()) + (
    RegexString,
)

global_vars = compact.CompactDict({
    'FILE': global_args[0] if global_args else '<EVAL>',
})
array = compact.CompactDict()
functions = {
    'INTEGER': BuiltinFunction(1, Integer),
    'FLOAT': BuiltinFunction(1, Float),
    'STRING': BuiltinFunction(1, String),
    'REGEX': BuiltinFunction(1, RegexString),
    'BOOLEAN': BuiltinFunction(1, Boolean),
    'NULL': BuiltinFunction(0, Null),

    'READ': BuiltinFunction(1, BFList.read),
    'LEN': BuiltinFunction(1, BFList.get_length),
    'READFILE': BuiltinFunction(1, BFList.readfile),

    'NOT': BuiltinFunction(1, lambda x: Boolean(not x.value)),

    'EXIT': BuiltinFunction(1, sys.exit),
}
procedures = {}
