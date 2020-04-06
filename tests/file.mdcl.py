'''

MDCL created by Aiden Blishen Cuneo.
First Commit was at: 1/1/2020.


PATTERN:

definition,

    __init__,

    __magicmethods__,

    appending/adding methods,

    splicing/removing methods,

    getting/retrieving methods,

    boolean returning methods,

'''


class CompactList:

    def __init__(self, *values):
        __slots__ = []
        self._value = ()
        values = values[0] if len(values) == 1 else values
        for a in values:
            self.append(a)
    
    def __repr__(self):
        return str(list(self._value))
    
    def __str__(self):
        return str(list(self._value))
    
    def __eq__(self, value):
        return self._value == value
    
    def __getitem__(self, item):
        return self._value[item]
    
    def __setitem__(self, item, value):
        self.setitem(item, value)
    
    def __delattr__(self, index):
        self.delete_from(index)

    def __delitem__(self, index):
        self.delete_from(index)
    
    def __contains__(self, item):
        return item in self._value
    
    def setitem(self, item, value):
        self._value = list(self._value)
        self._value[item] = value
        self._value = tuple(self._value)

    def append(self, value):
        self._value += tuple([value])

    def extend(self, value):
        self._value += tuple(value)

    def delete_from(self, index):
        self._value = list(self._value)
        del self._value[index]
        self._value = tuple(self._value)
    
    def index(self, item):
        return self._value.index(item)

    def is_empty(self):
        return not bool(self._value)

    def has_data(self):
        return bool(self._value)


class CompactDict:

    def __init__(self, values=None):
        __slots__ = []
        self._value = CompactList()
        values = {} if values is None else values
        for a in values:
            self.setitem(a, values[a])

    def __repr__(self):
        return str(self.as_dict())

    def __str__(self):
        return str(self.as_dict())

    def __add__(self, other):
        for a in other:
            self[a] = other[a]
        return self

    def __delattr__(self, key):
        self.delete_key(key)

    def __getitem__(self, item):
        return self.getitem(item)

    def __setitem__(self, key, value):
        return self.setitem(key, value)

    def __delitem__(self, key):
        self.delete_key(key)
    
    def __contains__(self, key):
        return key in self.as_dict()

    def setitem(self, key, value):
        if key in self.keys():
            self._value[self.keys().index(key)][1] = value
        else:
            self._value.append(CompactList(key, value))

    def getitem(self, name):
        if all([a in '0123456789' for a in str(name)]) and name not in self.keys()._value:
            return self.keys()[name]
        return self.as_dict()[name]

    def as_dict(self):
        return {a[0] : a[1] for a in self._value}
    
    def keys(self):
        return CompactList([a[0] for a in self._value])
    
    def values(self):
        return CompactList([a[1] for a in self._value])
    
    def delete_key(self, key):
        if key in self.keys()._value:
            del self._value[self.keys().index(key)]
        else:
            raise KeyError

    def is_empty(self):
        return not bool(self.as_dict())

    def has_data(self):
        return bool(self.as_dict())

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

'''

MDCL created by Aiden Blishen Cuneo.
First Commit was at: 1/1/2020.

'''

_debug_mode = True
_is_compiled = True
__version__ = '1.6.7'

import ast
import datetime
import os
import re
import signal
import sys
import time
import traceback as tb
import types

from copy import copy, deepcopy
from pprint import pformat



get_input = raw_input if sys.version_info[0] < 3 else input


class SignalCatches:

    def __init__(self):
        self.switches = {
            'INT': True,
            'TSTP': True,
            'SEGV': True,

            'ECHO': True,
        }
        signal.signal(signal.SIGINT, self.keyboard_interrupt)
        if 'SIGTSTP' in dir(signal):
            signal.signal(signal.SIGTSTP, self.keyboard_interrupt)
        signal.signal(signal.SIGSEGV, self.segmentation_fault)

    def send(self, signal):
        if signal == 'SIGINT':
            self.keyboard_interrupt()
        elif signal == 'SIGTSTP':
            self.keyboard_interrupt()
        elif signal == 'SIGSEGV':
            self.segmentation_fault()

    def keyboard_interrupt(self, signal=None, frame=None):
        if self.switches['INT']:
            call_error(error_type='keyboardinterrupt')

    def eof_error(self, signal=None, frame=None):
        if self.switches['TSTP']:
            call_error(error_type='eoferror')

    def segmentation_fault(self, signal=None, frame=None):
        if self.switches['SEGV']:
            call_error('Segmentation Fault.', 'fatal')


class BaseDatatype:

    def __init__(self, value=None, start_data=None, is_object=True):
        self.data = {} if value is None else {
            'value': value,
        }
        if start_data:
            self.data.update(start_data)
        if is_object:
            self.data.update({
                'map': BuiltinFunction('map',
                    [['@']],
                    self._map),
            })
        self.data = CompactDict(self.data)

    def do_action(self, action, args):
        if action in self.data:
            f = self.data[action]
        elif action == 'add':
            f = self.add
        elif action == 'sub':
            f = self.sub
        elif action == 'mult':
            f = self.mult
        elif action == 'div':
            f = self.div
        elif action == 'pwr':
            f = self.pwr
        elif action == 'mod':
            f = self.mod
        elif action == 'eq':
            f = self.eq
        elif action == 'lt':
            f = self.lt
        elif action == 'gt':
            f = self.gt
        elif action == 'le':
            f = self.le
        elif action == 'ge':
            f = self.ge
        elif action == 'has':
            f = self.has
        else:
            raise AttributeError
        if isinstance(f, (Function, BuiltinFunction)):
            val = evaluate(['!', f, self] + list(args), func_self=False)
            return val, type(val)
        return f(*args)

    # Begin built-in Object functions, prefix with _

    def _map(self, args):
        try:
            return Array(list([call_function(args[0], a) for a in self.value]))
        except TypeError:
            call_error(pformat(type(self).__name__) + ' object is not iterable.', 'type')
            exit()
        return Null()


class Function(BaseDatatype):

    def __init__(self, name, args=None, code=None):
        if isinstance(name, (Function, BuiltinFunction)):
            self.name = name.name
            self.args = name.args
            self.code = name.code
        else:
            if args is None or code is None:
                call_error('function can not be declared without second or third arguments '
                    'if first argument is not a Function. This is a Python error.', 'fatal')
            for a in range(len(args)):
                for b in range(len(args[a])):
                    if isinstance(args[a][b], type):
                        args[a][b] = args[a][b].__name__
            self.name = name
            self.args = args
            self.code = code
        self.value = self.get_value()
        super().__init__(self.value, is_object=False)
        self.data['name'] = self.name

    def __repr__(self):
        return self.get_value()

    def __str__(self):
        return repr(self)

    def get_value(self):
        if self.name == '<InlineFunction>':
            return self.name
        return '<Function ' + self.name + '>'

    def check_args(self, args):
        r = [a for a in self.args if '*' not in a]
        for a in range(len(r)):
            if a >= len(args):
                call_error('function ' + self.name + ' requires at least ' + str(len(r))
                    + ' positional argument' + ('' if len(r) == 1 else 's') + '.', 'argerr')
        for a in range(len(self.args)):
            if a >= len(args):
                args += (Null(),)
        if len(args) > len(self.args):
            call_error('function ' + self.name + ' received ' + str(len(args)) + ' arguments, '
                'maximum amount for this function is ' + str(len(self.args)) + '.', 'argerr')
        return args

    def call(self, args, ex_args=None):
        if isinstance(args, Array):
            args = args.value
        args = self.check_args(args)
        if isinstance(self.code, (types.FunctionType, types.BuiltinFunctionType, type)):
            r = translate_datatypes(self.code(*args))
            global_vars['_'] = r
            return r
        if ex_args:
            args += ex_args
        r = evaluate([self.code], args=args[:len(self.args)])
        global_vars['_'] = r
        return r


class BuiltinFunction(Function):

    def call(self, args, ex_args=None):
        if isinstance(args, Array):
            args = args.value
        args = self.check_args(args)
        r = translate_datatypes(self.code(args))
        global_vars['_'] = r
        return r


class Integer(BaseDatatype):

    def __init__(self, value):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
        if isinstance(value, int):
            self.value = value
        elif 'Integer' in value.data:
            self.value = evaluate((value.data['Integer'], '()'))
        mdc_assert(self, value, (int, float) + (
            Integer, Float, String, Boolean, Null),
            'int', showname=False)
        if isinstance(value, int):
            self.value = value
        elif isinstance(value, float):
            self.value = round(value)
        elif isinstance(value, Integer):
            self.value = value.value
        elif isinstance(value, Float):
            self.value = round(value.value)
        elif isinstance(value, String):
            try:
                self.value = round(float(value.value))
            except ValueError:
                call_error('String ' + pformat(value) + ' can not '
                    'be converted into an Integer.', 'type')
        elif isinstance(value, Boolean):
            self.value = value.value.value
        elif isinstance(value, Null):
            self.value = 0
        super().__init__(self.value)

    def __repr__(self):
        return str(self.value)

    def __bool__(self):
        return bool(self.value)

    def _integer(self):
        return self.value

    def foriter(self):
        return Array(translate_datatypes(tuple(range(self.value))))

    def add(self, other):
        mdc_assert(self, other, (Integer, Float, String), 'add')
        if isinstance(other, (Integer, Float)):
            return self.value + other.value, type(other)
        if isinstance(other, String):
            return str(self.value) + other.value, String

    def sub(self, other):
        mdc_assert(self, other, (Integer, Float), 'sub')
        return self.value - other.value, type(other)

    def mult(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'mult')
        if isinstance(other, (Integer, Float)):
            return self.value * other.value, type(other)
        if isinstance(other, String):
            return self.value * other.value, String
        if isinstance(other, Boolean):
            return self.value * other.value.value, Integer

    def div(self, other):
        mdc_assert(self, other, (Integer, Float, Boolean), 'div')
        if isinstance(other, (Integer, Float)):
            return self.value / other.value, type(other)
        if isinstance(other, Boolean):
            return self.value * int(not other.value.value), Integer

    def pwr(self, other):
        mdc_assert(self, other, (Integer, Float, Boolean), 'pwr')
        if isinstance(other, (Integer, Float)):
            return self.value ** other.value, type(other)
        if isinstance(other, Boolean):
            return self.value ** other.value.value, Integer

    def mod(self, other):
        mdc_assert(self, other, (Integer, Float, Boolean), 'mod')
        if isinstance(other, (Integer, Float)):
            return self.value % other.value, type(other)
        if isinstance(other, Boolean):
            return self.value % other.value.value, Integer

    def eq(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'eq')
        if isinstance(other, (Integer, Float)):
            return self.value == other.value, Boolean
        if isinstance(other, String):
            return self.value == len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value == other.value.value, Boolean

    def lt(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'lt')
        if isinstance(other, (Integer, Float)):
            return self.value < other.value, Boolean
        if isinstance(other, String):
            return self.value < len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value < other.value.value, Boolean

    def gt(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'gt')
        if isinstance(other, (Integer, Float)):
            return self.value > other.value, Boolean
        if isinstance(other, String):
            return self.value > len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value > other.value.value, Boolean

    def le(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'le')
        if isinstance(other, (Integer, Float)):
            return self.value <= other.value, Boolean
        if isinstance(other, String):
            return self.value <= len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value <= other.value.value, Boolean

    def ge(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'ge')
        if isinstance(other, (Integer, Float)):
            return self.value >= other.value, Boolean
        if isinstance(other, String):
            return self.value >= len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value >= other.value.value, Boolean


class Binary(BaseDatatype):

    def __init__(self, value):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
        mdc_assert(self, value, (str, int, float) + (
            Integer, Float, String, Boolean, Null),
            'bin', showname=False)
        if isinstance(value, str):
            try:
                self.value = int(value, 2)
            except ValueError:
                call_error('Value ' + pformat(value) + ' can not '
                    'be converted into Binary.', 'type')
        elif isinstance(value, int):
            self.value = [value, bin(value)] ##########################
        elif isinstance(value, float):
            self.value = round(value)
        elif isinstance(value, Integer):
            self.value = value.value
        elif isinstance(value, Float):
            self.value = round(value.value)
        elif isinstance(value, String):
            try:
                self.value = int(value.value, 2)
            except ValueError:
                call_error('String ' + pformat(value) + ' can not '
                    'be converted into Binary.', 'type')
        elif isinstance(value, Boolean):
            self.value = value.value.value
        elif isinstance(value, Null):
            self.value = 0
        super().__init__(self.value)

    def __repr__(self):
        return self.value + 'b'


class Float(BaseDatatype):

    def __init__(self, value):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
        mdc_assert(self, value, (int, float) + (
            Integer, Float, String, Boolean, Null),
            'float', showname=False)
        if isinstance(value, int):
            self.value = float(value)
        if isinstance(value, float):
            self.value = value
        elif isinstance(value, Integer):
            self.value = float(value.value)
        elif isinstance(value, Float):
            self.value = value.value
        elif isinstance(value, String):
            try:
                self.value = float(value.value)
            except ValueError:
                call_error('String ' + pformat(value) + ' can not '
                    'be converted into a Float.', 'type')
        elif isinstance(value, Boolean):
            self.value = float(value.value.value)
        elif isinstance(value, Null):
            self.value = 0.0
        super().__init__(self.value)

    def __repr__(self):
        return pformat(self.value)

    def __bool__(self):
        return bool(self.value)

    def call(self):
        return not self.value, Boolean

    def add(self, other):
        mdc_assert(self, other, (Integer, Float), 'add')
        return self.value + other.value, Float

    def sub(self, other):
        mdc_assert(self, other, (Integer, Float), 'sub')
        return self.value - other.value, Float

    def mult(self, other):
        mdc_assert(self, other, (Integer, Float, Boolean), 'sub')
        if isinstance(other, (Integer, Float)):
            return self.value * other.value, Float
        if isinstance(other, Boolean):
            return self.value * other.value.value, Integer

    def div(self, other):
        mdc_assert(self, other, (Integer, Float, Boolean), 'div')
        if isinstance(other, (Integer, Float)):
            return self.value / other.value, Float
        if isinstance(other, Boolean):
            return self.value * int(not other.value.value), Integer

    def pwr(self, other):
        mdc_assert(self, other, (Integer, Float, Boolean), 'pwr')
        if isinstance(other, (Integer, Float)):
            return self.value ** other.value, Float
        if isinstance(other, Boolean):
            return self.value ** other.value.value, Integer

    def eq(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'eq')
        if isinstance(other, (Integer, Float)):
            return self.value == other.value, Boolean
        if isinstance(other, String):
            return self.value == len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value == other.value.value, Boolean

    def lt(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'lt')
        if isinstance(other, (Integer, Float)):
            return self.value < other.value, Boolean
        if isinstance(other, String):
            return self.value < len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value < other.value.value, Boolean

    def gt(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'gt')
        if isinstance(other, (Integer, Float)):
            return self.value > other.value, Boolean
        if isinstance(other, String):
            return self.value > len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value > other.value.value, Boolean

    def le(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'le')
        if isinstance(other, (Integer, Float)):
            return self.value <= other.value, Boolean
        if isinstance(other, String):
            return self.value <= len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value <= other.value.value, Boolean

    def ge(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean), 'ge')
        if isinstance(other, (Integer, Float)):
            return self.value >= other.value, Boolean
        if isinstance(other, String):
            return self.value >= len(other.value), Boolean
        if isinstance(other, Boolean):
            return self.value >= other.value.value, Boolean


class String(BaseDatatype):

    def __init__(self, value):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
        mdc_assert(self, value, (str,) + datatypes,
            'string', showname=False)
        if isinstance(value, str):
            self.value = value
        elif isinstance(value, (Integer, Float, String, Null)):
            self.value = str(value.value)
        elif isinstance(value, RegexString):
            self.value = str(value.value.pattern)
        elif isinstance(value, Boolean):
            self.value = 'true' if value.value.value else 'false'
        elif isinstance(value, builtin_types):
            self.value = str(value.value)
        elif isinstance(value, datatypes):
            self.value = String(value.value).value
        data = {
            'capitalise': BuiltinFunction('capitalise',
                [],
                self._capitalise),
            'capitalize': BuiltinFunction('capitalize',
                [],
                self._capitalise),
            'count': BuiltinFunction('count',
                [['@']],
                self._count),
            'endswith': BuiltinFunction('endswith',
                [['@']],
                self._endswith),
            'join': BuiltinFunction('join',
                [['@']],
                self._join),
            'upper': BuiltinFunction('upper',
                [],
                self._upper),
            'lower': BuiltinFunction('lower',
                [],
                self._lower),
            'lstrip': BuiltinFunction('lstrip',
                [['@', '*']],
                self._lstrip),
            'replace': BuiltinFunction('replace',
                [['@', '*'], ['@', '*']],
                self._replace),
            'rstrip': BuiltinFunction('rstrip',
                [['@', '*']],
                self._rstrip),
            'split': BuiltinFunction('split',
                [['@', '*'], ['@', '*']],
                self._split),
            'strip': BuiltinFunction('strip',
                [['@', '*']],
                self._strip),
            'startswith': BuiltinFunction('startswith',
                [['@']],
                self._startswith),
        }
        super().__init__(self.value, start_data=data)

    def __repr__(self):
        return pformat(self.value)

    def __str__(self):
        return self.value

    def call(self):
        return not self.value, Boolean

    def foriter(self):
        return Array(tuple(String(a) for a in self.value))

    def add(self, other):
        mdc_assert(self, other, datatypes, 'add')
        if isinstance(other, (Integer, Float)):
            return self.value + str(other.value), String
        if isinstance(other, String):
            return self.value + other.value, String
        if isinstance(other, Array):
            return (self.value,) + other.value, Array
        return str(self.value) + str(other.value), String

    def sub(self, other):
        mdc_assert(self, other, (Integer, String), 'sub')
        if isinstance(other, Integer):
            return self.value[:-other.value], String
        if isinstance(other, String):
            return self.value.replace(other.value, '', 1), String

    def mult(self, other):
        mdc_assert(self, other, (Integer, Boolean), 'mult')
        if isinstance(other, Integer):
            return self.value * other.value, String
        if isinstance(other, Boolean):
            return self.value * other.value.value, String

    def div(self, other):
        mdc_assert(self, other, (String, Boolean), 'div')
        if isinstance(other, String):
            return self.value.count(other.value), Integer
        if isinstance(other, Boolean):
            return self.value if other.value.value else '', String

    def eq(self, other):
        mdc_assert(self, other, (
            Integer, Float, String, RegexString, Boolean, Null),
            'eq')
        if isinstance(other, Integer):
            return len(self.value) == other.value, Boolean
        if isinstance(other, Float):
            return len(self.value) == Integer(value).value, Boolean
        if isinstance(other, String):
            return self.value == other.value, Boolean
        if isinstance(other, RegexString):
            a = other.value.match(self.value)
            return bool(a) if a else 0, Boolean
        if isinstance(other, Boolean):
            return bool(self.value), Boolean
        if isinstance(other, Null):
            return not self.value, Boolean

    def index(self, other):
        mdc_assert(self, other, Integer, 'index')
        a = int(BFList.get_length((self,)).value)
        if int(other.value) > a - 1:
            call_error('String index out of range, ' + str(other) + ' > ' + str(a - 1) + '.',
                'outofrange')
        return self.value[other.value], String

    def has(self, other):
        mdc_assert(self, other, String, 'has')
        if isinstance(other, String):
            return other.value in self.value, Boolean

    # Begin built-in Object functions, prefix with _

    def _capitalise(self, args):
        return String(self.value.capitalize())

    def _count(self, args):
        mdc_assert(self, args[0], String, 'count')
        return Integer(self.value.count(args[0].value))

    def _endswith(self, args):
        mdc_assert(self, args[0], String, 'endswith')
        return Boolean(self.value.endswith(args[0].value))

    def _join(self, args):
        mdc_assert(self, args[0], Array, 'join')
        j = ''
        v = args[0].value
        for a in range(len(v)):
            if not isinstance(v[a], String):
                call_error('expected type String in index ' + str(a) + ' of iterable during joining.',
                    'type')
            j += v[a].value + self.value
        return String(j[:-len(self.value)])

    def _upper(self, args):
        return String(self.value.upper())

    def _lower(self, args):
        return String(self.value.lower())

    def _lstrip(self, args):
        mdc_assert(self, args[0], (Null, String), 'lstrip')
        if isinstance(args[0], Null):
            return String(self.value.lstrip())
        return String(self.value.lstrip(args[0].value))

    def _replace(self, args):
        mdc_assert(self, args[0], String, 'replace')
        mdc_assert(self, args[1], String, 'replace')
        return String(self.value.replace(args[0].value, args[1].value))

    def _rstrip(self, args):
        mdc_assert(self, args[0], (Null, String), 'rstrip')
        if isinstance(args[0], Null):
            return String(self.value.rstrip())
        return String(self.value.rstrip(args[0].value))

    def _split(self, args):
        mdc_assert(self, args[0], (Null, String), 'split')
        mdc_assert(self, args[1], (Null, Integer), 'split')
        return Array(self.value.split(
            None if isinstance(args[0], Null) else args[0].value,
            -1 if isinstance(args[1], Null) else args[1].value))

    def _strip(self, args):
        mdc_assert(self, args[0], (Null, String), 'strip')
        if isinstance(args[0], Null):
            return String(self.value.strip())
        return String(self.value.strip(args[0].value))

    def _startswith(self, args):
        mdc_assert(self, args[0], String, 'startswith')
        return Boolean(self.value.startswith(args[0].value))


class RegexString(BaseDatatype):

    def __init__(self, value):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
        mdc_assert(self, value, (str, re.Pattern, String), 'regex', showname=False)
        if isinstance(value, (str, re.Pattern)):
            self.value = re.compile(value)
        elif isinstance(value, String):
            self.value = re.compile(value.value)
        super().__init__(self.value)

    def __repr__(self):
        return 'x' + pformat(self.value.pattern)

    def call(self):
        return not self.value, Boolean

    def eq(self, other):
        mdc_assert(self, other, String, 'eq')
        a = self.value.match(other.value)
        return bool(a) if a else 0, Boolean


class Timedelta(BaseDatatype):

    def __init__(self, value):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
        mdc_assert(self, value, (datetime.timedelta, Timedelta, Date, Null), 'timedelta', showname=False)
        if isinstance(value, datetime.timedelta):
            self.value = value
        elif isinstance(value, Timedelta):
            self.value = value.value
        else:
            self.value = datetime.timedelta()
        super().__init__(self.value)

    def __repr__(self):
        return str(self.value)

    def call(self):
        return not self.value, Boolean

    def add(self, other):
        mdc_assert(self, other, (Date, Timedelta), 'add')
        return self.value + other.value, Timedelta

    def sub(self, other):
        mdc_assert(self, other, (Date, Timedelta), 'sub')
        return self.value - other.value, Timedelta

    def mult(self, other):
        mdc_assert(self, other, (Date, Timedelta), 'mult')
        return self.value * other.value, Timedelta

    def div(self, other):
        mdc_assert(self, other, (Date, Timedelta), 'div')
        return self.value / other.value, Float


class Date(BaseDatatype):

    def __init__(self, value):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
        mdc_assert(self, value, (datetime.datetime, Timedelta, Date, Null), 'date', showname=False)
        if isinstance(value, datetime.datetime):
            self.value = value
        elif isinstance(value, Timedelta):
            self.value = value.starttime
        elif isinstance(value, Date):
            self.value = value.value
        else:
            self.value = datetime.datetime.now()
        super().__init__(self.value)

    def __repr__(self):
        return str(self.value)

    def call(self):
        return not self.value, Boolean

    def add(self, other):
        mdc_assert(self, other, (Date, Timedelta), 'add')
        return self.value + other.value, Timedelta

    def sub(self, other):
        mdc_assert(self, other, (Date, Timedelta), 'sub')
        return self.value - other.value, Timedelta


class Slice(BaseDatatype):

    def __init__(self, value):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
        mdc_assert(self, value, (str, String, Slice), 'slice', showname=False)
        if isinstance(value, str):
            self.value = self.make_slice(value)
        elif isinstance(value, String):
            self.value = self.make_slice(value.value)
        elif isinstance(value, Slice):
            self.value = self.make_slice(value.display())
        super().__init__(self.value)

    def __repr__(self):
        return self.display()

    def display(self):
        if self.value[0] == self.value[1] and self.value[2] == 1:
            return '[' + pformat(self.value[0]) + ']'
        return '[' + ':'.join([pformat(a) for a in self.value]) + ']'

    def make_slice(self, value):
        value = value.strip('[]')
        if ':' in value:
            value = value.split(':')
        else:
            value = [value, value, False]
        if len(value) > 3:
            call_error('slice received too many arguments, maximum is 3.', 'argerr')
        if value == ['', '']:
            value = [False, False, True]
        while len(value) < 3:
            value += [False]
        if not value[0]:
            value[0] = '0'
        if not value[1]:
            value[1] = '-1'
        if not value[2]:
            value[2] = '1'
        for a in range(len(value), 0, -1):
            value.insert(a, ',')
        value = list(evaluate(value).value)
        is_multi = True
        try:
            value[0] = int(value[0].value)
        except ValueError:
            is_multi = False
        try:
            value[1] = int(value[1].value)
        except ValueError:
            if is_multi and value[1] != -1:
                call_error('Non-Integer value found in position 1 of slice.', 'value')
        try:
            if isinstance(value[2], Boolean) and value[2].value:
                value[2] = True
            else:
                value[2] = int(value[2].value)
        except ValueError:
            if is_multi:
                call_error('Non-Integer value found in position 2 of slice.', 'value')
        return value

    def do_slice(self, obj):
        if isinstance(obj, (String, Array)):
            start = len(obj.value) + self.value[0] if self.value[0] < 0 else self.value[0]
            stop = len(obj.value) + self.value[1] if self.value[1] < 0 else self.value[1]
            skip = self.value[2]
            if isinstance(skip, bool) and skip:
                newval = obj.value[:]
            elif start == stop and skip == 1:
                try:
                    newval = obj.value[start]
                except IndexError:
                    call_error('slice index ' + pformat(start) + ' not in object.', 'outofrange')
            elif start > 0 and stop < len(obj.value) and skip != 1:
                newval = obj.value[start:stop:skip]
            elif start > 0 and stop < len(obj.value):
                newval = obj.value[start:stop]
            elif start > 0 and skip != 1:
                newval = obj.value[start::skip]
            elif start > 0:
                newval = obj.value[start:]
            elif stop < len(obj.value):
                newval = obj.value[:stop]
            elif stop < len(obj.value) and skip != 1:
                newval = obj.value[:stop:skip]
            elif skip != 1:
                newval = obj.value[::skip]
            else:
                newval = obj.value[:]
            if isinstance(obj, String):
                return String(newval)
            if isinstance(obj, Array):
                return translate_datatypes(newval)
        if 'index' not in dir(obj):
            call_error('Datatype ' + type(obj).__name__ + ' does not have an index method to deal with slice.', 'attr')
        if isinstance(obj.index, (Function, BuiltinFunction)):
            return obj.index.call((obj, self,))
        return obj.index(self)


class Arglist(BaseDatatype):

    def __init__(self, value):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
        mdc_assert(self, value, (str, String, Arglist), 'arglist', showname=False)
        if isinstance(value, str):
            self.value = self.make_arglist(value)
        elif isinstance(value, String):
            self.value = self.make_arglist(value.value)
        elif isinstance(value, Arglist):
            self.value = value.value
        super().__init__(self.value)

    def __repr__(self):
        return self.display()

    def display(self):
        return '[' + ', '.join([' '.join(a) for a in self.value]) + (',' if len(self.value) == 1 else '') + ']'

    def make_arglist(self, value):
        value = value.strip('[]')
        newvalue = []
        optionals = False
        for a in value.split(','):
            if not a.strip():
                continue
            line = []
            a = a.strip()
            if a.endswith('*'):
                if a == '*':
                    call_error('Empty "*" found in Arglist: ' + pformat('(' + value + ')'), 'syntax')
                line += [a[:-1]]
                line += ['*']
                optionals = True
            elif '*' in a:
                call_error('Out of place "*" found in Arglist: ' + pformat('(' + value + ')'), 'syntax')
            elif optionals:
                call_error('Positional argument can not be placed after optional argument in Arglist: ' + pformat('(' + value + ')'),
                    'syntax')
            elif a:
                line += [a]
            if line:
                newvalue += [line]
        return newvalue


class Boolean(BaseDatatype):

    def __init__(self, value):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
        mdc_assert(self, value, (int, str, bool) + builtin_types, 'bool', showname=False)
        if isinstance(value, str):
            value = value.lower()
            if value == 'true':
                self.value = True
            elif value == 'false':
                self.value = False
            else:
                self.value = bool(value)
        elif isinstance(value, bool):
            self.value = value
        elif isinstance(value, builtin_types):
            self.value = bool(value.value)
        else:
            self.value = bool(value)
        super().__init__(self.value)

    def __repr__(self):
        return repr(self.value).lower()

    def __bool__(self):
        return bool(self.value)

    def call(self):
        return not self.value, Boolean


class Array(BaseDatatype):

    def __init__(self, value=None):
        mdc_assert(self, value, (type(None), tuple, list, CompactList) + builtin_types, 'array', showname=False)
        if isinstance(value, type(None)):
            self.value = ()
        if isinstance(value, (tuple, list)):
            self.value = tuple(value)
        elif isinstance(value, CompactList):
            self.value = value._value
        elif isinstance(value, String):
            self.value = tuple(String(a) for a in value.value)
        elif isinstance(value, Array):
            self.value = tuple(value.value)
        elif isinstance(value, Null):
            self.value = tuple()
        elif isinstance(value, builtin_types):
            self.value = (value,)
        data = {
            'index': BuiltinFunction('index',
                [['@']],
                self._index),
        }
        super().__init__(self.value, start_data=data)

    def __repr__(self):
        return '(' + ', '.join(pformat(a) for a in self.value) + ')'

    def __bool__(self):
        return bool(self.value)

    def call(self):
        return not self.value, Boolean

    def add(self, other):
        mdc_assert(self, other, builtin_types, 'add')
        return self.value + (other,), Array

    def sub(self, other):
        mdc_assert(self, other, (Integer, String), 'sub')
        if isinstance(other, Integer):
            return self.value[:-other.value], Array
        if isinstance(other, String):
            self.value = list(self.value)
            for a in range(len(self.value)):
                if self.value[a].value == other.value:
                    del self.value[a]
                    break
            self.value = tuple(self.value)
            return self.value, Array

    def mult(self, other):
        mdc_assert(self, other, Array, 'mult')
        return self.value + other.value, Array

    def index(self, other):
        mdc_assert(self, other, Integer, 'index')
        a = int(BFList.get_length((self,)).value)
        if int(other.value) > a - 1:
            call_error('Array index out of range, ' + str(other) + ' > ' + str(a - 1) + '.',
                'outofrange')
        return self.value[other.value], type(self.value[other.value])

    def has(self, other):
        mdc_assert(self, other, builtin_types, 'has')
        return any(a.value == other.value for a in self.value), Boolean

    # Begin built-in Object functions, prefix with _

    def _index(self, other):
        try:
            return self.value.index(other[0].value)
        except ValueError:
            return Integer(-1)


class Module(BaseDatatype):

    def __init__(self, name, data, is_file=True):
        self.value = os.path.abspath(name) if is_file else name
        self.data = data

    def __repr__(self):
        return '<Module ' + self.value + '>'

    def __str__(self):
        return '<Module( ' + ', '.join(str(a) + ': ' + pformat(self.data[a]) for a in self.data) + ' )>'

    def foriter(self):
        return Array(translate_datatypes(self.data.keys()))

    def index(self, slc):
        if slc.value[0].value not in self.data:
            call_error('key ' + pformat(slc.value[0].value) + ' does not exist.', 'key')
        return self.data[slc.value[0].value]


class Null(BaseDatatype):

    def __init__(self, *args):
        self.value = None
        super().__init__(self.value)

    def __repr__(self):
        return 'null'

    def __bool__(self):
        return False

    def call(self):
        return True, Boolean

    def add(self, other):
        return other.value, type(other)

    def sub(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean, Array, Null), 'sub')
        if isinstance(other, (Integer, Float)):
            return - other.value, type(other)
        if isinstance(other, String):
            return other.value[::-1], String
        if isinstance(other, Boolean):
            return not other.value.value, Boolean
        if isinstance(other, Array):
            return other.value[::-1], Array
        if isinstance(other, Null):
            return None, Null

    def mult(self, other):
        return None, Null

    def div(self, other):
        return None, Null

    def pwr(self, other):
        return None, Null

    def mod(self, other):
        return None, Null

    def eq(self, other):
        mdc_assert(self, other, builtin_types, 'eq')
        if isinstance(other, (Integer, Float, String, Array)):
            return not other.value, Boolean
        if isinstance(other, RegexString):
            return not str(other.value.pattern), Boolean
        if isinstance(other, Boolean):
            return not other.value.value, Boolean
        if isinstance(other, Null):
            return True, Boolean
        return not other.value, Boolean

    def lt(self, other):
        mdc_assert(self, other, builtin_types, 'lt')
        if isinstance(other, (Integer, Float)):
            return 0 < other.value, Boolean
        if isinstance(other, (String, Array)):
            return other.value, Boolean
        if isinstance(other, RegexString):
            return str(other.value.pattern), Boolean
        if isinstance(other, Boolean):
            return 0 < other.value.value, Boolean
        if isinstance(other, Null):
            return False, Boolean
        return bool(other.value), Boolean

    def gt(self, other):
        mdc_assert(self, other, builtin_types, 'gt')
        if isinstance(other, (Integer, Float)):
            return 0 > other.value, Boolean
        if isinstance(other, (String, Array)):
            return not value.value, Boolean
        if isinstance(other, RegexString):
            return not str(other.value.pattern), Boolean
        if isinstance(other, Boolean):
            return False, Boolean
        if isinstance(other, Null):
            return False, Boolean
        return not other.value, Boolean

    def le(self, other):
        mdc_assert(self, other, builtin_types, 'le')
        if isinstance(other, (Integer, Float)):
            return 0 <= other.value, Boolean
        return True, Boolean

    def ge(self, other):
        mdc_assert(self, other, builtin_types, 'ge')
        if isinstance(other, (Integer, Float)):
            return 0 >= other.value, Boolean
        if isinstance(other, (String, Array)):
            return not value.value, Boolean
        if isinstance(other, RegexString):
            return not str(other.value.pattern), Boolean
        if isinstance(other, Boolean):
            return 0 >= other.value.value, Boolean
        if isinstance(other, Null):
            return False, Boolean
        return not other.value, Boolean

    def index(self, other):
        return None, Null

    def has(self, other):
        return False, Boolean


class BreakToken(BaseDatatype):

    def __init__(self, *args):
        self.value = None
        super().__init__(self.value)

    def __repr__(self):
        return '\'break\''

    def __str__(self):
        return 'break'


class MDCLError(Exception):
    pass


class MDCLExit(Exception):
    pass


class Debug:

    @staticmethod
    def find_value(value):
        values = [a for a in local_vars if local_vars[a].value == value.value]
        if values:
            return values[0]
        else:
            return None

    @staticmethod
    def ts(lst):
        return [type(a) for a in lst]

    @staticmethod
    def s(lst):
        print(lst, Debug.ts(lst))


def call_function(func, args, func_self=True):
    global local_vars
    if isinstance(args, tuple):
        args = Array(args)
    else:
        args = Array((args,))
    thishas = dir(func)
    if 'call' not in thishas:
        call_error('type ' + type(func).__name__ + ' is not callable.', 'attr')
    if 'args' not in thishas or 'code' not in thishas:
        vals = func.call()
        settype = vals[1] if isinstance(vals, tuple) else type(vals)
        output = settype(vals[0] if isinstance(vals, tuple) else vals)
        return output
    f = args.value
    oldlocals = deepcopy(local_vars)
    if func_self:
        local_vars['self'] = func
    for i in range(len(func.args)):
        if not func.args[i]:
            continue
        if i >= len(f) and func.args[i][-1] == '*':
            f += Null(),
        elif i >= len(f):
            call_error('function ' + func.name + ' requires at least ' + str(len(func.args[i]))
                + ' positional argument' + ('' if len(func.args[i]) == 1 else 's') + '.', 'argerr')
        if '@' not in func.args[i]:
            local_vars[func.args[i][0]] = f[i]
    output = func.call(f)
    local_vars = deepcopy(oldlocals)
    return output


def as_tuple(value):
    if isinstance(value, Array):
        value = value.value
    elif not isinstance(value, tuple):
        value = value,
    return value


def do_action(first, action, second, error=None):
    try:
        vals = first.do_action(action, (second,))
        settype = vals[1] if isinstance(vals, tuple) else type(vals)
        return settype(vals[0] if isinstance(vals, tuple) else vals)
    except AttributeError:
        call_error('Type ' + type(first).__name__ + ' does not have a method for handling ' + action,
            'attr', error)


def initialise_path(src_path, local_path, compiled=False):
    if not os.path.isdir(src_path):
        call_error("The path: '" + str(src_path) + "' could not be found.", 'dirnotfound')
    if not os.path.isdir(local_path):
        call_error("The path: '" + str(local_path) + "' could not be found.", 'dirnotfound')
    # os.chdir(local_path) # Path no longer changes to source script path. Path stays as command execution path.
    global_vars['PATH'] = Array([
        String(local_path),
        String(os.path.abspath(src_path + '/builtins')),
        String(src_path),
    ])
    if compiled:
        return
    if not os.path.isfile(src_path + '/startup.mdcl'):
        call_error('Your installation of MDCL is missing a required library at path: "'
            + os.path.abspath(src_path + '/startup.mdcl') + '". Please re-install or repair '
            'your installation. Exports are currently located at: '
            'https://github.com/aidencuneo/MDCL-Interpreter/tree/master/dist', 'fatal')
    with open(src_path + '/startup.mdcl') as f:
        code = f.read()
    start(code)


def initialise_global_vars(file=None):
    global_vars['FILE'] = String(current_file if file is None else file)


def initialise_local_vars():
    global local_vars
    local_vars = CompactDict({
        'int': BuiltinFunction('int',
            [['@', '*']],
            Integer),
        'float': BuiltinFunction('float',
            [['@', '*']],
            Float),
        'string': BuiltinFunction('string',
            [['@', '*']],
            String),
        'regex': BuiltinFunction('regex',
            [[String, '*']],
            RegexString),
        'timedelta': BuiltinFunction('timedelta',
            [['@', '*']],
            Timedelta),
        'date': BuiltinFunction('date',
            [['@', '*']],
            Date),
        'slice': BuiltinFunction('slice',
            [['@', '*']],
            Slice),
        'bool': BuiltinFunction('bool',
            [['@', '*']],
            Boolean),

        'read': BuiltinFunction('read',
            [[String, '*']],
            BFList.read),
        'len': BuiltinFunction('len',
            [[String, Array]],
            BFList.get_length),
        'readfile': BuiltinFunction('readfile',
            [[String]],
            BFList.readfile),
        'writefile': BuiltinFunction('writefile',
            [[String], [String]],
            BFList.writefile),
        'type': BuiltinFunction('type',
            [['@']],
            BFList.get_type),
        'echo': BuiltinFunction('echo',
            [['@', '*']],
            BFList.echo),
        'write': BuiltinFunction('write',
            [['@', '*'], ['@', '*'], ['@', '*']],
            BFList.write),
        'wait': BuiltinFunction('wait',
            [[Integer, Float]],
            BFList.wait),
        'globals': BuiltinFunction('globals',
            [],
            BFList.get_globals),
        'locals': BuiltinFunction('locals',
            [],
            BFList.get_locals),
        'argv': BuiltinFunction('argv',
            [[Integer, '*']],
            BFList.get_argv),
        'getdata': BuiltinFunction('getdata',
            [['@']],
            BFList.get_data),
        'getkeys': BuiltinFunction('getkeys',
            [['@']],
            BFList.get_keys),
        'exec': BuiltinFunction('exec',
            [['@']],
            BFList._exec),
        'eval': BuiltinFunction('eval',
            [['@']],
            BFList._eval),
        'assign': BuiltinFunction('assign',
            [['@'], ['@']],
            BFList._assign),
        'pretty': BuiltinFunction('pretty',
            [['@']],
            lambda x: pformat(x[0].value)),

        'pyeval': BuiltinFunction('pyeval',
            [['@']],
            lambda x: eval(str(x[0].value), globals())),
        'pyexec': BuiltinFunction('pyexec',
            [['@']],
            lambda x: exec(str(x[0].value), globals())),
        'tokenise': BuiltinFunction('tokenise',
            [['@']],
            lambda x: tokenise(x[0].value)),
        'tokeniseFile': BuiltinFunction('tokeniseFile',
            [['@']],
            lambda x: tokenise_file(x[0].value)),

        'exit': BuiltinFunction('exit',
            [],
            lambda x: (
                String(''),
                doMDCLExit()
            )[0]),
    })


def call_error(text=None, error_type=None, line=None, args=None, showfile=True):
    original_error = error_type
    if isinstance(error_type, MDCLError):
        er = str(error_type)
        error_type = er[:er.index('::')]
        text = er[er.index('::') + 2:]
    e = 'ERROR'
    if error_type == 'fatal':
        if not text:
            print('A fatal error has occurred which has terminated the runtime environment.')
            print('PYTHON TRACEBACK:')
            exc = tb.format_exc()
            print(exc[exc.index(':') + 2:])
            print('Please consider posting this traceback as an issue on the GitHub Repository page at: '
                'https://github.com/aidencuneo/MDC-Lang')
            sys.exit()
        e = 'FATAL ERROR'
    elif error_type in error_tags:
        e = error_tags[error_type]
    if error_type in current_catch and not isinstance(original_error, MDCLError):
        raise MDCLError(error_type + '::' + (text if text is not None else ''))
    if e != 'fatal':
        print('\n-- Error Breadcrumbs --\n')
    for bci in range(len(breadcrumbs)):
        bc = breadcrumbs[bci]
        thisfile = os.path.abspath(bc[0])
        codesplit = bc[1].split('\n')
        lines = [
            codesplit[bc[3] - 1] if bc[3] - 1 < len(codesplit) else False,
            codesplit[bc[3]] if bc[3] < len(codesplit) else False,
            codesplit[bc[3] + 1] if bc[3] + 1 < len(codesplit) else False,
        ]
        codeline = codesplit[bc[3]] if bc[3] < len(codesplit) else ''
        if line in lines:
            line = lines.index(line)
            if line == 0:
                bc[3] -= 1
            elif line == 2:
                bc[3] += 1
            codeline = lines[line]
        print(('At file "' + thisfile + '", line ' + str(bc[3] + 1) + (
            ' (of surrounding code block)' if bc[4] else '')
            if showfile else ''))
        if bci == len(breadcrumbs) - 1:
            print('  ~~ ' + codeline.strip())
        elif isinstance(codeline, str):
            print('  -> ' + codeline.strip())
        print('')
    print('>> ' + e + ' (' + error_type + ')')
    if text and error_type != 'keyboardinterrupt':
        print('  :: ' + text)
    elif text is None and error_type != 'keyboardinterrupt':
        print('Your call_error call is missing the text argument. '
            'Ensure that you have a value other than None as the text argument '
            'for your call_error call.')
    sys.exit()


def perform_try_catch(e, error=None, args=None):
    er = str(e)
    er = er[:er.index('::')]
    if er in current_catch:
        global_vars['ERR'] = String(er)
        return evaluate((current_catch[er],), error=error, args=args)
    else:
        call_error(error_type=e)


def mdc_assert(first, second, types, action, showall=False, showname=True):
    if not isinstance(types, (list, tuple)):
        types = types,
    if not isinstance(second, types):
        typestr = '(' + ', '.join([a.__name__ for a in types if showall or (not showall and a in builtin_types)]) + ')'
        s = type(first).__name__ + ' o' if showname else 'O'
        s += 'perand type for ' + action + ' '
        if not showall:
            types = tuple(a for a in types if a in datatypes)
        if types == builtin_types == datatypes:
            s += 'must be a builtin type or currently imported MDCL Datatype'
        elif types == builtin_types:
            s += 'must be a builtin type'
        elif types == datatypes:
            s += 'must be a currently imported MDCL Datatype'
        else:
            s += 'must fit into: ' + typestr
        call_error(s + '. "' + type(second).__name__ + '" is invalid.',
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


def import_module(fname):
    global current_file
    global current_code
    global current_line
    global local_vars
    newcode = get_code(fname)
    if isinstance(newcode, Exception):
        return
    oldfile = current_file
    oldcode = current_code
    oldline = current_line
    oldlocals = deepcopy(local_vars)
    initialise_local_vars()
    run(newcode, fname, raw=True)
    current_file = oldfile
    current_code = oldcode
    current_line = oldline
    module = Module(fname, deepcopy(local_vars))
    local_vars = oldlocals
    return module


def start(rawcode, filename=None, exit_on_exc=True):
    global breadcrumbs
    try:
        breadcrumbs = []
        run(rawcode, filename, raw=True)
    except MDCLError as e:
        call_error(error_type=e)
    except MDCLExit:
        if exit_on_exc:
            sys.exit()
        raise MDCLExit()
    except (KeyboardInterrupt, EOFError):
        sig_c.send('SIGINT')
    except RecursionError:
        call_error('Too many recursive calls.', 'recursion')
    except ZeroDivisionError:
        call_error('Attemped division or modulo by zero.', 'zerodivision')
    except Exception as e:
        call_error(error_type='fatal')


def run(rawcode, filename=None, tokenised=False, oneline=False, echo=True, raw=False,
    yielding=False, localargs=None, independent=False, has_breadcrumbs=True):
    global breadcrumbs
    global current_file
    global current_code
    global current_line
    global current_catch
    global break_token
    global previous_condition
    global local_vars
    global datatypes
    code = rawcode
    if not current_file:
        initialise_global_vars(file=filename)
    if filename != 'keep':
        current_file = '<EVAL>' if filename is None else filename
        if not independent:
            current_code = current_code if filename is None else code
            current_line = 1
    if independent:
        filename = ''
        line = 1
    if raw:
        code = process(code)
    if oneline:
        code = [code]
    lines = tokenise_file(rawcode, dofilter=False)
    if has_breadcrumbs:
        breadcrumbs += [[
            current_file,
            rawcode, 
            0,
            line if independent else current_line,
            independent,
        ]]
    o = ''
    yielded = []
    i = 0
    while i < len(code):
        if not code[i].strip():
            i += 1
            continue
        if tokenised:
            a = code[i]
        else:
            a = tokenise(code[i])
        if not a:
            i += 1
            continue
        elif a[0] == 'new':
            if len(a) < 4 or ':' not in a:
                call_error('Datatype declaration requires at least a datatype name, initialisation code, and the ":" separator.', 'argerr')
            name = a[1]
            func = a[-1]
            arguments = tuple(filter(None, split_list(a[2:-1], ':')))
            types = [b.__name__ for b in builtin_types]
            optionals = False
            for b in arguments:
                for c in b:
                    if c not in types and not c == '*':
                        call_error(pformat(c) + ' is not defined as a type.', 'attr')
                if '*' in b:
                    optionals = True
                elif optionals and not '*' in b:
                    call_error('Optional function arguments for init must be after all positional arguments.', 'syntax')
            if name in globals() or name in locals() or name in builtin_types:
                call_error('Invalid Datatype name. Datatype name must not already be defined.', 'defined')
            exec('class ' + name + '(BaseDatatype):pass', globals())
            this = eval(name)
            actions = {b[1:] : local_vars[b] for b in local_vars
                if isinstance(local_vars[b], (Function, BuiltinFunction))
                and b[0] == '!'
                and b[1:] in mdcl_keywords + ('echo',)
            }
            if 'echo' not in actions:
                call_error('Datatype is missing an echo function.', 'attr')
            for a in actions:
                setattr(this, a, actions[a])
            def __init__(self, args):
                if not isinstance(args, (list, tuple)):
                    args = args,
                self.value = evaluate([func], args=args)
                self.data = CompactDict({} if self.value is None else {
                    'value': self.value,
                })
            def __repr__(self):
                try:
                    return pformat(actions['echo'].call(self))
                except RecursionError:
                    raise e
            this.__init__ = __init__
            this.__repr__ = __repr__
            datatypes += (this,)
            local_vars[name] = Function(name, arguments, this)
            del this
            del __init__
            del __repr__
        elif a[0] == 'if':
            if len(a) < 2:
                call_error('if statement requires at least a condition and code to run.', 'syntax')
            if not a[1]:
                call_error('if statement requires at least a condition and code to run.', 'syntax')
            if bool(evaluate(a[1:-1], error=code[i], args=localargs)):
                ev = evaluate((a[-1],), error=code[i], args=localargs, has_breadcrumbs=False)
                if isinstance(ev, BreakToken):
                    return ev
                if not isinstance(ev, Null):
                    if yielding:
                        yielded += [ev]
                    else:
                        o += str(ev)
                        if echo:
                            sys.stdout.write(str(ev))
                previous_condition = True
            else:
                previous_condition = False
        elif a[0] == 'elif':
            if len(a) < 2:
                call_error('elif statement requires at least a condition and code to run.', 'syntax')
            if not a[1]:
                call_error('elif statement requires at least a condition and code to run.', 'syntax')
            if not previous_condition and bool(evaluate(a[1:-1], error=code[i], args=localargs)):
                ev = evaluate((a[-1],), error=code[i], args=localargs, has_breadcrumbs=False)
                if isinstance(ev, BreakToken):
                    return ev
                if not isinstance(ev, Null):
                    if yielding:
                        yielded += [ev]
                    else:
                        o += str(ev)
                        if echo:
                            sys.stdout.write(str(ev))
                previous_condition = True
            else:
                previous_condition = False
        elif a[0] == 'else':
            if len(a) < 2:
                call_error('else statement requires code to run.', 'syntax')
            if not a[1]:
                call_error('else statement requires code to run.', 'syntax')
            if not previous_condition:
                ev = evaluate((a[1],), error=code[i], args=localargs, has_breadcrumbs=False)
                if isinstance(ev, BreakToken):
                    return ev
                if not isinstance(ev, Null):
                    if yielding:
                        yielded += [ev]
                    else:
                        o += str(ev)
                        if echo:
                            sys.stdout.write(str(ev))
            previous_condition = True
        elif a[0] == 'while':
            if len(a) < 2:
                call_error('while loop requires at least code to run. (condition not required)', 'syntax')
            if not (a[-1].startswith('{') and a[-1].endswith('}')):
                call_error('while loop requires at least code to run. (condition not required)', 'syntax')
            condition = True if len(a) < 3 else a[1:-1]
            if not condition:
                call_error('invalid syntax for while loop condition.', 'syntax')
            while bool(evaluate(condition, error=code[i], args=localargs)):
                break_token = True
                ev = evaluate((a[-1],), error=code[i], args=localargs, has_breadcrumbs=False)
                if isinstance(ev, BreakToken):
                    break_token = False
                    break
                if not isinstance(ev, Null):
                    if yielding:
                        yielded += [ev]
                    else:
                        o += str(ev)
                        if echo:
                            sys.stdout.write(str(ev))
        elif a[0] == 'for':
            if len(a) < 3:
                call_error('for loop requires at least an iterable and code to run. (var name optional)', 'syntax')
            if not (a[-1].startswith('{') and a[-1].endswith('}')):
                call_error('for loop is missing a valid code block.', 'syntax')
            if ':' in a[1:-1]:
                variable = a[a.index(':') - 1]
                iterable = evaluate(a[a.index(':') + 1:-1], error=code[i], args=localargs)
            else:
                variable = None
                iterable = evaluate(a[1:-1], error=code[i], args=localargs)
            runcode = a[-1]
            if variable in global_vars and variable != ',':
                call_error('name ' + pformat(variable) + ' is already defined in the global variables list.', 'var')
            if variable in reserved_names and variable != ',':
                call_error('for loop var names can not be reserved names.', 'var')
            if not runcode:
                call_error('for loop code to run can not be empty.', 'syntax')
            if not isinstance(iterable, Array):
                if 'foriter' not in dir(iterable):
                    call_error('type ' + type(iterable).__name__ + ' is not iterable.', 'type')
                iterable = iterable.foriter()
            if isinstance(iterable, Array):
                iterable = iterable.value
            if not isinstance(iterable, tuple):
                call_error('type ' + type(iterable).__name__ + ' foriter function does not return an iterable.', 'type')
            oldvariable = None
            if variable in local_vars:
                oldvariable = local_vars[variable]
            for val in iterable:
                if variable is not None:
                    local_vars[variable] = val
                local_vars['#'] = val
                break_token = True
                ev = evaluate((runcode,), error=code[i], args=localargs, has_breadcrumbs=False)
                if isinstance(ev, BreakToken):
                    break_token = False
                    break
                if not isinstance(ev, Null):
                    if yielding:
                        yielded += [ev]
                    else:
                        o += str(ev)
                        if echo:
                            sys.stdout.write(str(ev))
            if oldvariable is not None:
                local_vars[variable] = oldvariable
        elif a[0] == 'try':
            if len(a) < 3:
                call_error('try statement requires at least code to run.', 'syntax')
            contents = split_list(a[1:], lambda x: x.startswith('{') and x.endswith('}'), astype=tuple)
            runcode = contents[0]
            if not runcode:
                call_error('try statement code to run can not be empty.', 'syntax')
            catches = {}
            keys = []
            for b in contents[1:]:
                if not (b[-1].startswith('{') and b[-1].endswith('}')):
                    call_error('try statement is missing a valid code block.', 'syntax')
                if b[0] == 'catch':
                    keys = b[1:-1]
                    if not keys:
                        call_error('catch statement missing errortags to catch.', 'syntax')
                    keys = evaluate(keys, error=code[i], args=localargs)
                    if isinstance(keys, Array):
                        keys = keys.value
                    if not isinstance(keys, (tuple, list)):
                        keys = keys,
                    for c in keys:
                        if not isinstance(c, String):
                            call_error('errortags to catch must be String.', 'type')
                        catches[c.value] = b[-1]
                    keys = []
                elif 'catch' in b:
                    call_error('catch keyword out of place.', 'syntax')
            if keys:
                call_error('unfinished catch keyword in try statement.', 'syntax')
            oldcatch = current_catch
            current_catch = catches
            try:
                ev = evaluate(runcode, error=code[i], args=localargs)
                if isinstance(ev, BreakToken):
                    return ev
                if not isinstance(ev, Null):
                    if yielding:
                        yielded += [ev]
                    else:
                        o += str(ev)
                        if echo:
                            sys.stdout.write(str(ev))
            except MDCLError as e:
                ev = perform_try_catch(e, error=code[i], args=localargs)
                if isinstance(ev, BreakToken):
                    return ev
                if not isinstance(ev, Null):
                    if yielding:
                        yielded += [ev]
                    else:
                        o += str(ev)
                        if echo:
                            sys.stdout.write(str(ev))
            except MDCLExit:
                raise MDCLExit()
            except (KeyboardInterrupt, EOFError):
                if sig_c.switches['INT']:
                    ev = perform_try_catch(MDCLError('keyboardinterrupt::'), error=code[i], args=localargs)
                    if isinstance(ev, BreakToken):
                        return ev
                    if not isinstance(ev, Null):
                        if yielding:
                            yielded += [ev]
                        else:
                            o += str(ev)
                            if echo:
                                sys.stdout.write(str(ev))
            except RecursionError:
                ev = perform_try_catch(MDCLError('recursion::Too many recursive calls in a row.'), error=code[i], args=localargs)
                if isinstance(ev, BreakToken):
                    return ev
                if not isinstance(ev, Null):
                    if yielding:
                        yielded += [ev]
                    else:
                        o += str(ev)
                        if echo:
                            sys.stdout.write(str(ev))
            except ZeroDivisionError:
                ev = perform_try_catch(MDCLError('zerodivision::Attemped division or modulo by zero.'), error=code[i], args=localargs)
                if isinstance(ev, BreakToken):
                    return ev
                if not isinstance(ev, Null):
                    if yielding:
                        yielded += [ev]
                    else:
                        o += str(ev)
                        if echo:
                            sys.stdout.write(str(ev))
            except Exception as e:
                call_error(error_type='fatal')
            current_catch = oldcatch
        elif ':' in a or '+:' in a or '-:' in a or '*:' in a or '/:' in a:
            if ':' in a:
                oper = ':'
            elif '+:' in a:
                oper = '+:'
            elif '-:' in a:
                oper = '-:'
            elif '*:' in a:
                oper = '*:'
            elif '/:' in a:
                oper = '/:'
            key = [''.join(z) for z in split_list(a[:a.index(oper)], '.')]
            k = 0
            while k < len(key):
                if k + 1 < len(key):
                    if key[k + 1] in reserved_names and len(key) < 2:
                        call_error('invalid variable name, variable names can not be reserved names.', 'var')
                    if not re.match('^[a-zA-Z]+$', key[k + 1]) and key[k + 1]:
                        call_error('invalid variable name, variable names must fit this regex expression: ^[a-zA-Z]+$', 'var')
                if k < len(key) - 2:
                    if not key[k]:
                        call_error('can not set attribute with a null parent (missing value before `.`)', 'argerr')
                    if k + 1 >= len(key):
                        call_error('missing attribute to set inside parent "' + key[k - 1] + '".', 'argerr')
                    old = key[k]
                    key[k] = evaluate([key[k]], error=code[i], args=localargs)
                    try:
                        key[k] = key[k].data[key[k + 1]]
                    except KeyError as e:
                        call_error(type(old).__name__ + ' ' + pformat(old) + ' does not have attribute ' + pformat(key[k + 1]) + '.',
                            'attr')
                    del key[k + 1]
                    k -= 1
                k += 1
            value = evaluate(a[a.index(oper) + 1:], args=localargs, error=code[i])
            if isinstance(value, tuple):
                if not value:
                    value = Null()
                elif value:
                    value = translate_datatypes(value[0])
            if key[2:]:
                call_error('invalid settatr syntax.', 'syntax')
            elif not key:
                key = ['']
            if key[1:]:
                if oper != ':' and key[0] not in local_vars:
                    call_error('undefined token: ' + pformat(key[0]), 'syntax', code[i])
                if oper != ':' and key[1] not in local_vars[key[0]].data:
                    call_error(type(key[0]).__name__ + ' ' + pformat(key[0]) + ' does not have attribute ' + pformat(key[1]) + '.',
                        'attr')
                if key[1] == 'value':
                    call_error('Attribute "value" of type "' + type(local_vars[key[0]]).__name__ + '" is a readonly value.',
                        'readonly')
                if isinstance(value, (Function, BuiltinFunction)):
                    value.data['name'] = key[1]
                    value.name = key[1]
                if oper == '+:':
                    value = do_action(local_vars[key[0]].data[key[1]], 'add', value, error=code[i])
                elif oper == '-:':
                    value = do_action(local_vars[key[0]].data[key[1]], 'sub', value, error=code[i])
                elif oper == '*:':
                    value = do_action(local_vars[key[0]].data[key[1]], 'mult', value, error=code[i])
                elif oper == '/:':
                    value = do_action(local_vars[key[0]].data[key[1]], 'div', value, error=code[i])
                if isinstance(key[0], str):
                    local_vars[key[0]].data[key[1]] = value
                else:
                    key[0].data[key[1]] = value
            elif key:
                if oper != ':' and key[0] not in local_vars:
                    call_error('Undefined Token: ' + pformat(key[0]), 'syntax', code[i])
                if isinstance(value, (Function, BuiltinFunction)):
                    value.data['name'] = key[0]
                    value.name = key[0]
                if oper == '+:':
                    value = do_action(local_vars[key[0]], 'add', value, error=code[i])
                elif oper == '-:':
                    value = do_action(local_vars[key[0]], 'sub', value, error=code[i])
                elif oper == '*:':
                    value = do_action(local_vars[key[0]], 'mult', value, error=code[i])
                elif oper == '/:':
                    value = do_action(local_vars[key[0]], 'div', value, error=code[i])
                if key[0]:
                    local_vars[key[0]] = value
        elif a[0] == 'del':
            if len(a) < 2:
                call_error('del statement missing variable or key to delete.', 'argerr')
            key = ''.join(a[1:])
            if key in local_vars:
                if isinstance(local_vars[key], BuiltinFunction):
                    call_error('del statement can not delete built-in functions.', 'argerr')
                del local_vars[key]
            elif key in global_vars:
                call_error('del statement can not delete global arguments.', 'argerr')
        elif a[0] == 'import':
            if len(a) < 2:
                call_error('import requires at least one argument.', 'argerr')
            fnames = as_tuple(evaluate(a[1:], error=code[i], args=localargs))
            if any(not isinstance(f, String) for f in fnames):
                call_error('import arguments must be of type String.', 'type')
            for fname in fnames:
                for b in global_vars['PATH'].value:
                    f = String(str(b.value) + '/' + str(fname.value)).value
                    if not f.endswith('.mdcl'):
                        f += '.mdcl'
                    newmodule = import_module(f)
                    if newmodule is None:
                        continue
                    local_vars[fname.value] = newmodule
                    break
                else:
                    call_error('import could not find module ' + pformat(fname) + ' in PATH.', 'import')
        elif a[0] == 'sig':
            if len(a) < 2:
                call_error('sig requires at least a signal name.', 'argerr')
            if len(a) > 2:
                a = evaluate_line(a, start=2, error=code[i], args=localargs)
            signal_name = a[1].strip()
            if signal_name not in sig_c.switches:
                call_error('signal ' + pformat(signal_name) + ' is not a valid signal.', 'unknownvalue')
            newvalue = not sig_c.switches[signal_name]
            if len(a) > 2:
                newvalue = Boolean(a[2]).value
            if not isinstance(newvalue, bool):
                call_error('sig new value must evaluate to Boolean.', 'type')
            sig_c.switches[signal_name] = newvalue
        elif a[0] == 'raise':
            a = evaluate_line(a, start=1, error=code[i], args=localargs)
            errortag = String('')
            errortext = String('')
            if len(a) > 1:
                errortag = a[1]
            if len(a) > 2:
                errortext = a[2]
            if not isinstance(errortag, String):
                call_error('error type to raise must be of type String.', 'type')
            if not isinstance(errortext, String):
                call_error('error text must be of type String', 'type')
            ev = perform_try_catch(MDCLError(errortag.value + '::' + errortext.value), error=code[i], args=localargs)
            if isinstance(ev, BreakToken):
                return ev
            if not isinstance(ev, Null):
                if yielding:
                    yielded += [ev]
                else:
                    o += str(ev)
                    if echo:
                        sys.stdout.write(str(ev))
        elif a[0] == 'errortag':
            a = evaluate_line(a, start=1, error=code[i], args=localargs)
            if len(a) < 2:
                call_error('errortag requires at least an error type name.', 'argerr')
            errortype = a[1]
            errortag = String('')
            if len(a) > 2:
                errortag = a[2]
            if not isinstance(errortype, String):
                call_error('error type to set tag for must be of type String.', 'type')
            if not isinstance(errortag, String):
                call_error('error tag must be of type String.', 'type')
            if errortype.value in error_tags and errortag.value:
                call_error('an error tag with that name already exists.', 'type')
            if errortype.value in start_error_tags:
                call_error('built-in errortags are readonly.', 'readonly')
            if errortag.value:
                error_tags[errortype.value] = errortag.value
            else:
                del error_tags[errortype.value]
        elif a[0] == 'yield':
            if not yielding:
                call_error('value returning is not possible from the current scope.', 'syntax')
            yielded += [evaluate(a[1:], error=code[i], args=localargs)]
        elif a[0] == 'ret':
            if not yielding:
                call_error('value returning is not possible from the current scope.', 'syntax')
            yielded += [evaluate(a[1:], error=code[i], args=localargs)]
            break
        else:
            a = evaluate(a, error=code[i], args=localargs)
            if isinstance(a, BreakToken):
                return a
            if sig_c.switches['ECHO'] and isinstance(a, builtin_types):
                o += str(a)
                if echo:
                    sys.stdout.write(str(a))
        if independent:
            line += lines[i].count('\n')
        else:
            current_line += lines[i].count('\n')
        if has_breadcrumbs:
            breadcrumbs[-1][3] = line if independent else current_line
            breadcrumbs[-1][2] = i
        i += 1
    if has_breadcrumbs:
        breadcrumbs = breadcrumbs[:-1]
    if yielding:
        return yielded
    return o


def translate_datatypes(dt, dotuple=True, error_on_fail=True):
    if isinstance(dt, tuple([a for a in datatypes_switch.keys() if dotuple or a != tuple])):
        dt = datatypes_switch[type(dt)](dt)
    if isinstance(dt, types.FunctionType):
        args = [['@'] for a in dt.__defaults__] if dt.__defaults__ else []
        args += [['@', '*'] for a in dt.__kwdefaults__] if dt.__kwdefaults__ else []
        dt = Function(dt.__name__, args, dt)
    if isinstance(dt, types.BuiltinFunctionType):
        dt = Function(dt.__name__, [], dt)
    if isinstance(dt, Array):
        contents = tuple(translate_datatypes(a) for a in dt.value)
        dt = Array(contents)
    if isinstance(dt, datatypes + (Function,)):
        return dt
    if not (isinstance(dt, tuple) and not dotuple) and error_on_fail:
        call_error('There was an error during datatype translation for value: ' + pformat(dt) + '.', 'value')
    return dt


def pre_evaluate(exp, error=None, dostrings=False):
    if not exp:
        return exp
    new = [a for a in exp]
    a = 0
    while a < len(new):
        if isinstance(new[a], datatypes):
            a += 1
            continue
        if isinstance(new[a], tuple([b for b in datatypes_switch.keys() if dostrings or b != str])):
            new[a] = datatypes_switch[type(new[a])](new[a])
        if not isinstance(new[a], str):
            pass
        ### '.' CHECK USED TO GO HERE
        elif re.match('^x(\'|").*(\'|")', new[a]): # Is new[a] a Regex String? If so, assign Regex() class.
            try:
                new[a] = RegexString(ast.literal_eval(new[a][1:]))
            except Exception:
                call_error('Invalid Regex String.', 'syntax', error)
        elif re.match("^'.*'$", convert_escapes(new[a])): # Is new[a] a string with single quotes? If so, assign String() class using RAW value.
            new[a] = String(new[a][1:-1])
        elif re.match('^".*"$', convert_escapes(new[a])): # Is new[a] a string with double quotes? If so, assign evaluated String() class.
            try:
                #print(new[a])
                new[a] = String(ast.literal_eval(convert_escapes(new[a])))
            except Exception:
                call_error('Invalid String.', 'syntax', error)
        elif re.match('^(-|\+)*[0-9]*\.[0-9]+$', new[a]): # Is new[a] a float? If so, assign Float() class.
            new[a] = Float(float(new[a]))
        elif re.match('^(-|\+)*[0-9]+$', new[a]): # Is new[a] an integer? If so, assign Integer() class.
            new[a] = Integer(int(new[a]))
        elif new[a] in ('true', 'false'): # Is new[a] a boolean? If so, assign Boolean() class.
            new[a] = Boolean(new[a])
        elif new[a] == 'null': # Is new[a] null? If so, assign Null() class.
            new[a] = Null()
        a += 1
    return new


def evaluate_line(oldline, start, end=None, error=None, args=None):
    if end is None:
        end = len(oldline)
    new_line = evaluate(oldline[start:end], error=error, args=args)
    if isinstance(new_line, Array):
        oldline[start:end] = new_line.value
    else:
        oldline[start] = new_line
    return oldline


def evaluate(exp, error=None, args=None, funcargs=False, has_breadcrumbs=True, func_self=True, translate=True):
    global current_file
    global current_code
    global current_line
    global break_token
    global local_vars
    if not exp:
        return ()
    reps = {
        '+': 'add',
        '-': 'sub',
        '*': 'mult',
        '/': 'div',
        '^': 'pwr',
        '%': 'mod',
        '=': 'eq',
        '>': 'gt',
        '<': 'lt',
        '>=': 'ge',
        '<=': 'le',
    }
    new = exp[:]
    new = pre_evaluate(new, error=error)
    array_cont = []
    a = 0
    while a < len(new):
        if isinstance(new[a], datatypes + (type(None),)) and not (
            isinstance(new[a], Slice)
        ):
            a += 1
            continue
        if new[a] in reps:
            new[a] = reps[new[a]]
        if new[a] in mdcl_keywords:
            if a - 1 < 0:
                call_error('missing first argument for ' + new[a] + ' method.', 'syntax', error)
            if a + 1 >= len(new):
                call_error('missing second argument for ' + new[a] + ' method.', 'syntax', error)
            try:
                vals = new[a - 1].do_action(new[a], (evaluate([new[a + 1]], error=error, args=args),))
                settype = vals[1] if isinstance(vals, tuple) else type(vals)
                new[a] = settype(vals[0] if isinstance(vals, tuple) else vals)
                del new[a + 1]
                del new[a - 1]
                a -= 1
            except AttributeError:
                call_error('type ' + type(new[a - 1]).__name__ + ' does not have a method for handling ' + new[a],
                    'attr', error)
        elif isinstance(new[a], Slice):
            if a - 1 >= 0:
                vals = new[a].do_slice(new[a - 1])
                settype = vals[1] if isinstance(vals, tuple) else type(vals)
                new[a] = settype(vals[0] if isinstance(vals, tuple) else vals)
                del new[a - 1]
                a -= 1
        elif new[a] == '.':
            if a - 1 < 0:
                call_error('Can not get attribute from null. (Missing value before ".")', 'argerr', error)
            if a + 1 >= len(new):
                call_error('Missing argument to retrieve from "' + new[a - 1] + '".', 'argerr', error)
            new[a - 1] = evaluate([new[a - 1]], error=error)
            try:
                old = new[a - 1]
                new[a - 1] = new[a - 1].data[new[a + 1]]
            except KeyError:
                call_error(type(old).__name__ + ' ' + pformat(exp[a - 1]) + ' does not have attribute ' + pformat(new[a + 1]) + '.',
                    'attr', error)
            del new[a]
            del new[a]
            a -= 1
        elif new[a] == '!':
            if a + 1 >= len(new):
                call_error('missing second argument for ! (boolean not) operator.', 'syntax', error)
            del new[a]
            new[a:] = evaluate(new[a:], error=error, args=args),
            if 'boolnot' in dir(new[a]):
                vals = new[a].boolnot()
                settype = vals[1] if isinstance(vals, tuple) else type(vals)
                new[a] = settype(vals[0] if isinstance(vals, tuple) else vals)
            else:
                new[a] = Boolean(not new[a].value)
            a -= 1
        elif new[a].startswith('args[') and new[a].endswith(']'):
            key = int(new[a][5:-1])
            if args:
                if key >= len(args):
                    new[a] = Null()
                new[a] = args[key]
            else:
                if key >= len(global_args):
                    new[a] = Null()
                new[a] = global_args[key]
        elif new[a] == '=>':
            if a - 1 < 0:
                call_error('inline function declaration requires a left hand argument.', 'argerr', error)
            if a + 1 >= len(new):
                call_error('inline function declaration requires a right hand argument.', 'argerr', error)
            if not isinstance(new[a - 1], Arglist):
                call_error('inline function declaration requires Arglist as left hand argument.', 'type', error)
            if not (new[a + 1].startswith('{') and new[a + 1].endswith('}')):
                call_error('inline function declaration requires a code block as right hand argument.', 'type', error)
            func = new[a + 1]
            arguments = new[a - 1].value
            new[a] = Function('<InlineFunction>', arguments, func)
            del new[a + 1]
            del new[a - 1]
            a += 1
        elif new[a] == ',':
            if a - 1 < 0:
                if not array_cont:
                    call_error('syntax error, missing value before comma.', 'syntax', error)
                array_cont = [array_cont]
                del new[a]
                a -= 1
            else:
                array_cont += [new[a - 1]]
                del new[a - 1]
                del new[a - 1]
                a -= 2
        elif new[a] == '?':
            if a - 1 < 0:
                call_error('shorthand if statement requires a condition.', 'argerr', error)
            if a + 1 >= len(new):
                call_error('shorthand if statement requires right hand values.', 'argerr', error)
            condition = evaluate((new[a - 1],), error=error, args=args)
            if '\\' in new[a + 1:]:
                sep = new.index('\\', a + 1)
                first = new[a + 1:sep]
                second = new[sep + 1:]
            else:
                first = new[a + 1:]
                second = Null(),
            del new[a:]
            a = 0
            new[a] = (
                evaluate(first, args=args, error=error)
                if Boolean(condition) else
                evaluate(second, args=args, error=error)
            )
        elif new[a] == 'and':
            if a - 1 < 0:
                call_error('and requires a left hand argument.', 'argerr', error)
            if a + 1 >= len(new):
                call_error('and requires a right hand argument.', 'argerr', error)
            left = evaluate((new[a - 1],), args=args, error=error)
            right = evaluate((new[a + 1],), args=args, error=error)
            new[a] = Boolean(Boolean(left) and Boolean(right))
            del new[a + 1]
            del new[a - 1]
            a -= 1
        elif new[a] == 'or':
            if a - 1 < 0:
                call_error('or requires a left hand argument.', 'argerr', error)
            if a + 1 >= len(new):
                call_error('or requires a right hand argument.', 'argerr', error)
            left = evaluate([new[a - 1]], args=args, error=error)
            right = evaluate_line(new, start=a + 1, error=error, args=args)[a + 1] # TAKE A LOOK AT THIS #############################################################################
            new[a] = Boolean(Boolean(left) or Boolean(right))
            del new[a + 1]
            del new[a - 1]
            a -= 1
        elif new[a] == 'only':
            if a - 1 < 0:
                call_error('only requires a left hand argument.', 'argerr', error)
            if a + 1 >= len(new):
                call_error('only requires a right hand argument.', 'argerr', error)
            argument = evaluate((new[a - 1],), args=args, error=error)
            if not isinstance(argument, (Integer, String, Array)):
                call_error('only can only iterate over an Array, Integer, or String.', 'type')
            if isinstance(argument, Integer):
                argument = range(argument.value)
            else:
                argument = argument.value
            runcode = new[a + 1].strip()[1:-1].strip()
            output = []
            for value in argument:
                value = run(runcode, filename='keep', echo=False, raw=True, yielding=True, localargs=[value], has_breadcrumbs=has_breadcrumbs)
                newvalue = value
                if not value:
                    newvalue = []
                elif len(value) == 1:
                    newvalue = [value[0]]
                    if isinstance(value[0], Null):
                        newvalue = []
                output += newvalue
            new[a] = Array(output)
            del new[a + 1]
            del new[a - 1]
            a -= 1
        elif new[a] == 'to':
            if a + 1 >= len(new):
                call_error('to requires a right hand argument.', 'argerr', error)
            left = evaluate((new[a - 1],), args=args, error=error) if a > 0 else Integer(0)
            right = evaluate((new[a + 1],), args=args, error=error)
            if not isinstance(left, Integer):
                call_error('to requires an Integer as left hand argument.', 'type', error)
            if not isinstance(right, Integer):
                call_error('to requires an Integer as right hand argument.', 'type', error)
            step = 1
            if right.value < left.value:
                step = -1
                right.value -= 1
            if a > 0:
                right.value += 1
            new[a] = Array(tuple(Integer(z) for z in range(left.value, right.value, step)))
            del new[a + 1]
            if a > 0:
                del new[a - 1]
                a -= 1
        elif new[a] == 'skip':
            if a - 1 < 0:
                call_error('skip requires a left hand argument.', 'argerr', error)
            if a + 1 >= len(new):
                call_error('skip requires a right hand argument.', 'argerr', error)
            left = evaluate((new[a - 1],), args=args, error=error)
            right = evaluate((new[a + 1],), args=args, error=error)
            if not isinstance(left, Array):
                call_error('skip can only skip items in an Array.', 'type', error)
            if not isinstance(right, Integer):
                call_error('skip can only skip through an Array using an Integer as index.', 'type', error)
            new[a] = Array()
            if right.value:
                new[a] = Array(left.value[::right.value])
            del new[a + 1]
            del new[a - 1]
            a -= 1
        elif new[a] == 'break':
            if not break_token:
                call_error('Can not break non-existent loop.', 'break', error)
            return BreakToken()
        elif new[a].startswith('<EVAL>') and new[a].endswith('</EVAL>'):
            new[a] = new[a][6:-7]
            b = new[a].split('\n\\')
            new[a] = eval_statement(b[0], args, b[1])
        elif new[a].startswith('(') or new[a].endswith(')'):
            if not new[a].startswith('('):
                call_error('Unmatched ' + pformat(')') + '.', 'syntax', error)
            if not new[a].endswith(')'):
                call_error('Unmatched ' + pformat('(') + '.', 'syntax', error)
            temp = False
            if not a - 1 < 0:
                if isinstance(new[a - 1], (Function, BuiltinFunction)):
                    temp = True
            if not temp:
                values = evaluate(tokenise(new[a][1:-1].strip()), args=args, error=error)
                if isinstance(values, tuple):
                    new[a] = Array()
                else:
                    new[a] = values
                if len(new) > 1 and len(exp) > 1:
                    a -= 1
                a += 1
                continue
            values = evaluate(tokenise(new[a][1:-1].strip()), error=error, args=args, translate=False)
            new[a] = call_function(new[a - 1], values)
            del new[a - 1]
            a -= 1
        elif new[a].startswith('`') or new[a].endswith('`'):
            if not new[a].startswith('`') or not new[a].endswith('`'):
                call_error('Unmatched ' + pformat('`') + '.', 'syntax', error)
            values = evaluate(tokenise(new[a][1:-1].strip()), error=error, args=args)
            new[a] = values
            if len(new) > 1 and len(exp) > 1:
                a -= 1
        elif new[a].startswith('{') or new[a].endswith('}'):
            if not new[a].startswith('{'):
                call_error('Unmatched ' + pformat('}') + '.', 'syntax')
            if not new[a].endswith('}'):
                call_error('Unmatched ' + pformat('{') + '.', 'syntax')
            value = run(
                new[a].strip()[1:-1].strip(),
                filename='keep',
                echo=True,
                raw=True,
                yielding=True,
                localargs=args,
                independent=True,
                has_breadcrumbs=has_breadcrumbs)
            if isinstance(value, BreakToken):
                return value
            new[a] = Array(value)
            if not value:
                new[a] = Null()
            elif len(value) == 1:
                new[a] = value[0]
        elif new[a].startswith('[') or new[a].endswith(']'):
            if not new[a].startswith('['):
                call_error('Unmatched ' + pformat(']') + '.', 'syntax')
            if not new[a].endswith(']'):
                call_error('Unmatched ' + pformat('[') + '.', 'syntax')
            if not new[a][1:-1].strip():
                new[a] = Arglist(new[a])
            elif ',' in new[a]:
                new[a] = Arglist(new[a])
            else: # ':' in new[a]
                new[a] = Slice(new[a])
            a -= 1
        elif new[a] == 'array':
            contents = new[a + 1] if a < len(new) - 1 else []
            if contents:
                contents = evaluate((new[a + 1],), args=args, error=error)
            if not isinstance(contents, (tuple, list, String, Array)):
                contents = (contents,)
            new[a] = translate_datatypes(contents)
            if a < len(new) - 1:
                del new[a + 1]
        elif new[a] in local_vars:
            new[a] = local_vars[new[a]]
            a -= 1
        elif new[a] in global_vars:
            new[a] = global_vars[new[a]]
            a -= 1
        elif new[a] in reserved_names:
            call_error('invalid syntactical usage of reserved name ' + pformat(new[a]) + '.', 'syntax')
        else:
            token = new[a]
            if len(token) > 100:
                token = token[:97] + '...'
            call_error('undefined token: ' + pformat(token), 'syntax', error)
        a += 1
    if array_cont:
        if len(new) > 1:
            call_error('too many values in a row, use commas to separate Array items.', 'syntax', error)
        if len(new) == 1:
            array_cont += [new[0]]
        return translate_datatypes(tuple(array_cont)) if translate else tuple(array_cont)
    if not new:
        return new
    if len(new) == 1:
        if funcargs:
            new = new,
        return translate_datatypes(new[0])
    if len(new) > 1:
        call_error('too many values in a row, use commas to separate Array items.', 'syntax', error)
    return translate_datatypes(new) if translate else new


def doMDCLExit():
    raise MDCLExit()


def convert_escapes(quoted_string):
    return (quoted_string
        .replace('\a', '\\a')
        .replace('\b', '\\b')
        .replace('\f', '\\f')
        .replace('\n', '\\n')
        .replace('\r', '\\r')
        .replace('\t', '\\t')
    )


def split_list(s, split_at, astype=None):
    o = []
    c = []
    for a in s:
        if '__call__' in dir(split_at):
            c += [a]
            if split_at(a):
                o += [c]
                c = []
        elif a == split_at and isinstance(split_at, str):
            o += [c]
            c = []
        else:
            c += [a]
    o = filter(None, o + [c])
    return astype(o) if astype is not None else list(o)


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
    def read(args):
        return String(get_input(*args)
            if [a for a in args if type(a) is not Null]
            else get_input())

    @staticmethod
    def get_length(args):
        if isinstance(args[0], builtin_types):
            return Integer(len(args[0].value))
        return Integer(len(args[0]))

    @staticmethod
    def readfile(args):
        if not isinstance(args[0], String):
            call_error('readfile first argument must be of type String, ' + type(args[0]).__name__ + ' is invalid.', 'argerr')
        try:
            with open(args[0].value, 'rb') as f:
                data = f.read()
            data = data.decode('utf-8').replace('\r\n', '\n')
            return String(data)
        except UnicodeDecodeError:
            call_error('readfile failed to decode file encoding from: "' + str(args[0]) + '".', 'ioerr')
        except FileNotFoundError:
            call_error('file at path: "' + str(args[0]) + '" does not exist.', 'filenotfound')
        except Exception:
            call_error('readfile failed to read from the file at path: "' + str(args[0]) + '"', 'ioerr')

    @staticmethod
    def writefile(args):
        if not isinstance(args[0], String):
            call_error('writefile first argument must be of type String, ' + type(args[0]).__name__ + ' is invalid.', 'argerr')
        if not isinstance(args[1], String):
            call_error('writefile second argument must be of type String, ' + type(args[1]).__name__ + ' is invalid.', 'argerr')
        try:
            with open(args[0].value, 'w') as f:
                f.write(args[1].value)
            return Integer(len(args[1].value))
        except Exception:
            call_error('writefile failed to write to file at path: "' + str(args[0]) + '"', 'ioerr')

    @staticmethod
    def get_type(args):
        if not args:
            args = [Null()]
        return String(type(args[0]).__name__)

    @staticmethod
    def echo(args):
        sys.stdout.write(str(args[0]))
        return String('')

    @staticmethod
    def write(args):
        content = String('') if isinstance(args[0], Null) else args[0]
        sep = args[1] if isinstance(args[1], String) else String(' ')
        end = args[2] if isinstance(args[2], String) else String('\n')
        if isinstance(content, Array):
            content = String(sep.value.join([str(a) for a in content.value]))
        if isinstance(content, str):
            content = String(content)
        print(content, end=end.value)
        return String('')

    @staticmethod
    def wait(args):
        time.sleep(args[0].value)
        return String('')

    @staticmethod
    def get_globals(args):
        return Array(global_vars.keys()._value)

    @staticmethod
    def get_locals(args):
        return Array(local_vars.keys()._value)

    @staticmethod
    def get_argv(args):
        args = list(args)
        if isinstance(args[0], Integer):
            args[0] = args[0].value
        if isinstance(args[0], int):
            if args[0] < len(global_args):
                return global_args[args[0]]
            else:
                return Null()
        return Array(global_args)

    @staticmethod
    def get_data(args):
        if isinstance(args[0], datatypes):
            n = Null()
            n.data['value'] = '{'
            n.value = '{'
            for a in list(args[0].data.keys()):
                b = a + ': ' + pformat(args[0].data[a]) + ', '
                n.data['value'] += b
                n.value += b
            n.data['value'] = String(n.data['value'][:-2] + '}')
            n.value = String(n.value[:-2] + '}')
            return n
        return Null()

    @staticmethod
    def get_keys(args):
        if isinstance(args[0], datatypes):
            n = Null()
            n.data['value'] = '('
            n.value = '('
            for a in list(args[0].data.keys()):
                b = pformat(a) + ', '
                n.data['value'] += b
                n.value += b
            n.data['value'] = String(n.data['value'][:-2] + ')')
            n.value = String(n.value[:-2] + ')')
            return n
        return Null()

    @staticmethod
    def _exec(args):
        mdc_assert(None, args[0], String, 'exec', showname=False)
        start(args[0].value)
        return Null()

    @staticmethod
    def _eval(args):
        mdc_assert(None, args[0], String, 'eval', showname=False)
        return evaluate(tokenise(args[0].value))

    @staticmethod
    def _assign(args):
        mdc_assert(None, args[0], String, 'assign', showname=False)
        local_vars[args[0].value] = args[1]
        return Null()


#
# VARIABLES
#

sig_c = SignalCatches()

current_file = ''
current_code = ''
current_line = 1
current_catch = {}
breadcrumbs = []
break_token = False
previous_condition = None

reserved_names = (
    'ERR',
    'PATH',
    ',',
    '?',

    'new',
    'if',
    'elif',
    'else',
    'while',
    'for',
    'try',
    'catch',
    ':',
    'del',
    'import',
    'define', # Remake define statement.
    'sig',
    'raise',
    'errortag',
    'yield',

    'add',
    'sub',
    'mult',
    'div',
    'pwr',
    'mod',
    'eq',
    'lt',
    'gt',
    'le',
    'ge',
    'index',
    'has',

    '+',
    '-',
    '*',
    '/',
    '^',
    '%',
    '=',
    '|',

    'call',
    'and',
    'or',
    'only',
    'to',
    'skip',
    'break',
    'array',

    'int',
    'float',
    'string',
    'regex',
    'timedelta',
    'date',
    'slice',
    'bool',
    'null',

    'read',
    'len',
    'readfile',
    'writefile',
    'type',
    'echo',
    'wait',
    'globals',
    'locals',
    'argv',

    'not',

    'exit',
)

mdcl_keywords = (
    'add',
    'sub',
    'mult',
    'div',
    'pwr',
    'mod',
    'eq',
    'lt',
    'gt',
    'le',
    'ge',
    'has',
)

start_error_tags = error_tags = CompactDict({
    'exp': 'ERROR attempting to evaluate expression',
    'ioerr': 'IOERROR',
    'argerr': 'ARGUMENT ERROR',
    'assert': 'ASSERTION ERROR',
    'var': 'VAR ERROR',
    'syntax': 'SYNTAX ERROR',
    'attr': 'ATTRIBUTE ERROR',
    'recursion': 'RECURSION ERROR',
    'type': 'TYPE ERROR',
    'value': 'VALUE ERROR',
    'keyboardinterrupt': 'KEYBOARD INTERRUPT',
    'eoferror': 'END OF FILE ERROR',
    'unknownvalue': 'UNKNOWN VALUE',
    'filenotfound': 'FILE NOT FOUND ERROR',
    'dirnotfound': 'DIRECTORY NOT FOUND ERROR',
    'outofrange': 'OUT OF RANGE ERROR',
    'import': 'IMPORT ERROR',
    'namespace': 'NAMESPACE ERROR',
    'zerodivision': 'ZERO DIVISION ERROR',
    'readonly': 'READONLY VALUE',
    'fatal': 'FATAL ERROR',
    'defined': 'ALREADY DEFINED VALUE',
    'break': 'BREAK KEYWORD ERROR',
})

datatypes_switch = {
    str: String,
    int: Integer,
    float: Float,
    datetime.datetime: Date,
    datetime.timedelta: Timedelta,
    bool: Boolean,
    tuple: Array,
    list: Array,
    CompactList: Array,
    type(None): Null,
    types.FunctionType: BuiltinFunction,
}
builtin_types = tuple(set(datatypes_switch.values())) + (
    RegexString,
    Slice,
    Function,
    Arglist,
    Module,
    BreakToken,
)

local_vars = None
initialise_local_vars()

datatypes = copy(builtin_types)
global_vars = CompactDict()
global_args = [String(a) for a in (sys.argv if _is_compiled else sys.argv[1:])]

import functools
fname = os.path.abspath(sys.argv[0])
dirname = os.path.dirname(fname)
src_path = sys.path[0] if _debug_mode else os.path.dirname(sys.path[0])
initialise_path(src_path, dirname, compiled=True)

def iterate(arg):
    if isinstance(arg, int):
        arg = range(arg)
    return arg
def call(func, args=None):
    return call_function(local_vars[func], args)

for a in local_vars:
    exclude = ['len', 'type', 'locals', 'globals', 'exec', 'eval', 'int', 'float']
    if type(local_vars[a]) in (Function, BuiltinFunction) and a not in globals().keys() and a not in exclude:
        exec(a + '=functools.partial(call, ' + pformat(a) + ')')

scb = '{'
ecb = '}'
sb = '('
eb = ')'

def cbstrip(str,):
    if (str [0] == scb) and (str [-1] == ecb):
        str = str [1:-1]
    return str . strip ("\n\t ")
def bstrip(str,):
    if (str [0] == sb) and (str [-1] == eb):
        str = pyeval(pretty(str) + '[1:-1]')
    return str . strip ("\n\t ")

print(bstrip('({code you know}}())'))
