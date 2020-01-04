'''

MDCL created by Aiden Blishen Cuneo.
First Commit was at: 1/1/2020.

'''

__version__ = '1.3.3'

import ast
import os
import re
import sys
import string
import traceback as tb

from functools import partial
from pprint import pformat

import loader

from compact import CompactList, CompactDict

input_func = 'raw_input' if sys.version_info[0] < 3 else 'input'
get_input = raw_input if sys.version_info[0] < 3 else input


class Function:

    def __init__(self, name, args, code):
        self.name = name
        for a in range(len(args)):
            for b in range(len(args[a])):
                if isinstance(args[a][b], type):
                    args[a][b] = args[a][b].__name__
        self.args = args
        self.code = code

    def check_args(self, args):
        r = [a for a in self.args if '*' not in a]
        for a in range(len(r)):
            if a >= len(args):
                call_error('Function ' + self.name + ' requires at least ' + str(len(r))
                    + ' positional argument' + ('' if len(r) == 1 else 's') + '.', 'argerr')
        for a in range(len(self.args)):
            if a >= len(args):
                args += (Null(),)
            elif type(args[a]).__name__ not in self.args[a] and '@' not in self.args[a]:
                types = '(' + ', '.join([b for b in self.args[a] if b != '*']) + ')'
                call_error('Argument ' + str(a + 1) + ' of function ' + self.name + ' must fit into: '
                    + types + '. "' + type(args[a]).__name__ + '" is invalid.', 'assert')
        return args

    def call(self, args, ex_args=None):
        if ex_args:
            args += ex_args
        args = self.check_args(args)
        r = evaluate([self.code], args=args[:len(self.args)])
        global_vars['_'] = r
        return r


class BuiltinFunction(Function):

    def call(self, args, ex_args=None):
        args = self.check_args(args)
        r = self.code([evaluate(args[:len(self.args)], args=ex_args)][0])
        global_vars['_'] = r
        return r


class Datatype:

    def __init__(self, value):
        self.value = value.value

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
        elif action == 'HAS':
            r = self.HAS(*args)
        else:
            raise AttributeError
        return r


class Integer(Datatype):

    def __init__(self, value):
        mdc_assert(self, value, (int, str) + (
            Integer, Float, String, Boolean, Null),
            'INTEGER', showname=False)
        if isinstance(value, int):
            self.value = value
        elif isinstance(value, str):
            try:
                self.value = int(value)
            except ValueError:
                self.value = 0
        elif isinstance(value, Integer):
            self.value = value.value
        elif isinstance(value, Float):
            self.value = int(round(value.value))
        elif isinstance(value, String):
            try:
                self.value = int(value.value)
            except ValueError:
                self.value = 0
        elif isinstance(value, Boolean):
            self.value = value.value.value
        elif isinstance(value, Null):
            self.value = 0

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

    def DIV(self, other):
        mdc_assert(self, other, (Integer, Float, Boolean), 'DIV')
        if isinstance(other, (Integer, Float)):
            return self.value / other.value, type(other)
        if isinstance(other, Boolean):
            return self.value * int(not other.value.value), Integer

    def PWR(self, other):
        mdc_assert(self, other, (Integer, Float, Boolean), 'PWR')
        if isinstance(other, (Integer, Float)):
            return self.value ** other.value, type(other)
        if isinstance(other, Boolean):
            return self.value ** other.value.value, Integer

    def EQ(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'EQ')
        if isinstance(other, (Integer, Float)):
            return self.value == other.value, Boolean
        if isinstance(other, String):
            return self.value == len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value == other.value.value, Boolean

    def LT(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'LT')
        if isinstance(other, (Integer, Float)):
            return self.value < other.value, Boolean
        if isinstance(other, String):
            return self.value < len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value < other.value.value, Boolean

    def GT(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'GT')
        if isinstance(other, (Integer, Float)):
            return self.value > other.value, Boolean
        if isinstance(other, String):
            return self.value > len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value > other.value.value, Boolean

    def LE(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'LE')
        if isinstance(other, (Integer, Float)):
            return self.value <= other.value, Boolean
        if isinstance(other, String):
            return self.value <= len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value <= other.value.value, Boolean

    def GE(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'GE')
        if isinstance(other, (Integer, Float)):
            return self.value >= other.value, Boolean
        if isinstance(other, String):
            return self.value >= len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value >= other.value.value, Boolean


class Float(Datatype):

    def __init__(self, value):
        mdc_assert(self, value, (int, float, str) + (
            Integer, Float, String, Boolean, Null),
            'FLOAT', showname=False)
        if isinstance(value, int):
            self.value = float(value)
        if isinstance(value, float):
            self.value = value
        elif isinstance(value, str):
            try:
                self.value = float(value)
            except ValueError:
                self.value = 0.0
        elif isinstance(value, Integer):
            self.value = float(value.value)
        elif isinstance(value, Float):
            self.value = value.value
        elif isinstance(value, String):
            try:
                self.value = float(value.value)
            except ValueError:
                self.value = 0.0
        elif isinstance(value, Boolean):
            self.value = float(value.value.value)
        elif isinstance(value, Null):
            self.value = 0.0

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
        mdc_assert(self, other, (Integer, Float, Boolean), 'SUB')
        if isinstance(other, (Integer, Float)):
            return self.value * other.value, type(other)
        if isinstance(other, Boolean):
            return self.value * other.value.value, Integer

    def DIV(self, other):
        mdc_assert(self, other, (Integer, Float, Boolean), 'DIV')
        if isinstance(other, (Integer, Float)):
            return self.value / other.value, type(other)
        if isinstance(other, Boolean):
            return self.value * int(not other.value.value), Integer

    def PWR(self, other):
        mdc_assert(self, other, (Integer, Float, Boolean), 'PWR')
        if isinstance(other, (Integer, Float)):
            return self.value ** other.value, type(other)
        if isinstance(other, Boolean):
            return self.value ** other.value.value, Integer

    def EQ(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'EQ')
        if isinstance(other, (Integer, Float)):
            return self.value == other.value, Boolean
        if isinstance(other, String):
            return self.value == len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value == other.value.value, Boolean

    def LT(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'LT')
        if isinstance(other, (Integer, Float)):
            return self.value < other.value, Boolean
        if isinstance(other, String):
            return self.value < len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value < other.value.value, Boolean

    def GT(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'GT')
        if isinstance(other, (Integer, Float)):
            return self.value > other.value, Boolean
        if isinstance(other, String):
            return self.value > len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value > other.value.value, Boolean

    def LE(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'LE')
        if isinstance(other, (Integer, Float)):
            return self.value <= other.value, Boolean
        if isinstance(other, String):
            return self.value <= len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value <= other.value.value, Boolean

    def GE(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'GE')
        if isinstance(other, (Integer, Float)):
            return self.value >= other.value, Boolean
        if isinstance(other, String):
            return self.value >= len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value >= other.value.value, Boolean


class String(Datatype):

    def __init__(self, value):
        mdc_assert(self, value, (str,) + (
            Integer, Float, String, RegexString, Boolean, Null),
            'STRING', showname=False)
        if isinstance(value, str):
            self.value = value
        elif isinstance(value, (Integer, Float, String, Null)):
            self.value = str(value.value)
        elif isinstance(value, RegexString):
            self.value = str(value.value.pattern)
        elif isinstance(value, Boolean):
            self.value = 'TRUE' if value.value.value else 'FALSE'

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
            return self.value[:-other.value], String
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
        mdc_assert(self, other, (
            Integer, Float, String, RegexString, Boolean, Null),
            'EQ')
        if isinstance(other, Integer):
            return len(self.value) == other.value, Boolean
        if isinstance(other, Float):
            return len(self.value) == Integer(value).value, Boolean
        if isinstance(other, String):
            return self.value == other.value, Boolean
        if isinstance(other, RegexString):
            return self.value == str(other.value.pattern), Boolean
        if isinstance(other, Boolean):
            return bool(self.value), Boolean
        if isinstance(other, Null):
            return not self.value, Boolean

    def INDEX(self, other):
        mdc_assert(self, other, Integer, 'INDEX')
        a = int(BFList.get_length(self).value)
        if int(other.value) > a - 1:
            call_error('String index out of range, ' + str(other) + ' > ' + str(a - 1) + '.', 'argerr')
        return self.value[other.value], String

    def HAS(self, other):
        mdc_assert(self, other, String, 'HAS')
        if isinstance(other, String):
            return other.value in self.value, Boolean


class RegexString(Datatype):

    def __init__(self, value):
        mdc_assert(self, value, (str, re.Pattern, String), 'REGEX', showname=False)
        if isinstance(value, (str, re.Pattern)):
            self.value = re.compile(value)
        elif isinstance(value, String):
            self.value = re.compile(value.value)

    def __repr__(self):
        return pformat(self.value)

    def __str__(self):
        return 'RE' + pformat(self.value.pattern)

    def EQ(self, other):
        mdc_assert(self, other, String, 'EQ')
        a = self.value.match(other.value)
        return int(a) if a else 0, Integer


class Boolean(Datatype):

    def __init__(self, value):
        mdc_assert(self, value, (int, str, bool) + builtin_types, 'BOOLEAN', showname=False)
        if isinstance(value, str):
            value = value.lower()
            if value == 'true':
                self.value = Integer(1)
            elif value == 'false':
                self.value = Integer(0)
            else:
                self.value = Integer(bool(value))
        elif isinstance(value, bool):
            self.value = Integer(value)
        elif isinstance(value, builtin_types):
            self.value = Integer(bool(value.value))
        else:
            self.value = Integer(bool(value))

    def __repr__(self):
        return self.value.__repr__()

    def __str__(self):
        return self.__repr__().upper()

    def __bool__(self):
        return bool(self.value)


class Array(Datatype):

    def __init__(self, value=None):
        mdc_assert(self, value, (int, float, str, bool, tuple, list, type(None)) + builtin_types, 'ARRAY', showname=False)
        if isinstance(value, int):
            self.value = (Integer(value),)
        elif isinstance(value, float):
            self.value = (Float(value),)
        elif isinstance(value, str):
            self.value = (String(value),)
        elif isinstance(value, bool):
            self.value = (Boolean(value),)
        elif isinstance(value, (tuple, list)):
            self.value = tuple(value)
        elif isinstance(value, Null):
            self.value = tuple()
        elif isinstance(value, String):
            self.value = (String(a) for a in value.value)
        elif isinstance(value, builtin_types + (type(None),)):
            self.value = (value,)

    def __repr__(self):
        return '[' + ', '.join(
            (type(a).__name__ + '(' + pformat(a) + ')')
            if isinstance(a, builtin_types) else pformat(a)
            for a in self.value) + ']'

    def __str__(self):
        return '[' + ', '.join(pformat(a) for a in self.value) + ']'

    def __bool__(self):
        return bool(self.value)

    def ADD(self, other):
        mdc_assert(self, other, builtin_types, 'ADD')
        if isinstance(other, Array):
            return self.value + other.value, Array
        else:
            return self.value + (other,), Array

    def SUB(self, other):
        mdc_assert(self, other, (Integer, String), 'SUB')
        if isinstance(other, Integer):
            return self.value[:-other.value], Array
        if isinstance(other, String):
            self.value.remove(other.value)
            return self, Array

    def INDEX(self, other):
        mdc_assert(self, other, Integer, 'INDEX')
        a = int(BFList.get_length(self).value)
        if int(other.value) > a - 1:
            call_error('Array index out of range, ' + str(other) + ' > ' + str(a - 1) + '.', 'argerr')
        return self.value[other.value], type(self.value[other.value])

    def HAS(self, other):
        mdc_assert(self, other, builtin_types, 'HAS')
        return other.value in self.value, Boolean


class Null(Datatype):

    def __init__(self, *args):
        self.value = None

    def __repr__(self):
        return pformat('NULL')

    def __str__(self):
        return 'NULL'

    def __bool__(self):
        return False


def initialise_path(path):
    if not os.path.isdir(path):
        call_error("The path: '" + str(path) + "' could not be found.", 'ioerr')
    os.chdir(path)


def initialise_global_vars(file=None):
    global_vars['FILE'] = String(current_file if file is None else file)
    global_vars['_'] = Null()
    global_vars[','] = Null()


def call_error(text, error_type=None, line=None, showfile=True):
    if isinstance(line, (list, tuple)):
        line = ' '.join([str(a) for a in line])
    print(end='\n')
    e = 'ERROR'
    if error_type == 'eval':
        e = 'ERROR attempting to run eval statement'
    elif error_type == 'exp':
        e = 'ERROR attempting to evaluate expression'
    elif error_type == 'ioerr':
        e = 'IOERROR'
    elif error_type == 'argerr':
        e = 'ARGUMENT ERROR'
    elif error_type == 'assert':
        e = 'ASSERTION ERROR'
    elif error_type == 'var':
        e = 'VAR ERROR'
    elif error_type == 'syntax':
        e = 'SYNTAX ERROR'
    elif error_type == 'attr':
        e = 'ATTRIBUTE ERROR'
    elif error_type == 'recursion':
        e = 'RECURSION ERROR'
    elif error_type == 'type':
        e = 'TYPE ERROR'
    elif error_type == 'value':
        e = 'VALUE ERROR'
    elif error_type == 'fatal':
        print('A fatal error has occurred which has terminated the runtime environment.')
        print('PYTHON TRACEBACK:')
        tb.print_exc()
        print('Please consider posting this traceback as an issue on the GitHub Repository page at: '
            'https://github.com/aidencuneo/MDC-Lang')
        sys.exit()
    thisfile = os.path.abspath(current_file)
    method = []
    while thisfile.endswith('METHOD>'):
        method += [thisfile[rindex(thisfile, '\n') + 1:-7]]
        thisfile = thisfile[:rindex(thisfile, '\n') - 1:]
    print('> ' + e + (
        ' at file "' + thisfile + '", in ' + ', in '.join(
            method[::-1] if method else ['line ' + str(current_line)])
        if showfile else '') + ':')
    if not method:
        codeline = loader.get_code('', specificline=current_line, setcode=current_code)
        if isinstance(codeline, str):
            print('  -> ' + codeline.strip())
    if line:
        print('  ~~ ' + line)
    print('  :: ' + text)
    sys.exit()


def mdc_assert(first, second, types, action, showall=False, showname=True):
    if not isinstance(types, (list, tuple)):
        types = types,
    if not isinstance(second, types):
        types = '(' + ', '.join([a.__name__ for a in types if showall or (not showall and a in builtin_types)]) + ')'
        s = type(first).__name__ + ' o' if showname else 'O'
        call_error(s + 'perand type for ' + action + ' must fit into: ' + types + '. "' + type(second).__name__ + '" is invalid.',
            'assert')


def eval_statement(code, args, error):
    try:
        args = [evaluate([z], error=error) for z in args]
        out = eval(code, (CompactDict({'args': args}) + globals()).as_dict())
        return eval_datatypes([out], error=error, dostrings=True)[0]
    except BaseException as e:
        if isinstance(e, SystemExit):
            print('\nThe following error occurred as a result of the above error:')
        call_error(str(e), 'eval', error)


def run(rawcode, filename=None, tokenised=False, oneline=False, echo=True, raw=False, yielding=False, localargs=None):
    global current_file
    global current_code
    global current_line
    code = rawcode
    if not current_file:
        initialise_global_vars(file=filename)
    if filename != 'keep':
        current_file = '<EVAL>' if filename is None else filename
        current_code = current_code if filename is None else code
        current_line = 1
    if raw:
        code = loader.process(code)
    if oneline:
        code = [code]
    lines = loader.tokenise_file(rawcode, dofilter=False)
    o = ''
    yielded = []
    i = 0
    while i < len(code):
        current_line += lines[i].count('\n')
        global_vars['LINE'] = Integer(current_line)
        if not code[i].strip():
            i += 1
            continue
        if tokenised:
            a = replacekeys(code[i], args=localargs)
        else:
            a = replacekeys(loader.tokenise(code[i]), args=localargs)
        if ':' in a:
            if a[0] == 'NEW':
                if len(a) < 4:
                    call_error('Function declaration requires at least a function name, function code, and the ":" separator.', 'argerr')
                name = a[1]
                func = a[-1]
                arguments = tuple(filter(None, split_list(a[2:-1], ':')))
                types = [b.__name__ for b in builtin_types]
                optionals = False
                for b in arguments:
                    for c in b:
                        if c not in types and not c == '*' and not c == '@':
                            call_error(pformat(c) + ' is not defined as a type.', 'attr')
                    if '*' in b:
                        optionals = True
                    elif optionals and not '*' in b:
                        call_error('Optional function arguments must be after all positional arguments.', 'syntax')
                functions[name] = Function(name, arguments, func)
            elif a[0] == 'IF':
                if len(a) < 3:
                    call_error('IF statement requires at least a condition, the ":" separator, and code to run.', 'syntax')
                contents = tuple(filter(None, split_list(a[1:], ':')))
                if not contents[1:]:
                    call_error('IF statement requires at least a condition, the ":" separator, and code to run.', 'syntax')
                conditions = [contents[0]]
                runcodes = [contents[1]]
                haselse = False
                con = contents[2:]
                b = 0
                while b < len(con):
                    if con[b][0] == 'IF':
                        call_error('IF can not be placed after ELIF or ELSE in the same chain.', 'syntax')
                    elif con[b][0] == 'ELIF':
                        if len(con[b]) < 2 or b + 2 >= len(con):
                            call_error('ELIF statement requires at least a condition, the ":" separator, and code to run.', 'syntax')
                        if haselse:
                            call_error('ELIF can not be placed after ELSE in the same chain.', 'syntax')
                        conditions += [con[b][1:]]
                        runcodes += [con[b + 1]]
                        b += 1
                    elif con[b][0] == 'ELSE':
                        haselse = True
                        if b + 1 >= len(con):
                            call_error('ELSE statement requires at least the ":" separator and code to run.', 'syntax')
                        if len(con[b]) > 1:
                            call_error('ELSE statement can not have any conditions, use the ELIF statement to evaluate conditions.', 'syntax')
                        conditions += ['ELSE']
                        runcodes += [con[b + 1]]
                        b += 1
                    elif haselse:
                        call_error('ELSE statement ends an IF-ELIF-ELSE chain. Tokens can not be evaluated after one.', 'syntax')
                    b += 1
                if len(conditions) != len(runcodes):
                    call_error('Number of conditions must be equal to number of code sets to run in an IF-ELIF-ELSE chain.', 'syntax')
                for b in range(len(conditions)):
                    e = False
                    if conditions[b] == 'ELSE':
                        e = True
                    elif Boolean(evaluate(conditions[b], error=code[i], args=localargs)):
                        e = True
                    if e:
                        ev = evaluate(runcodes[b], error=code[i], args=localargs)
                        if not isinstance(ev, Null):
                            o += str(ev)
                            if echo:
                                sys.stdout.write(str(ev))
                        break
            elif a[0] == 'WHILE':
                if len(a) < 3:
                    call_error('WHILE loop requires at least a condition, the ":" separator, and code to run.', 'syntax')
                contents = tuple(filter(None, split_list(a[1:], ':')))
                if not contents[1:]:
                    call_error('WHILE loop requires at least a condition, the ":" separator, and code to run.', 'syntax')
                condition = contents[0]
                runcode = contents[1]
                while Boolean(evaluate(condition, error=code[i], args=localargs)):
                    ev = evaluate(runcode, error=code[i], args=localargs)
                    if not isinstance(ev, Null):
                        o += str(ev)
                        if echo:
                            sys.stdout.write(str(ev))
            elif a[0] == 'FOR':
                if len(a) < 3:
                    call_error('FOR loop requires at least a variable name, iterable, the ":" separator, and code to run.', 'syntax')
                contents = tuple(filter(None, split_list(a[1:], ':')))
                if not contents[2:]:
                    call_error('FOR loop requires at least a variable name, iterable, the ":" separator, and code to run.', 'syntax')
                variable = contents[0][0]
                iterable = evaluate(contents[1], error=code[i], args=localargs)
                runcode = contents[2]
                if not variable:
                    call_error('FOR loop variable name can not be empty.', 'syntax')
                if variable in global_vars and variable != ',':
                    call_error('Name ' + pformat(variable) + ' is already defined in the global variables list.', 'var')
                if variable in local_vars:
                    call_error('Name ' + pformat(variable) + ' is already defined in the local variables list.', 'var')
                if not iterable:
                    call_error('FOR loop iterable can not be NULL.', 'syntax')
                if not runcode:
                    call_error('FOR loop code to run can not be empty.', 'syntax')
                if not isinstance(iterable, (Integer, String, Array)):
                    call_error('FOR loop can only iterate over an Array. FOR loops also support: (Integer, String).', 'type')
                if isinstance(iterable, Integer):
                    iterable = range(iterable.value)
                else:
                    iterable = iterable.value
                for value in iterable:
                    local_vars[variable] = value
                    global_vars[','] = value
                    ev = evaluate(runcode, error=code[i], args=localargs)
                    if not isinstance(ev, Null):
                        o += str(ev)
                        if echo:
                            sys.stdout.write(str(ev))
            else:
                key = ''.join(a[:a.index(':')])
                if key.startswith('array[(') and key.endswith(')]'):
                    key = ast.literal_eval(key[6:-1])
                else:
                    call_error('Invalid variable key. Variable keys must be surrounded by parentheses.', 'var')
                value = evaluate(a[a.index(':') + 1:], error=code[i], args=localargs)
                array[key] = value
        elif a[0] == 'NEW':
            call_error('Function declaration is missing the ":" separator.', 'syntax')
        elif a[0] == 'IF':
            call_error('IF statement is missing the ":" separator.', 'syntax')
        elif a[0] == 'WHILE':
            call_error('WHILE loop is missing the ":" separator.', 'syntax')
        elif a[0] == 'FOR':
            call_error('FOR loop is missing the ":" separator.', 'syntax')
        elif a[0] == 'IMPORT':
            if len(a) < 2:
                call_error('IMPORT statement requires at least one argument.', 'argerr')
            fname = str(evaluate([a[1]], error=code[i], args=localargs))
            newcode = loader.get_code(fname)
            if isinstance(newcode, Exception):
                call_error('There was an error attempting to read from ' + fname + '.', 'ioerr')
            oldfile = current_file
            oldcode = current_code
            oldline = current_line
            run(newcode, fname, raw=True)
            current_file = oldfile
            current_code = oldcode
            current_line = oldline
        elif a[0] == 'DEFINE':
            if len(a) < 3:
                call_error('DEFINE statement requires two arguments, KEY and VALUE.', 'argerr')
            key = a[1].strip()
            if not key:
                call_error('DEFINE statement key must not be empty.', 'argerr')
            if key in global_vars or key in local_vars:
                call_error('Constant with key ' + pformat(key) + ' already exists. Constants can not be redefined.', 'syntax')
            value = evaluate(a[2:], error=code[i], args=localargs)
            local_vars[key] = value
        elif a[0] == 'GOTO':
            if current_file.endswith('METHOD>'):
                call_error('GOTO statement can not run in the current scope.', 'syntax')
            if not a[1:]:
                call_error('GOTO statement requires at least one argument.', 'argerr')
            line = evaluate(a[1:], error=code[i], args=localargs)
            try:
                line = int(line.value)
                if line < 0:
                    line = current_line + line
                elif not line:
                    line = current_line
                current_line = line
                if not line <= current_code.count('\n') + 1:
                    call_error('GOTO statement argument must be lower than the line count of the current file.')
            except ValueError:
                call_error('GOTO statement argument must be a valid line number.')
            newcode = loader.get_code('', fromline=line, setcode=current_code)
            if isinstance(newcode, Exception):
                call_error('There was an error attempting to read from ' + current_file + '.', 'ioerr')
            code = loader.process(newcode)
            filename = 'keep'
            tokenised = False
            oneline = False
            i = 0
            continue
        elif a[0] == 'YIELD':
            if not yielding:
                call_error('Yielding is not possible from the current scope.', 'syntax')
            yielded += [evaluate(a[1:], error=code[i], args=localargs)]
        else:
            a = evaluate(a, error=code[i], args=localargs)
            if type(a) in builtin_types:
                o += str(a)
                if echo:
                    sys.stdout.write(str(a))
        i += 1
    if yielding:
        return yielded
    return o


def eval_datatypes(exp, error=None, dostrings=False):
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
                    call_error('Variable key does not exist.', 'var', '(' + new[a][9:-3] + ')')
        if isinstance(new[a], tuple([b for b in datatypes_switch.keys() if dostrings or b != str])):
            new[a] = datatypes_switch[type(new[a])](new[a])
        if not isinstance(new[a], str):
            pass
        elif re.match('^(-|\+)*[0-9]+', new[a]): # Is new[a] an integer? If so, assign Integer() class.
            new[a] = Integer(new[a])
        elif re.match('^RE(\'|").+(\'|")', new[a]): # Is new[a] a Regex String? If so, assign Regex() class.
            try:
                new[a] = RegexString(ast.literal_eval(new[a][2:]))
            except Exception:
                call_error('Invalid Regex String.', 'syntax', error)
        elif re.match("^'.+'", new[a]) or new[a] == "''": # Is new[a] a string with single quotes? If so, assign String() class using RAW value.
            new[a] = String(new[a][1:-1])
        elif re.match('^".+"', new[a]) or new[a] == '""': # Is new[a] a string with double quotes? If so, assign evaluated String() class.
            try:
                new[a] = String(ast.literal_eval(new[a]))
            except Exception:
                call_error('Invalid String.', 'syntax', error)
        elif new[a] in ('TRUE', 'FALSE', 'True', 'False'): # Is new[a] a boolean? If so, assign Boolean() class.
            new[a] = Boolean(new[a])
        elif new[a] in ('null', 'NULL', 'None'): # Is new[a] null? If so, assign Null() class.
            new[a] = Null()
        a += 1
    return new


def eval_functions(exp, error=None, args=None):
    global current_file
    global current_code
    global current_line
    if not exp:
        return exp
    new = [a for a in exp]
    a = 0
    while a < len(new):
        if isinstance(new[a], builtin_types):
            pass
        elif new[a].startswith('args[') and new[a].endswith(']'):
            key = int(new[a][5:-1])
            if args:
                if key >= len(args):
                    call_error('Local argument list index out of range, ' + str(key) + ' > ' + str(len(args) - 1) + '.', 'argerr', error)
                new[a] = args[key]
            else:
                if key >= len(global_args):
                    call_error('Global argument list index out of range, ' + str(key) + ' > ' + str(len(global_args) - 1) + '.', 'argerr', error)
                new[a] = global_args[key]
        elif new[a] in functions:
            limit = len(functions[new[a]].args)
            f = evaluate(new[a + 1:a + 1 + limit], error=error, args=args)
            if not isinstance(f, (tuple, list)):
                f = f,
            oldfile = current_file
            oldcode = current_code
            oldline = current_line
            current_file = current_file + '\n<' + new[a] + 'METHOD>'
            current_code = functions[new[a]].code
            current_line = 1
            new[a] = functions[new[a]].call(f, ex_args=args)
            current_file = oldfile
            current_code = oldcode
            current_line = oldline
            del new[a + 1:a + 1 + limit]
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
        'HAS',
    )
    new = [a for a in exp]
    new = eval_functions(eval_datatypes(new, error=error), error=error, args=args)
    a = 0
    while a < len(new):
        if isinstance(new[a], builtin_types):
            pass
        elif new[a] in reps:
            if a - 1 < 0:
                call_error('Missing first argument for ' + new[a] + ' method.', 'syntax', error)
            if a + 1 >= len(new):
                call_error('Missing second argument for ' + new[a] + ' method.', 'syntax', error)
            try:
                vals = new[a - 1].do_action(new[a], (evaluate([new[a + 1]], error=error, args=args),))
                settype = vals[1] if isinstance(vals, tuple) else type(new[a - 1])
                new[a] = settype(vals[0])
                del new[a + 1]
                del new[a - 1]
                a -= 2
            except AttributeError:
                call_error('Type ' + type(new[a - 1]).__name__ + ' does not have a method for handling ' + new[a], 'attr', error)
        elif new[a] == 'AND':
            if a - 1 < 0:
                call_error('AND requires a left hand argument.', 'argerr', error)
            if a + 1 >= len(new):
                call_error('AND requires a right hand argument.', 'argerr', error)
            left = evaluate(replacekeys([new[a - 1]], args=args), error=error, args=args)
            right = evaluate(replacekeys([new[a + 1]], args=args), error=error, args=args)
            new[a] = Boolean(Boolean(left) and Boolean(right))
            del new[a + 1]
            del new[a - 1]
            a -= 1
        elif new[a] == 'OR':
            if a - 1 < 0:
                call_error('OR requires a left hand argument.', 'argerr', error)
            if a + 1 >= len(new):
                call_error('OR requires a right hand argument.', 'argerr', error)
            left = evaluate(replacekeys([new[a - 1]], args=args), error=error, args=args)
            right = evaluate(replacekeys([new[a + 1]], args=args), error=error, args=args)
            new[a] = Boolean(Boolean(left) or Boolean(right))
            del new[a + 1]
            del new[a - 1]
            a -= 1
        elif new[a] == 'TO':
            if a + 1 >= len(new):
                call_error('TO requires a right hand argument.', 'argerr', error)
            left = evaluate(replacekeys([new[a - 1]], args=args), error=error, args=args) if a > 0 else Integer(0)
            right = evaluate(replacekeys([new[a + 1]], args=args), error=error, args=args)
            if not isinstance(left, Integer):
                call_error('TO requires an Integer as left hand argument.', 'type', error)
            if not isinstance(right, Integer):
                call_error('TO requires an Integer as right hand argument.', 'type', error)
            step = 1
            if right.value < left.value:
                step = -1
                right.value -= 1
            else:
                right.value += 1
            new[a] = Array(tuple(Integer(z) for z in range(left.value, right.value, step)))
            del new[a + 1]
            if a > 0:
                del new[a - 1]
                a -= 1
        elif new[a] == 'SKIP':
            if a - 1 < 0:
                call_error('SKIP requires a left hand argument.', 'argerr', error)
            if a + 1 >= len(new):
                call_error('SKIP requires a right hand argument.', 'argerr', error)
            left = evaluate(replacekeys([new[a - 1]], args=args), error=error, args=args)
            right = evaluate(replacekeys([new[a + 1]], args=args), error=error, args=args)
            if not isinstance(left, Array):
                call_error('SKIP can only skip items in an Array.', 'type', error)
            if not isinstance(right, Integer):
                call_error('SKIP can only skip through an Array using an Integer as index.', 'type', error)
            if not right.value:
                call_error('Right hand argument for SKIP can not be 0.', 'value', error)
            new[a] = Array(left.value[0::right.value])
            del new[a + 1]
            del new[a - 1]
            a -= 1
        elif new[a].startswith('<EVAL>') and new[a].endswith('</EVAL>'):
            new[a] = new[a][6:-7]
            b = new[a].split('\n\\')
            new[a] = eval_statement(b[0], args, b[1])
        elif (new[a].startswith('[') or new[a].endswith(']')) and not new[a].startswith('args['):
            if not new[a].startswith('['):
                call_error('Unmatched ' + pformat(']') + '.', 'syntax', error)
            if not new[a].endswith(']'):
                call_error('Unmatched ' + pformat('[') + '.', 'syntax', error)
            values = evaluate(replacekeys(loader.tokenise(new[a][1:-1].strip()), args=args), error=error, args=args)
            if isinstance(values, (tuple, list)):
                new[:a + 1:] = values
            else:
                new[a] = values
        elif new[a].startswith('<') or new[a].endswith('>'):
            if not new[a].startswith('<'):
                call_error('Unmatched ' + pformat('>') + '.', 'syntax', error)
            if not new[a].endswith('>'):
                call_error('Unmatched ' + pformat('<') + '.', 'syntax', error)
            if not a > 0:
                call_error('Shorthand condition requires a left hand argument.', 'argerr', error)
            if not a <= len(new):
                call_error('Shorthand condition requires a right hand argument.', 'argerr', error)
            condition = evaluate(replacekeys(loader.tokenise(new[a][1:-1].strip()), args=args), error=error, args=args)
            r = replacekeys(loader.tokenise(new[a][1:-1].strip()), args=args)
            left = evaluate(replacekeys([new[a - 1]], args=args), error=error, args=args)
            right = evaluate(replacekeys([new[a + 1]], args=args), error=error, args=args)
            del new[a + 1]
            del new[a - 1]
            a -= 1
            new[a] = left if bool(Boolean(condition)) else right
        elif new[a].startswith('{') or new[a].endswith('}'):
            if not new[a].startswith('{'):
                call_error('Unmatched ' + pformat('}') + '.', 'syntax')
            if not new[a].endswith('}'):
                call_error('Unmatched ' + pformat('{') + '.', 'syntax')
            value = run(new[a].strip()[1:-1].strip(), filename='keep', echo=True, raw=True, yielding=True, localargs=args)
            new[a] = Array(value)
            if not value:
                new[a] = Null()
            elif len(value) == 1:
                new[a] = value[0]
        elif new[a] in local_vars:
            new[a] = local_vars[new[a]]
        elif new[a] in global_vars:
            new[a] = global_vars[new[a]]
        elif new[a] not in functions:
            token = new[a]
            if len(token) > 100:
                token = token[:97] + '...'
            call_error('Undefined Token: ' + pformat(token), 'syntax', error)
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
            print(code)
            call_error(str(e), 'exp', error)
    return out


def replacekeys(line, args=None):
    for a in range(len(line)):
        if isinstance(line[a], builtin_types):
            pass
        elif line[a].startswith('(') and line[a].endswith(')'):
            values = []
            for b in line[a][1:-1].split(','):
                hx = b.strip().upper()
                if not all([c in loader.digits + 'ABCDEF' for c in hx]):
                    call_error('Invalid variable key. Variable keys must be in Hexadecimal form, including commas and: "0123456789ABCDEF".',
                        'var', line)
                values += ['0x' + hx]
            line[a] = 'array[(' + ','.join(values) + ',)]'
        elif line[a].startswith('$'):
            b = line[a][1]
            c = ''
            line[a] = line[a][2:]
            for z in range(len(line[a])):
                if line[a][z] in loader.digits:
                    b += line[a][z]
                else:
                    c += line[a][z]
            line[a] = 'args[' + b + ']'
            if c:
                line.insert(a + 1, c)
            if args is not None:
                key = int(line[a][5:-1])
                if key >= len(args):
                    call_error('Local argument list index out of range, ' + str(key) + ' > ' + str(len(args) - 1) + '.', 'argerr', line)
                line[a] = args[key]
        elif line[a].startswith('`') and line[a].endswith('`'):
            line[a] = '<EVAL>' + replaceargs(line[a][1:-1]) + '\n\\' + pformat(line[a]) + '</EVAL>'
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
        elif arg == 2 and code[i] in loader.digits:
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


def rindex(s, i):
    i = i[0]
    s = s[::-1]
    for a in range(len(s)):
        if s[a] == i:
            return len(s) - a
    return -1


#
# BUILTINS
#


class BFList:

    @staticmethod
    def read(*args):
        return String(get_input(*args)
            if [a for a in args if type(a) is not Null]
            else get_input())

    @staticmethod
    def get_length(*args):
        if isinstance(args[0], builtin_types):
            return Integer(len(args[0].value))
        return Integer(len(args[0]))

    @staticmethod
    def readfile(*args):
        if not isinstance(args[0], String):
            call_error('READFILE first argument must be of type String.', 'argerr')
        try:
            with open(args[0].value, 'rb') as f:
                data = f.read()
            data = data.decode('utf-8')
            return String(data)
        except UnicodeDecodeError:
            call_error('READFILE failed to decode file encoding from: ' + str(args[0]), 'ioerr')
        except FileNotFoundError:
            call_error('READFILE failed to find a file at path: ' + str(args[0]), 'ioerr')

    @staticmethod
    def get_type(*args):
        if not args:
            args = [Null()]
        return String(type(args[0]).__name__)

    @staticmethod
    def echo(args):
        content = String('') if isinstance(args[0], Null) else args[0]
        sep = args[1] if isinstance(args[1], String) else String(' ')
        end = args[2] if isinstance(args[2], String) else String('\n')
        if isinstance(args[0], Array):
            content = String(sep.value.join([str(a) for a in content.value]))
        print(content.value, end=end.value)
        return String('')


#
# VARIABLES
#

current_file = ''
current_code = ''
current_line = 1
global_args = [String(a) for a in sys.argv[1:]]

datatypes_switch = {
    str: String,
    int: Integer,
    float: Float,
    bool: Boolean,
    tuple: Array,
    list: Array,
    type(None): Null,
}
builtin_types = tuple(datatypes_switch.values()) + (
    RegexString,
)

global_vars = CompactDict()
local_vars = CompactDict()
array = CompactDict()
functions = {
    'INTEGER': BuiltinFunction('INTEGER',
        [],
        Integer),
    'FLOAT': BuiltinFunction('FLOAT',
        [[Integer, '*']],
        Float),
    'STRING': BuiltinFunction('STRING',
        [[Integer, '*']],
        String),
    'REGEX': BuiltinFunction('REGEX',
        [[String, '*']],
        RegexString),
    'BOOLEAN': BuiltinFunction('BOOLEAN',
        [[Integer, '*']],
        Boolean),
    'ARRAY': BuiltinFunction('ARRAY',
        [['@']],
        Array),
    'NULL': BuiltinFunction('NULL',
        [],
        Null),

    'READ': BuiltinFunction('READ',
        [[String, '*']],
        BFList.read),
    'LEN': BuiltinFunction('LEN',
        [[String, Array]],
        BFList.get_length),
    'READFILE': BuiltinFunction('READFILE',
        [[String]],
        BFList.readfile),
    'TYPE': BuiltinFunction('TYPE',
        [['@']],
        BFList.get_type),
    'ECHO': BuiltinFunction('ECHO',
        [['@'], ['*', 'String'], ['*', 'String']],
        BFList.echo),

    'NOT': BuiltinFunction('NOT',
        [['@']],
        lambda x: Boolean(not x.value)),

    'EXIT': BuiltinFunction('EXIT',
        [],
        lambda x: (String(''), sys.exit())[0]),
}
