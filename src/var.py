'''

MDCL created by Aiden Blishen Cuneo.
First Commit was at: 1/1/2020.

'''

_debug_mode = True
__version__ = '1.5.7'

import ast
import datetime
import os
import random
import re
import signal
import sys
import string
import threading
import time
import traceback as tb
import types

from copy import copy, deepcopy
from functools import partial
from pprint import pformat

import loader

from compact import CompactList, CompactDict

get_input = raw_input if sys.version_info[0] < 3 else input


class SignalCatches:

    def __init__(self):
        self.switches = {
            'INT': True,
            'TSTP': True,
            'SEGV': True,
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

    def __init__(self, value=None):
        self.data = CompactDict({} if value is None else {
            'value': value,
        })

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


class Function(BaseDatatype):

    def __init__(self, name, args=None, code=None):
        if isinstance(name, (Function, BuiltinFunction)):
            self.name = name.name
            self.args = name.args
            self.code = name.code
        else:
            if args is None or code is None:
                call_error('Function can not be declared without second or third arguments '
                    'if first argument is not a Function. This is a Python error.', 'fatal')
            for a in range(len(args)):
                for b in range(len(args[a])):
                    if isinstance(args[a][b], type):
                        args[a][b] = args[a][b].__name__
            self.name = name
            self.args = args
            self.code = code
        self.value = self.get_value()
        super().__init__(self.value)
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
                call_error('Function ' + self.name + ' requires at least ' + str(len(r))
                    + ' positional argument' + ('' if len(r) == 1 else 's') + '.', 'argerr')
        for a in range(len(self.args)):
            if a >= len(args):
                args += (Null(),)
        if len(args) > len(self.args):
            call_error('Function ' + self.name + ' received too many arguments, '
                'maximum amount for this Function is ' + str(len(self.args)) + '.', 'argerr')
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
        return pformat(self.value)

    def __bool__(self):
        return bool(self.value)

    def call(self):
        return not self.value, Boolean

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
        super().__init__(self.value)

    def __repr__(self):
        return pformat(self.value)

    def __str__(self):
        return self.value

    def call(self):
        return not self.value, Boolean

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
        return 'RE' + pformat(self.value.pattern)

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
        return '[' + ':'.join([str(a) for a in self.value]) + ']'

    def make_slice(self, value):
        value = value.strip('[]')
        if ':' in value:
            value = value.split(':')
        else:
            value = (value, value, '')
        if len(value) > 3:
            call_error('slice received too many arguments, maximum is 3.', 'argerr')
        while len(value) < 3:
            value += ['']
        if not value[0]:
            value[0] = '0'
        if not value[1]:
            value[1] = '.'
        if not value[2]:
            value[2] = '1'
        try:
            value[0] = int(value[0])
        except ValueError:
            call_error('Non-Integer value found in position 0 of slice.', 'value')
        try:
            value[1] = int(value[1])
        except ValueError:
            if value[1] != '.':
                call_error('Non-Integer value found (or missing dot) in position 1 of slice.', 'value')
        try:
            value[2] = int(value[2])
        except ValueError:
            call_error('Non-Integer value found in position 2 of slice.', 'value')
        return value

    def do_slice(self, obj):
        if isinstance(obj, (String, Array)):
            start = self.value[0]
            stop = len(obj.value) if self.value[1] == '.' else self.value[1]
            skip = self.value[2]
            if start and stop < len(obj.value) and skip != 1:
                newval = obj.value[start:stop:skip]
            elif start and stop < len(obj.value):
                newval = obj.value[start:stop]
            elif start and skip != 1:
                newval = obj.value[start::skip]
            elif start:
                newval = obj.value[start:]
            elif stop < len(obj.value) and skip != 1:
                newval = obj.value[:stop:skip]
            elif skip != 1:
                newval = obj.value[::skip]
            if isinstance(obj, String):
                return String(newval)
            if isinstance(obj, Array):
                return Array(newval)
        if not 'index' in dir(obj):
            call_error('Datatype ' + type(obj).__name__ + ' does not have an index method to deal with slice.', 'attr')
        if isinstance(obj.index, (Function, BuiltinFunction)):
            return obj.index.call((obj, self,))
        return obj.index(self)


class Arglist(BaseDatatype):

    def __init__(self, value):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
        mdc_assert(self, value, (str, String, Arglist), 'ARGTYPES', showname=False)
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
        super().__init__(self.value)

    def __repr__(self):
        return repr(self.value).upper()

    def __str__(self):
        return repr(self)

    def __bool__(self):
        return bool(self.value)

    def call(self):
        return not self.value, Boolean


class Array(BaseDatatype):

    def __init__(self, value=None):
        mdc_assert(self, value, (tuple, list) + builtin_types, 'ARRAY', showname=False)
        if isinstance(value, (tuple, list)):
            self.value = tuple(value)
        elif isinstance(value, String):
            self.value = tuple(String(a) for a in value.value)
        elif isinstance(value, Array):
            self.value = tuple(value.value)
        elif isinstance(value, Null):
            self.value = tuple()
        elif isinstance(value, builtin_types):
            self.value = (value,)
        super().__init__(self.value)

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


class Null(BaseDatatype):

    def __init__(self, *args):
        self.value = None
        super().__init__(self.value)

    def __repr__(self):
        return pformat('null')

    def __str__(self):
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
        return pformat('BREAK')

    def __str__(self):
        return 'BREAK'


class MDCLError(Exception):
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


def initialise_path(src_path, local_path):
    if not os.path.isdir(src_path):
        call_error("The path: '" + str(src_path) + "' could not be found.", 'dirnotfound')
    if not os.path.isdir(local_path):
        call_error("The path: '" + str(local_path) + "' could not be found.", 'dirnotfound')
    os.chdir(local_path)
    global_vars['PATH'] = Array([
        String(local_path),
        String(os.path.abspath(src_path + '/builtins')),
        String(src_path),
    ])
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
    global_vars[','] = Null()


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
        return evaluate(current_catch[er], error=error, args=args)
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


def start(rawcode, filename=None):
    try:
        run(rawcode, filename, raw=True)
    except MDCLError as e:
        call_error(error_type=e)
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
        code = loader.process(code)
    if oneline:
        code = [code]
    lines = loader.tokenise_file(rawcode, dofilter=False)
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
            a = replacekeys(code[i], args=localargs)
        else:
            a = replacekeys(loader.tokenise(code[i]), args=localargs)
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
            if len(a) < 3 or ':' not in a:
                call_error('If statement requires at least a condition, the ":" separator, and code to run.', 'syntax')
            contents = tuple(filter(None, split_list(a[1:], ':')))
            if not contents[1:]:
                call_error('If statement requires at least a condition, the ":" separator, and code to run.', 'syntax')
            conditions = [contents[0]]
            runcodes = [contents[1]]
            haselse = False
            con = contents[2:]
            b = 0
            while b < len(con):
                if con[b][0] == 'if':
                    call_error('If can not be placed after elif or else in the same chain.', 'syntax')
                elif con[b][0] == 'elif':
                    if len(con[b]) < 2 or b + 1 >= len(con):
                        call_error('Elif statement requires at least a condition, the ":" separator, and code to run.', 'syntax')
                    if haselse:
                        call_error('Elif can not be placed after else in the same chain.', 'syntax')
                    conditions += [con[b][1:]]
                    runcodes += [con[b + 1]]
                    b += 1
                elif con[b][0] == 'else':
                    haselse = True
                    if b + 1 >= len(con):
                        call_error('Else statement requires at least the ":" separator and code to run.', 'syntax')
                    if len(con[b]) > 1:
                        call_error('Else statement can not have any conditions, use the elif statement to evaluate conditions.', 'syntax')
                    conditions += ['else']
                    runcodes += [con[b + 1]]
                    b += 1
                elif haselse:
                    call_error('An else statement ends an if-elif-else chain, tokens can not be evaluated after a chain has ended.', 'syntax')
                b += 1
            if len(conditions) != len(runcodes):
                call_error('Number of conditions must be equal to number of code sets to run in an if-elif-else chain.', 'syntax')
            for b in range(len(conditions)):
                e = False
                if conditions[b] == 'else':
                    e = True
                elif bool(evaluate(conditions[b], error=code[i], args=localargs)):
                    e = True
                if e:
                    ev = evaluate(runcodes[b], error=code[i], args=localargs, has_breadcrumbs=False)
                    if isinstance(ev, BreakToken):
                        return ev
                    if not isinstance(ev, Null):
                        if yielding:
                            yielded += [ev]
                        else:
                            o += str(ev)
                            if echo:
                                sys.stdout.write(str(ev))
                    break
        elif a[0] == 'while':
            if len(a) < 3 or ':' not in a:
                call_error('While loop requires at least a condition, the ":" separator, and code to run.', 'syntax')
            contents = tuple(filter(None, split_list(a[1:], ':')))
            if not contents[1:]:
                call_error('While loop requires at least a condition, the ":" separator, and code to run.', 'syntax')
            condition = contents[0]
            runcode = contents[1]
            while bool(evaluate(condition, error=code[i], args=localargs)):
                break_token = True
                ev = evaluate(runcode, error=code[i], args=localargs, has_breadcrumbs=False)
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
            if len(a) < 3 or ':' not in a:
                call_error('For loop requires at least a variable name, iterable, the ":" separator, and code to run.', 'syntax')
            contents = tuple(filter(None, split_list(a[1:], ':')))
            if not contents[1:]:
                call_error('For loop requires at least an iterable, the ":" separator, and code to run.', 'syntax')
            if not contents[2:]:
                variable = None
                iterable = evaluate(contents[0], error=code[i], args=localargs)
                runcode = contents[1]
            else:
                variable = contents[0][0]
                iterable = evaluate(contents[1], error=code[i], args=localargs)
                runcode = contents[2]
            if variable in global_vars and variable != ',':
                call_error('Name ' + pformat(variable) + ' is already defined in the global variables list.', 'var')
            if variable in reserved_names and variable != ',':
                call_error('Invalid for loop variable name, for loop variable names can not be reserved names', 'var')
            if isinstance(iterable, Null):
                call_error('For loop iterable can not be null.', 'syntax')
            if not runcode:
                call_error('For loop code to run can not be empty.', 'syntax')
            if not isinstance(iterable, (Integer, String, Array)):
                call_error('For loop can only iterate over an Array, Integer, or String.', 'type')
            if isinstance(iterable, Integer):
                iterable = list(range(iterable.value))
            elif isinstance(iterable, String):
                iterable = Array(iterable)
            oldvariable = None
            if variable in local_vars:
                oldvariable = local_vars[variable]
            for val in translate_datatypes(iterable).value:
                if variable is not None:
                    local_vars[variable] = val
                local_vars[','] = val
                break_token = True
                ev = evaluate(runcode, error=code[i], args=localargs, has_breadcrumbs=False)
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
            if len(a) < 3 or ':' not in a:
                call_error('Try statement requires at least the ":" separator and code to run.', 'syntax')
            contents = split_list(a[1:], ':')
            runcode = contents[0]
            if not runcode:
                call_error('Try statement code to run can not be empty.', 'syntax')
            catches = {}
            keys = []
            for b in contents[1:]:
                if b[0] == 'catch':
                    keys = b[1:]
                else:
                    if not keys:
                        call_error('Try statement requires catch keyword before second set of code to run.', 'syntax')
                    keys = evaluate(keys, error=code[i], args=localargs)
                    if isinstance(keys, Array):
                        keys = keys.value
                    if not isinstance(keys, (tuple, list)):
                        keys = keys,
                    for c in keys:
                        if not isinstance(c, String):
                            call_error('Catch arguments must be of type String.', 'type')
                        catches[c.value] = b
                    keys = []
            if keys:
                call_error('Unfinished catch keyword in try statement')
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
                        call_error('Invalid variable name. Variable names can not be reserved names.', 'var')
                    if not re.match('^[a-zA-Z]+$', key[k + 1]) and key[k + 1]:
                        call_error('Invalid variable name, variable names must fit this regex expression: ^[a-zA-Z]+$', 'var')
                if k < len(key) - 2:
                    if not key[k]:
                        call_error('Cannot set attribute with a null parent. (Missing value before `.`)', 'argerr')
                    if k + 1 >= len(key):
                        call_error('Missing attribute to set inside parent "' + key[k - 1] + '".', 'argerr')
                    old = key[k]
                    key[k] = evaluate([key[k]], error=code[i], args=localargs)
                    try:
                        key[k] = key[k].data[key[k + 1]]
                    except KeyError:
                        call_error('Variable ' + pformat(old) + ' does not have attribute ' + pformat(key[k + 1]) + '.',
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
            if key[2:] or not key:
                call_error('Invalid settatr syntax.', 'syntax')
            if key[1:]:
                if oper != ':' and key[0] not in local_vars:
                    call_error('Undefined Token: ' + pformat(key[0]), 'syntax', code[i])
                if oper != ':' and key[1] not in local_vars[key[0]].data:
                    call_error('Variable ' + pformat(key[0]) + ' does not have attribute ' + pformat(key[1]) + '.',
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
                local_vars[key[0]].data[key[1]] = value
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
                local_vars[key[0]] = value
        elif a[0] == 'del':
            if len(a) < 2:
                call_error('Del statement missing variable or key to delete.', 'argerr')
            key = ''.join(a[1:])
            if key in local_vars:
                if isinstance(local_vars[key], BuiltinFunction):
                    call_error('Del statement can not delete built-in functions.', 'argerr')
                del local_vars[key]
            elif key in global_vars:
                call_error('Del statement can not delete global arguments.', 'argerr')
        elif a[0] == 'import':
            if len(a) < 2:
                call_error('Import requires at least one argument.', 'argerr')
            fnames = evaluate(a[1:], error=code[i], args=localargs)
            if any(not isinstance(f, String) for f in fnames):
                call_error('Import arguments must be of type String.', 'type')
            for fname in fnames:
                for b in global_vars['PATH'].value:
                    c = String(str(b.value) + '/' + str(fname.value))
                    f = c.value
                    if not f.endswith('.mdcl'):
                        f += '.mdcl'
                    newcode = loader.get_code(f)
                    if isinstance(newcode, Exception):
                        continue
                    oldfile = current_file
                    oldcode = current_code
                    oldline = current_line
                    run(newcode, f, raw=True)
                    current_file = oldfile
                    current_code = oldcode
                    current_line = oldline
                    break
                else:
                    call_error('No scripts within directory ' + pformat(b.value) + ' could be found or imported from.', 'import')
        elif a[0] == 'sig':
            a = evaluate_line(a, start=2, error=code[i], args=localargs)
            if len(a) < 2:
                call_error('Sig requires at least a signal name.', 'argerr')
            signal_name = a[1].strip()
            if signal_name not in sig_c.switches:
                call_error('Signal ' + pformat(signal_name) + ' is not a valid signal.', 'unknownvalue')
            newvalue = not sig_c.switches[signal_name]
            if len(a) > 2:
                newvalue = Boolean(a[2]).value.value
            if not isinstance(newvalue, bool):
                call_error('Sig new value must evaluate to Boolean.', 'type')
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
                call_error('Error type to raise must be of type String.', 'type')
            if not isinstance(errortext, String):
                call_error('Error text must be of type String', 'type')
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
                call_error('Errortag requires at least an error type name.', 'argerr')
            errortype = a[1]
            errortag = String('')
            if len(a) > 2:
                errortag = a[2]
            if not isinstance(errortype, String):
                call_error('Error type to set tag for must be of type String.', 'type')
            if not isinstance(errortag, String):
                call_error('Error tag must be of type String.', 'type')
            if errortype.value in error_tags and errortag.value:
                call_error('An error tag with that name already exists.', 'type')
            if errortype.value in start_error_tags:
                call_error('Built-in errortags are readonly.', 'readonly')
            if errortag.value:
                error_tags[errortype.value] = errortag.value
            else:
                del error_tags[errortype.value]
        elif a[0] == 'yield':
            if not yielding:
                call_error('Yielding is not possible from the current scope.', 'syntax')
            yielded += [evaluate(a[1:], error=code[i], args=localargs)]
        else:
            a = evaluate(a, error=code[i], args=localargs)
            if isinstance(a, BreakToken):
                return a
            if isinstance(a, builtin_types) and not isinstance(a, Null):
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
                call_error('Variable ' + pformat(exp[a - 1]) + ' does not have attribute ' + pformat(new[a + 1]) + '.', 'attr', error)
            del new[a]
            del new[a]
            a -= 1
        elif re.match('^re(\'|").+(\'|")', new[a]): # Is new[a] a Regex String? If so, assign Regex() class.
            try:
                new[a] = RegexString(ast.literal_eval(new[a][2:]))
            except Exception:
                call_error('Invalid Regex String.', 'syntax', error)
        elif re.match("^'.*'$", new[a]): # Is new[a] a string with single quotes? If so, assign String() class using RAW value.
            new[a] = String(new[a][1:-1])
        elif re.match('^".*"$', new[a]): # Is new[a] a string with double quotes? If so, assign evaluated String() class.
            try:
                new[a] = String(ast.literal_eval(new[a]))
            except Exception:
                call_error('Invalid String.', 'syntax', error)
        elif re.match('^(-|\+)*[0-9]*\.[0-9]+$', new[a]): # Is new[a] a float? If so, assign Float() class.
            new[a] = Float(float(new[a]))
        elif re.match('^(-|\+)*[0-9]+$', new[a]): # Is new[a] an integer? If so, assign Integer() class.
            new[a] = Integer(int(new[a]))
        elif new[a] in ('true', 'false'): # Is new[a] a boolean? If so, assign Boolean() class.
            new[a] = Boolean(bool(new[a]))
        elif new[a] == 'null': # Is new[a] null? If so, assign Null() class.
            new[a] = Null()
        a += 1
    return new


def evaluate_line(oldline, start, end=None, error=None, args=None):
    if end is None:
        end = len(oldline)
    new_line = evaluate(replacekeys(oldline[start:end], args=args), error=error, args=args)
    if isinstance(new_line, Array):
        oldline[start:end] = new_line.value
    else:
        oldline[start] = new_line
    return oldline


def evaluate(exp, error=None, args=None, funcargs=False, has_breadcrumbs=True, func_self=True):
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
    }
    new = [a for a in exp]
    new = pre_evaluate(new, error=error)
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
                call_error('Missing first argument for ' + new[a] + ' method.', 'syntax', error)
            if a + 1 >= len(new):
                call_error('Missing second argument for ' + new[a] + ' method.', 'syntax', error)
            try:
                vals = new[a - 1].do_action(new[a], (evaluate([new[a + 1]], error=error, args=args),))
                settype = vals[1] if isinstance(vals, tuple) else type(vals)
                new[a] = settype(vals[0] if isinstance(vals, tuple) else vals)
                del new[a + 1]
                del new[a - 1]
                a -= 1
            except AttributeError:
                call_error('Type ' + type(new[a - 1]).__name__ + ' does not have a method for handling ' + new[a],
                    'attr', error)
        elif isinstance(new[a], Slice):
            if a - 1 >= 0:
                vals = new[a].do_slice(new[a - 1])
                settype = vals[1] if isinstance(vals, tuple) else type(vals)
                new[a] = settype(vals[0] if isinstance(vals, tuple) else vals)
                del new[a - 1]
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
                call_error('Inline Function declaration requires a left hand argument.', 'argerr', error)
            if a + 1 >= len(new):
                call_error('Inline Function declaration requires a right hand argument.', 'argerr', error)
            if not isinstance(new[a - 1], Arglist):
                call_error('Inline Function declaration requires Arglist as left hand argument.', 'type', error)
            if not (new[a + 1].startswith('{') and new[a + 1].endswith('}')):
                call_error('Inline Function declaration requires a code block as right hand argument.', 'type', error)
            func = new[a + 1]
            arguments = new[a - 1].value
            new[a] = Function('<InlineFunction>', arguments, func)
            del new[a + 1]
            del new[a - 1]
            a += 1
        elif new[a] == '!':
            if a + 1 >= len(new):
                call_error('call requires a right hand argument.', 'argerr', error)
            del new[a]
            new[a:] = as_tuple(evaluate(new[a:], error=error, args=args))
            thishas = dir(new[a])
            if 'call' not in thishas:
                call_error('Type ' + type(new[a]).__name__ + ' is not callable.', 'attr', error)
            if 'args' not in thishas or 'code' not in thishas:
                vals = new[a].call()
                settype = vals[1] if isinstance(vals, tuple) else type(vals)
                new[a] = settype(vals[0] if isinstance(vals, tuple) else vals)
                a -= 1
                continue
            f = as_tuple(evaluate(new[a + 1:], error=error, args=args, funcargs=True))
            oldlocals = deepcopy(local_vars)
            if func_self:
                local_vars['self'] = new[a]
            for i in range(len(new[a].args)):
                if not new[a].args[i]:
                    continue
                if i >= len(f) and new[a].args[i][-1] == '*':
                    f += Null(),
                elif i >= len(f):
                    call_error('Function ' + new[a].name + ' requires at least ' + str(len(new[a].args[i]))
                        + ' positional argument' + ('' if len(new[a].args[i]) == 1 else 's') + '.', 'argerr')
                if '@' not in new[a].args[i]:
                    local_vars[new[a].args[i][0]] = f[i]
            new[a] = new[a].call(f)
            local_vars = deepcopy(oldlocals)
            del new[a + 1:]
        elif new[a] == 'and':
            if a - 1 < 0:
                call_error('and requires a left hand argument.', 'argerr', error)
            if a + 1 >= len(new):
                call_error('and requires a right hand argument.', 'argerr', error)
            left = evaluate(replacekeys([new[a - 1]], args=args), error=error, args=args)
            right = evaluate(replacekeys([new[a + 1]], args=args), error=error, args=args)
            new[a] = Boolean(Boolean(left) and Boolean(right))
            del new[a + 1]
            del new[a - 1]
            a -= 1
        elif new[a] == 'or':
            if a - 1 < 0:
                call_error('or requires a left hand argument.', 'argerr', error)
            if a + 1 >= len(new):
                call_error('or requires a right hand argument.', 'argerr', error)
            left = evaluate(replacekeys([new[a - 1]], args=args), error=error, args=args)
            right = evaluate_line(new, start=a + 1, error=error, args=args)[a + 1]#evaluate(replacekeys([new[a + 1]], args=args), error=error, args=args)
            new[a] = Boolean(Boolean(left) or Boolean(right))
            del new[a + 1]
            del new[a - 1]
            a -= 1
        elif new[a] == 'only':
            if a - 1 < 0:
                call_error('only requires a left hand argument.', 'argerr', error)
            if a + 1 >= len(new):
                call_error('only requires a right hand argument.', 'argerr', error)
            argument = evaluate(replacekeys([new[a - 1]], args=args), error=error, args=args)
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
            left = evaluate(replacekeys([new[a - 1]], args=args), error=error, args=args) if a > 0 else Integer(0)
            right = evaluate(replacekeys([new[a + 1]], args=args), error=error, args=args)
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
            left = evaluate(replacekeys([new[a - 1]], args=args), error=error, args=args)
            right = evaluate(replacekeys([new[a + 1]], args=args), error=error, args=args)
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
            if a - 1 < 0:
                call_error('Shorthand condition requires a left hand argument.', 'argerr', error)
            if a + 1 >= len(new):
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
            b = [z.strip() for z in new[a][1:-1].split(':') if z.strip()]
            if not b:
                new[a] = Arglist(new[a])
            elif ',' in new[a]:
                new[a] = Arglist(new[a])
            elif all([re.match('^(-|\+)*[0-9]+$', z) for z in b]):
                new[a] = Slice(new[a])
            else:
                call_error('Invalid syntax for bracket expression: ' + pformat(new[a]), 'syntax', error)
            a -= 1
        elif new[a] == 'array':
            contents = new[a + 1] if a < len(new) - 1 else []
            if contents:
                contents = evaluate(replacekeys([new[a + 1]], args=args), error=error, args=args)
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
            call_error('Invalid syntactical usage of reserved name.', 'syntax')
        else:
            token = new[a]
            if len(token) > 100:
                token = token[:97] + '...'
            call_error('Undefined Token: ' + pformat(token), 'syntax', error)
        a += 1
    if not new:
        return new
    if funcargs and len(new) == 1:
        new = new,
    if len(new) == 1:
        return translate_datatypes(new[0])
    return translate_datatypes(new)


def replacekeys(line, args=None):
    for a in range(len(line)):
        if isinstance(line[a], builtin_types):
            pass
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
                    line[a] = Null()
                else:
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
            call_error('READFILE first argument must be of type String.', 'argerr')
        try:
            with open(args[0].value, 'rb') as f:
                data = f.read()
            data = data.decode('utf-8')
            return String(data)
        except UnicodeDecodeError:
            call_error('READFILE failed to decode file encoding from: "' + str(args[0]) + '".', 'ioerr')
        except FileNotFoundError:
            call_error('A file at path: "' + str(args[0]) + '" does not exist.', 'filenotfound')
        except Exception:
            call_error('READFILE failed to read from the file at path: "' + str(args[0]) + '"', 'ioerr')

    @staticmethod
    def writefile(args):
        pass

    @staticmethod
    def get_type(args):
        if not args:
            args = [Null()]
        return String(type(args[0]).__name__)

    @staticmethod
    def echo(args):
        content = String('') if isinstance(args[0], Null) else args[0]
        sep = args[1] if isinstance(args[1], String) else String(' ')
        end = args[2] if isinstance(args[2], String) else String('\n')
        if isinstance(content, Array):
            content = String(sep.value.join([str(a) for a in content.value]))
        elif isinstance(content, str):
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
        if isinstance(args[0], Integer):
            if args[0].value < len(global_args):
                return global_args[args[0].value]
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

reserved_names = (
    'FILE',
    '_',
    ',',
    'ERR',
    'PATH',

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
    'alphabet',

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
    'eval': 'ERROR attempting to run eval statement',
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
    type(None): Null,
    types.FunctionType: BuiltinFunction,
}
builtin_types = tuple(set(datatypes_switch.values())) + (
    RegexString,
    Slice,
    Function,
    Arglist,
    BreakToken,
)

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
        [['@', '*'], [String, '*'], [String, '*']],
        BFList.echo),
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

    'not': BuiltinFunction('not',
        [['@']],
        lambda x: Boolean(not x.value)),

    'exit': BuiltinFunction('exit',
        [],
        lambda x: (String(''), sys.exit())[0]),
})

datatypes = copy(builtin_types)
global_vars = CompactDict()
global_args = [String(a) for a in sys.argv[1:]]
