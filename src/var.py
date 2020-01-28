'''

MDCL created by Aiden Blishen Cuneo.
First Commit was at: 1/1/2020.

'''

_debug_mode = True
__version__ = '1.4.1'

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

from copy import copy
from functools import partial
from pprint import pformat

import loader

from compact import CompactList, CompactDict

get_input = raw_input if sys.version_info[0] < 3 else input


class SignalCatches:

    def __init__(self):
        self.switches = {
            'INT': True,
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

    def segmentation_fault(self, signal=None, frame=None):
        if self.switches['SEGV']:
            call_error('Segmentation Fault.', 'fatal')


class Function:

    def __init__(self, name, args, code):
        self.name = name
        for a in range(len(args)):
            for b in range(len(args[a])):
                if isinstance(args[a][b], type):
                    args[a][b] = args[a][b].__name__
        self.args = args
        self.code = code
        self.value = '<Function ' + str(self.name) + '>'

    def check_args(self, args):
        r = [a for a in self.args if '*' not in a]
        for a in range(len(r)):
            if a >= len(args):
                call_error('Function ' + self.name + ' requires at least ' + str(len(r))
                    + ' positional argument' + ('' if len(r) == 1 else 's') + '.', 'argerr')
        for a in range(len(self.args)):
            if a >= len(args):
                args += (Null(),)
            elif type(args[a]).__name__ not in self.args[a] and '@' not in self.args[a] and not isinstance(args[a], Null):
                types = '(' + ', '.join([b for b in self.args[a] if b != '*']) + ')'
                call_error('Argument ' + str(a + 1) + ' of function ' + self.name + ' must fit into: '
                    + types + '. "' + type(args[a]).__name__ + '" is invalid.', 'assert')
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
        r = self.code(args)
        global_vars['_'] = r
        return r


class BaseDatatype:

    def __init__(self, value):
        self.value = value.value

    def do_action(self, action, args):
        if action == 'ADD':
            f = self.ADD
        elif action == 'SUB':
            f = self.SUB
        elif action == 'MULT':
            f = self.MULT
        elif action == 'DIV':
            f = self.DIV
        elif action == 'PWR':
            f = self.PWR
        elif action == 'MOD':
            f = self.MOD
        elif action == 'EQ':
            f = self.EQ
        elif action == 'LT':
            f = self.LT
        elif action == 'GT':
            f = self.GT
        elif action == 'LE':
            f = self.LE
        elif action == 'GE':
            f = self.GE
        elif action == 'INDEX':
            f = self.INDEX
        elif action == 'HAS':
            f = self.HAS
        else:
            raise AttributeError
        if isinstance(f, (Function, BuiltinFunction)):
            value = f.call((self,) + args)
            return value, type(value)
        return f(*args)


class Integer(BaseDatatype):

    def __init__(self, value):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
        mdc_assert(self, value, (int, float) + (
            Integer, Float, String, Boolean, Null),
            'INTEGER', showname=False)
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

    def __repr__(self):
        return pformat(self.value)

    def __bool__(self):
        return bool(self.value)

    def ADD(self, other):
        mdc_assert(self, other, (Integer, Float, String), 'ADD')
        if isinstance(other, (Integer, Float)):
            return self.value + other.value, type(other)
        if isinstance(other, String):
            return str(self.value) + other.value, String

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

    def MOD(self, other):
        mdc_assert(self, other, (Integer, Float, Boolean), 'MOD')
        if isinstance(other, (Integer, Float)):
            return self.value % other.value, type(other)
        if isinstance(other, Boolean):
            return self.value % other.value.value, Integer

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


class Float(BaseDatatype):

    def __init__(self, value):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
        mdc_assert(self, value, (int, float) + (
            Integer, Float, String, Boolean, Null),
            'FLOAT', showname=False)
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

    def __repr__(self):
        return pformat(self.value)

    def __bool__(self):
        return bool(self.value)

    def ADD(self, other):
        mdc_assert(self, other, (Integer, Float), 'ADD')
        return self.value + other.value, Float

    def SUB(self, other):
        mdc_assert(self, other, (Integer, Float), 'SUB')
        return self.value - other.value, Float

    def MULT(self, other):
        mdc_assert(self, other, (Integer, Float, Boolean), 'SUB')
        if isinstance(other, (Integer, Float)):
            return self.value * other.value, Float
        if isinstance(other, Boolean):
            return self.value * other.value.value, Integer

    def DIV(self, other):
        mdc_assert(self, other, (Integer, Float, Boolean), 'DIV')
        if isinstance(other, (Integer, Float)):
            return self.value / other.value, Float
        if isinstance(other, Boolean):
            return self.value * int(not other.value.value), Integer

    def PWR(self, other):
        mdc_assert(self, other, (Integer, Float, Boolean), 'PWR')
        if isinstance(other, (Integer, Float)):
            return self.value ** other.value, Float
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


class String(BaseDatatype):

    def __init__(self, value):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
        mdc_assert(self, value, (str,) + datatypes,
            'STRING', showname=False)
        if isinstance(value, str):
            self.value = value
        elif isinstance(value, (Integer, Float, String, Null)):
            self.value = str(value.value)
        elif isinstance(value, RegexString):
            self.value = str(value.value.pattern)
        elif isinstance(value, Boolean):
            self.value = 'TRUE' if value.value.value else 'FALSE'
        elif isinstance(value, datatypes):
            self.value = String(value.value).value

    def __repr__(self):
        return pformat(self.value)

    def __str__(self):
        return self.value

    def ADD(self, other):
        mdc_assert(self, other, datatypes, 'ADD')
        if isinstance(other, (Integer, Float)):
            return self.value + str(other.value), String
        if isinstance(other, String):
            return self.value + other.value, String
        if isinstance(other, Array):
            return (self.value,) + other.value, Array
        return str(self.value) + str(other.value), String

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
            a = other.value.match(self.value)
            return bool(a) if a else 0, Boolean
        if isinstance(other, Boolean):
            return bool(self.value), Boolean
        if isinstance(other, Null):
            return not self.value, Boolean

    def INDEX(self, other):
        mdc_assert(self, other, Integer, 'INDEX')
        a = int(BFList.get_length((self,)).value)
        if int(other.value) > a - 1:
            call_error('String index out of range, ' + str(other) + ' > ' + str(a - 1) + '.',
                'outofrange')
        return self.value[other.value], String

    def HAS(self, other):
        mdc_assert(self, other, String, 'HAS')
        if isinstance(other, String):
            return other.value in self.value, Boolean


class RegexString(BaseDatatype):

    def __init__(self, value):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
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
        return bool(a) if a else 0, Boolean


class Timedelta(BaseDatatype):

    def __init__(self, value):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
        mdc_assert(self, value, (datetime.timedelta, Timedelta, Date, Null), 'TIMEDELTA', showname=False)
        if isinstance(value, datetime.timedelta):
            self.value = value
        elif isinstance(value, Timedelta):
            self.value = value.value
        else:
            self.value = datetime.timedelta()

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)

    def ADD(self, other):
        mdc_assert(self, other, (Date, Timedelta), 'SUB')
        return self.value + other.value, Timedelta

    def SUB(self, other):
        mdc_assert(self, other, (Date, Timedelta), 'SUB')
        return self.value - other.value, Timedelta

    def MULT(self, other):
        mdc_assert(self, other, (Date, Timedelta), 'MULT')
        return self.value * other.value, Timedelta

    def DIV(self, other):
        mdc_assert(self, other, (Date, Timedelta), 'DIV')
        return self.value / other.value, Float


class Date(BaseDatatype):

    def __init__(self, value):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
        mdc_assert(self, value, (datetime.datetime, Timedelta, Date, Null), 'DATE', showname=False)
        if isinstance(value, datetime.datetime):
            self.value = value
        elif isinstance(value, Timedelta):
            self.value = value.starttime
        elif isinstance(value, Date):
            self.value = value.value
        else:
            self.value = datetime.datetime.now()

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)

    def ADD(self, other):
        mdc_assert(self, other, (Date, Timedelta), 'SUB')
        return self.value + other.value, Timedelta

    def SUB(self, other):
        mdc_assert(self, other, (Date, Timedelta), 'SUB')
        return self.value - other.value, Timedelta


class Slice(BaseDatatype):

    def __init__(self, value):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
        mdc_assert(self, value, (str, String, Slice), 'SLICE', showname=False)
        if isinstance(value, str):
            self.value = self.make_slice(value)
        elif isinstance(value, String):
            self.value = self.make_slice(value.value)
        elif isinstance(value, Slice):
            self.value = self.make_slice(value.display())

    def __repr__(self):
        return pformat(self.display())

    def __str__(self):
        return self.display()

    def display(self):
        return '(' + ':'.join([str(a) for a in self.value]) + ')'

    def make_slice(self, value):
        value = value.strip('()')
        if ':' in value:
            value = value.split(':')
        else:
            value = (value, value, '')
        if len(value) > 3:
            call_error('Slice received too many arguments, maximum is 3.', 'argerr')
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
            call_error('Non-Integer value found in position 0 of Slice.', 'value')
        try:
            value[1] = int(value[1])
        except ValueError:
            if value[1] != '.':
                call_error('Non-Integer value found (or missing dot) in position 1 of Slice.', 'value')
        try:
            value[2] = int(value[2])
        except ValueError:
            call_error('Non-Integer value found in position 2 of Slice.', 'value')
        return value

    def do_slice(self, obj):
        if isinstance(obj, (String, Array, Alphabet)):
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
            if isinstance(obj, Alphabet):
                return Alphabet(newval)
        if not 'SLICE' in dir(obj):
            call_error('Datatype ' + type(obj).__name__ + ' does not have a method to deal with SLICE.', 'attr')
        return obj.SLICE(self)


class Boolean(BaseDatatype):

    def __init__(self, value):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
        mdc_assert(self, value, (int, str, bool) + builtin_types, 'BOOLEAN', showname=False)
        if isinstance(value, Array):
            raise e
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


class Array(BaseDatatype):

    def __init__(self, value=None):
        mdc_assert(self, value, (tuple, list) + builtin_types, 'ARRAY', showname=False)
        if isinstance(value, (tuple, list)):
            self.value = tuple(value)
        elif isinstance(value, String):
            self.value = tuple(String(a) for a in value.value)
        elif isinstance(value, (Array, Alphabet)):
            self.value = tuple(value.value)
        elif isinstance(value, Null):
            self.value = tuple()
        elif isinstance(value, builtin_types):
            self.value = (value,)

    def __repr__(self):
        return self.__str__()
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
        return self.value + (other,), Array

    def SUB(self, other):
        mdc_assert(self, other, (Integer, String), 'SUB')
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

    def MULT(self, other):
        mdc_assert(self, other, (Array, Alphabet), 'MULT')
        return self.value + other.value, Array

    def INDEX(self, other):
        mdc_assert(self, other, Integer, 'INDEX')
        a = int(BFList.get_length((self,)).value)
        if int(other.value) > a - 1:
            call_error('Array index out of range, ' + str(other) + ' > ' + str(a - 1) + '.',
                'outofrange')
        return self.value[other.value], type(self.value[other.value])

    def HAS(self, other):
        mdc_assert(self, other, builtin_types, 'HAS')
        return any(a.value == other.value for a in self.value), Boolean


class Alphabet(BaseDatatype):

    def __init__(self, value=None):
        if isinstance(value, tuple):
            if len(value) == 1:
                value = value[0]
        mdc_assert(self, value, (tuple, list, set) + builtin_types, 'ALPHABET', showname=False)
        if isinstance(value, set):
            self.value = value
        elif isinstance(value, Alphabet):
            self.value = value.value
        elif isinstance(value, Array):
            self.value = set(value.value)
        elif isinstance(value, String):
            self.value = set([String(a) for a in value.value])
        else:
            self.value = set((value,))
        self.check()

    def __repr__(self):
        return '{' + ', '.join(
            (type(a).__name__ + '(' + pformat(a) + ')')
            if isinstance(a, builtin_types) else pformat(a)
            for a in self.value) + '}'

    def __str__(self):
        return '{' + ', '.join(pformat(a) for a in self.value) + '}'

    def __bool__(self):
        return bool(self.value)

    def check(self):
        has = []
        temp = list(a if isinstance(a, builtin_types) else translate_datatypes(a) for a in self.value)
        temp = sorted(temp, key=lambda x: x.value)
        a = 0
        while a < len(temp):
            if not isinstance(temp[a], builtin_types):
                temp[a] = translate_datatypes(temp[a])
            if temp[a].value in has:
                temp.remove(temp[a])
            else:
                has += [temp[a].value]
                a += 1
        self.value = set(temp)


class Null(BaseDatatype):

    def __init__(self, *args):
        self.value = None

    def __repr__(self):
        return pformat('NULL')

    def __str__(self):
        return 'NULL'

    def __bool__(self):
        return False

    def ADD(self, other):
        return other.value, type(other)

    def SUB(self, other):
        mdc_assert(self, other, (Integer, Float, String, Boolean, Array, Null))
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

    def MULT(self, other):
        return None, Null

    def DIV(self, other):
        return None, Null

    def PWR(self, other):
        return None, Null

    def MOD(self, other):
        return None, Null

    def EQ(self, other):
        mdc_assert(self, other, builtin_types, 'EQ')
        if isinstance(other, (Integer, Float, String, Array, Alphabet)):
            return not other.value, Boolean
        if isinstance(other, RegexString):
            return not str(other.value.pattern), Boolean
        if isinstance(other, Boolean):
            return not other.value.value, Boolean
        if isinstance(other, Null):
            return True, Boolean
        return not other.value, Boolean

    def LT(self, other):
        mdc_assert(self, other, builtin_types, 'LT')
        if isinstance(other, (Integer, Float)):
            return 0 < other.value, Boolean
        if isinstance(other, (String, Array, Alphabet)):
            return other.value, Boolean
        if isinstance(other, RegexString):
            return str(other.value.pattern), Boolean
        if isinstance(other, Boolean):
            return 0 < other.value.value, Boolean
        if isinstance(other, Null):
            return False, Boolean
        return bool(other.value), Boolean

    def GT(self, other):
        mdc_assert(self, other, builtin_types, 'GT')
        if isinstance(other, (Integer, Float)):
            return 0 > other.value, Boolean
        if isinstance(other, (String, Array, Alphabet)):
            return not value.value, Boolean
        if isinstance(other, RegexString):
            return not str(other.value.pattern), Boolean
        if isinstance(other, Boolean):
            return False, Boolean
        if isinstance(other, Null):
            return False, Boolean
        return not other.value, Boolean

    def LE(self, other):
        mdc_assert(self, other, builtin_types, 'LE')
        if isinstance(other, (Integer, Float)):
            return 0 <= other.value, Boolean
        return True, Boolean

    def GE(self, other):
        mdc_assert(self, other, builtin_types, 'GE')
        if isinstance(other, (Integer, Float)):
            return 0 >= other.value, Boolean
        if isinstance(other, (String, Array, Alphabet)):
            return not value.value, Boolean
        if isinstance(other, RegexString):
            return not str(other.value.pattern), Boolean
        if isinstance(other, Boolean):
            return 0 >= other.value.value, Boolean
        if isinstance(other, Null):
            return False, Boolean
        return not other.value, Boolean

    def INDEX(self, other):
        return None, Null

    def HAS(self, other):
        return False, Boolean


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
            'https://github.com/aidencuneo/MDC-Lang', 'fatal')
    with open(src_path + '/startup.mdcl') as f:
        code = f.read()
    start(code)


def initialise_global_vars(file=None):
    global_vars['FILE'] = String(current_file if file is None else file)
    global_vars['LINE'] = Integer(1)
    global_vars['_'] = Null()
    global_vars[','] = Null()
    global_vars['ERR'] = Null()


def call_error(text=None, error_type=None, line=None, args=None, showfile=True):
    original_error = error_type
    if isinstance(line, (list, tuple)):
        line = ' '.join([str(a) for a in line])
    if isinstance(error_type, MDCLError):
        er = str(error_type)
        error_type = er[:er.index('::')]
        text = er[er.index('::') + 2:]
    global_vars['ERR'] = String(error_type)
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
    thisfile = os.path.abspath(current_file)
    method = []
    while thisfile.endswith('METHOD>'):
        method += [thisfile[rindex(thisfile, '\n') + 1:-7]]
        thisfile = thisfile[:rindex(thisfile, '\n') - 1:]
    if e != 'fatal':
        print('\n> ' + e + ' (' + error_type + ') ' + (
            'at file "' + thisfile + '", in ' + ', in '.join(
                method[::-1] if method else ['line ' + str(current_line)])
            if showfile else '') + (':' if text or not method else ' <'))
    if not method:
        codeline = loader.get_code('', specificline=current_line, setcode=current_code)
        if isinstance(codeline, str):
            print('  -> ' + codeline.strip())
    if line:
        print('  ~~ ' + line)
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


def pydata_to_mdcldata(pydata):
    mdcldata = {}
    for a in dir(pydata):
        name = a
        while '_' in a:
            a = list(a)
            ind = a.index('_')
            if ind + 1 < len(a):
                a[ind + 1] = a[ind + 1].upper()
            del a[ind]
            a = ''.join(a)
        cur_attr = getattr(pydata, name)
        new_attr = translate_datatypes(cur_attr, error_on_fail=False)
        if not isinstance(new_attr, type(cur_attr)):
            mdcldata[a] = new_attr
    return mdcldata


def start(rawcode, filename=None):
    try:
        run(rawcode, filename, raw=True)
    except MDCLError as e:
        call_error(error_type=e)
    except (KeyboardInterrupt, EOFError):
        sig_c.send('SIGINT')
    except RecursionError:
        call_error('Too many recursive calls in a row.', 'recursion')
    except ZeroDivisionError:
        call_error('Attemped division or modulo by zero.', 'zerodivision')
    except Exception as e:
        call_error(error_type='fatal')


def run(rawcode, filename=None, tokenised=False, oneline=False, echo=True, raw=False, yielding=False, localargs=None):
    global current_file
    global current_code
    global current_line
    global current_catch
    global local_vars
    global datatypes
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
        if not a:
            i += 1
            continue
        if a[0] == 'NEW':
            if len(a) < 4 or ':' not in a:
                call_error('Function declaration requires at least a function name, function code, and the ":" separator.', 'argerr')
            specialmethod = False
            name = a[1]
            if a[1] == '!':
                specialmethod = True
                name = '!' + a[2]
                del a[1]
            func = a[-1]
            arguments = tuple(filter(None, split_list(a[2:-1], ':')))
            types = [b.__name__ for b in builtin_types]
            optionals = False
            for b in arguments:
                for c in b:
                    if c not in types and not c == '*' and not c == '@' and not specialmethod:
                        call_error(pformat(c) + ' is not defined as a type.', 'attr')
                if '*' in b:
                    optionals = True
                elif optionals and not '*' in b:
                    call_error('Optional function arguments must be after all positional arguments.', 'syntax')
            functions[name] = Function(name, arguments, func)
        elif a[0] == 'DATATYPE':
            if len(a) < 4 or ':' not in a:
                call_error('Datatype declaration requires at least a datatype name, initialisation code, and the ":" separator.', 'argerr')
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
                    call_error('Optional initialisation function arguments must be after all positional arguments.', 'syntax')
            if name in globals() or name in locals() or name in builtin_types:
                call_error('Invalid Datatype name. Datatype name must not already be defined.', 'defined')
            exec('class ' + name + '(BaseDatatype):pass', globals())
            this = eval(name)
            actions = {b[1:] : functions[b] for b in functions if b[0] == '!' and b[1:] in mdcl_keywords + ('ECHO',)}
            if 'ECHO' not in actions:
                call_error('Datatype is missing an ECHO function.', 'attr')
            for a in actions:
                setattr(this, a, actions[a])
            def __init__(self, args):
                if not isinstance(args, (list, tuple)):
                    args = args,
                self.value = evaluate([func], args=args)
            def __repr__(self):
                return pformat(evaluate([actions['ECHO'], self]))
            this.__init__ = __init__
            this.__repr__ = __repr__
            datatypes += (this,)
            functions[name] = Function(name, arguments, this)
            del this
            del __init__
            del __repr__
        elif a[0] == 'IF':
            if len(a) < 3 or ':' not in a:
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
                    if len(con[b]) < 2 or b + 1 >= len(con):
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
                        if yielding:
                            yielded += [ev]
                        else:
                            o += str(ev)
                            if echo:
                                sys.stdout.write(str(ev))
                    break
        elif a[0] == 'WHILE':
            if len(a) < 3 or ':' not in a:
                call_error('WHILE loop requires at least a condition, the ":" separator, and code to run.', 'syntax')
            contents = tuple(filter(None, split_list(a[1:], ':')))
            if not contents[1:]:
                call_error('WHILE loop requires at least a condition, the ":" separator, and code to run.', 'syntax')
            condition = contents[0]
            runcode = contents[1]
            while Boolean(evaluate(condition, error=code[i], args=localargs)):
                ev = evaluate(runcode, error=code[i], args=localargs)
                if not isinstance(ev, Null):
                    if yielding:
                        yielded += [ev]
                    else:
                        o += str(ev)
                        if echo:
                            sys.stdout.write(str(ev))
        elif a[0] == 'FOR':
            if len(a) < 3 or ':' not in a:
                call_error('FOR loop requires at least a variable name, iterable, the ":" separator, and code to run.', 'syntax')
            contents = tuple(filter(None, split_list(a[1:], ':')))
            if not contents[1:]:
                call_error('FOR loop requires at least an iterable, the ":" separator, and code to run.', 'syntax')
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
                call_error('Invalid FOR loop variable name. FOR loop variable names can not be reserved names', 'var')
            if isinstance(iterable, Null):
                call_error('FOR loop iterable can not be NULL.', 'syntax')
            if not runcode:
                call_error('FOR loop code to run can not be empty.', 'syntax')
            if not isinstance(iterable, (Integer, String, Array)):
                call_error('FOR loop can only iterate over an Array, Integer, or String.', 'type')
            if isinstance(iterable, Integer):
                iterable = list(range(iterable.value))
            elif isinstance(iterable, String):
                iterable = Array(iterable)
            oldvariable = None
            if variable in local_vars:
                oldvariable = local_vars[variable]
            for value in translate_datatypes(iterable).value:
                if variable is not None:
                    local_vars[variable] = value
                global_vars[','] = value
                ev = evaluate(runcode, error=code[i], args=localargs)
                if not isinstance(ev, Null):
                    if yielding:
                        yielded += [ev]
                    else:
                        o += str(ev)
                        if echo:
                            sys.stdout.write(str(ev))
            if oldvariable is not None:
                local_vars[variable] = oldvariable
        elif a[0] == 'TRY':
            if len(a) < 3 or ':' not in a:
                call_error('TRY statement requires at least the ":" separator and code to run.', 'syntax')
            contents = split_list(a[1:], ':')
            runcode = contents[0]
            if not runcode:
                call_error('TRY statement code to run can not be empty.', 'syntax')
            catches = {}
            keys = []
            for b in contents[1:]:
                if b[0] == 'CATCH':
                    keys = b[1:]
                else:
                    if not keys:
                        call_error('TRY statement requires CATCH keyword before second set of code to run.', 'syntax')
                    keys = evaluate(keys, error=code[i], args=localargs)
                    if isinstance(keys, Array):
                        keys = keys.value
                    if not isinstance(keys, (tuple, list)):
                        keys = keys,
                    for c in keys:
                        if not isinstance(c, String):
                            call_error('CATCH keyword arguments must be of type String.', 'type')
                        catches[c.value] = b
                    keys = []
            if keys:
                call_error('Unfinished CATCH keyword in TRY statement')
            oldcatch = current_catch
            current_catch = catches
            try:
                ev = evaluate(runcode, error=code[i], args=localargs)
                if not isinstance(ev, Null):
                    if yielding:
                        yielded += [ev]
                    else:
                        o += str(ev)
                        if echo:
                            sys.stdout.write(str(ev))
            except MDCLError as e:
                ev = perform_try_catch(e, error=code[i], args=localargs)
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
                    if not isinstance(ev, Null):
                        if yielding:
                            yielded += [ev]
                        else:
                            o += str(ev)
                            if echo:
                                sys.stdout.write(str(ev))
            except RecursionError:
                ev = perform_try_catch(MDCLError('recursion::Too many recursive calls in a row.'), error=code[i], args=localargs)
                if not isinstance(ev, Null):
                    if yielding:
                        yielded += [ev]
                    else:
                        o += str(ev)
                        if echo:
                            sys.stdout.write(str(ev))
            except ZeroDivisionError:
                ev = perform_try_catch(MDCLError('zerodivision::Attemped division or modulo by zero.'), error=code[i], args=localargs)
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
        elif ':' in a:
            key = ''.join(a[:a.index(':')])
            if key in reserved_names:
                call_error('Invalid variable name. Variable names can not be reserved names.', 'var')
            if key in functions:
                call_error('Invalid variable name. A function exists with that name, use DEL to delete functions or variables.', 'var')
            if not re.match('^[a-zA-Z]+$', key) and key:
                call_error('Invalid variable name, variable names must fit this REGEX expression: ^[a-zA-Z]+$', 'var')
            value = evaluate(a[a.index(':') + 1:], error=code[i], args=localargs)
            if key:
                local_vars[key] = value
        elif a[0] == 'DEL':
            if len(a) < 2:
                call_error('DEL statement missing variable or key to delete.', 'argerr')
            key = ''.join(a[1:])
            if key in local_vars:
                del local_vars[key]
            elif key in functions:
                if isinstance(functions[key], BuiltinFunction):
                    call_error('DEL statement can not delete built-in functions.', 'argerr')
                del functions[key]
            elif key in global_vars:
                call_error('DEL statement can not delete global arguments.', 'argerr')
        elif a[0] == 'IMPORT':
            if len(a) < 2:
                call_error('IMPORT statement requires at least one argument.', 'argerr')
            fnames = evaluate(a[1:], error=code[i], args=localargs, funcargs=True)
            if any(not isinstance(f, String) for f in fnames):
                call_error('IMPORT statement arguments must be of type String.', 'type')
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
        elif a[0] == 'UNIMPORT':
            if len(a) < 2:
                call_error('UNIMPORT statement requires at least one argument.', 'argerr')
            fnames = evaluate(a[1:], error=code[i], args=localargs, funcargs=True)
            if any(not isinstance(f, String) for f in fnames):
                call_error('UNIMPORT statement arguments must be of type String.', 'type')
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
                    old_local_vars = copy(local_vars)
                    old_global_vars = copy(global_vars)
                    old_functions = copy(functions)
                    run(newcode, f, raw=True)
                    current_file = oldfile
                    current_code = oldcode
                    current_line = oldline
                    for d in old_local_vars:
                        if old_local_vars[d] != local_vars[d]:
                            del local_vars[d]
                    for d in old_global_vars:
                        if old_global_vars[d] != global_vars[d]:
                            del global_vars[d]
                    for d in old_functions:
                        if old_functions[d] != functions[d]:
                            del functions[d]
                    break
                else:
                    call_error('No scripts within directory ' + pformat(b.value) + ' could be unimported.', 'import')
        #elif a[0] == 'PYIMPORT':
        #    pass
            # Probably delete this
            '''if len(a) < 2:
                call_error('PYIMPORT statement requires at least one argument.', 'argerr')
            fnames = evaluate(a[1:], error=code[i], args=localargs, funcargs=True)
            if any(not isinstance(f, String) for f in fnames):
                call_error('PYIMPORT statement arguments must be of type String.', 'type')
            for fname in fnames:
                try:
                    pydata = __import__(fname.value, globals(), locals(), ['*'])
                except ImportError:
                    call_error('A Python script at relative module path ' + pformat(fname.value) + ' could not be found or imported from.', 'import')
                local_vars += pydata_to_mdcldata(pydata)'''
        elif a[0] == 'SIG':
            a = evaluate_line(a, start=2, error=code[i], args=localargs)
            if len(a) < 2:
                call_error('SIG statement requires at least a signal name.', 'argerr')
            signal_name = a[1].strip()
            if signal_name not in sig_c.switches:
                call_error('Signal ' + pformat(signal_name) + ' is not a valid signal.', 'unknownvalue')
            newvalue = not sig_c.switches[signal_name]
            if len(a) > 2:
                newvalue = Boolean(a[2]).value.value
            if not isinstance(newvalue, bool):
                call_error('SIG statement new value must evaluate to Boolean.', 'type')
            sig_c.switches[signal_name] = newvalue
        elif a[0] == 'RAISE':
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
            if not isinstance(ev, Null):
                if yielding:
                    yielded += [ev]
                else:
                    o += str(ev)
                    if echo:
                        sys.stdout.write(str(ev))
        elif a[0] == 'ERRORTAG':
            a = evaluate_line(a, start=1, error=code[i], args=localargs)
            if len(a) < 2:
                call_error('ERRORTAG statement requires at least an error type name.', 'argerr')
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
        elif a[0] == 'YIELD':
            if not yielding:
                call_error('Yielding is not possible from the current scope.', 'syntax')
            yielded += [evaluate(a[1:], error=code[i], args=localargs)]
        else:
            a = evaluate(a, error=code[i], args=localargs)
            if isinstance(a, builtin_types) and not isinstance(a, Null):
                o += str(a)
                if echo:
                    sys.stdout.write(str(a))
        i += 1
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
    if isinstance(dt, (Array, Alphabet)):
        contents = tuple(translate_datatypes(a) for a in dt.value)
        dt = type(dt)(contents)
    if isinstance(dt, datatypes + (Function,)):
        return dt
    if not (isinstance(dt, tuple) and not dotuple) and error_on_fail:
        call_error('There was an error during datatype translation for value: ' + pformat(dt) + '.', 'value')
    return dt


def eval_datatypes(exp, error=None, dostrings=False):
    if not exp:
        return exp
    new = [a for a in exp]
    a = 0
    while a < len(new):
        if isinstance(new[a], datatypes):
            a += 1
            continue
        if isinstance(new[a], str):
            if re.match('^[a-zA-Z]+\.[a-zA-Z]+$', new[a]):
                keys = new[a].split('.')
                last = None
                if keys[0] not in set(local_vars + global_vars + functions):
                    call_error('Namespace ' + pformat(keys[0]) + ' does not exist or has not been imported.', 'namespace')
                if len(keys) > 2:
                    call_error('Too many namespace calls in one expression.', 'namespace')
                if keys[1] in local_vars[keys[0]]:
                    new[a] = local_vars[keys[0]][keys[1]]
                elif keys[1] in global_vars[keys[0]]:
                    new[a] = global_vars[keys[0]][keys[1]]
                elif keys[1] in functions[keys[0]]:
                    new[a] = keys[1]
        if isinstance(new[a], tuple([b for b in datatypes_switch.keys() if dostrings or b != str])):
            new[a] = datatypes_switch[type(new[a])](new[a])
        if not isinstance(new[a], str):
            pass
        elif re.match('^RE(\'|").+(\'|")', new[a]): # Is new[a] a Regex String? If so, assign Regex() class.
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
        elif new[a] in ('TRUE', 'FALSE', 'True', 'False'): # Is new[a] a boolean? If so, assign Boolean() class.
            new[a] = Boolean(bool(new[a]))
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
        if isinstance(new[a], (Function, BuiltinFunction)):
            limit = len(new[a].args)
            f = evaluate(new[a + 1:a + 1 + limit], error=error, args=args, funcargs=True)
            if not isinstance(f, tuple):
                f = f,
            f = f[:limit]
            oldfile = current_file
            oldcode = current_code
            oldline = current_line
            current_file = current_file + '\n<' + new[a].name + 'METHOD>'
            current_code = new[a].code
            current_line = 1
            new[a] = new[a].call(f)
            current_file = oldfile
            current_code = oldcode
            current_line = oldline
            del new[a + 1:a + 1 + limit]
        if isinstance(new[a], datatypes):
            pass
        elif new[a].startswith('args[') and new[a].endswith(']'):
            key = int(new[a][5:-1])
            if args:
                if key >= len(args):
                    call_error('Local argument list index out of range, ' + str(key) + ' > ' + str(len(args) - 1) + '.',
                        'outofrange', error)
                new[a] = args[key]
            else:
                if key >= len(global_args):
                    call_error('Global argument list index out of range, ' + str(key) + ' > ' + str(len(global_args) - 1) + '.',
                        'outofrange', error)
                new[a] = global_args[key]
        elif new[a] in functions:
            limit = len(functions[new[a]].args)
            f = evaluate(new[a + 1:a + 1 + limit], error=error, args=args, funcargs=True)
            if not isinstance(f, tuple):
                f = f,
            f = f[:limit]
            oldfile = current_file
            oldcode = current_code
            oldline = current_line
            current_file = current_file + '\n<' + new[a] + 'METHOD>'
            current_code = functions[new[a]].code
            current_line = 1
            new[a] = functions[new[a]].call(f)
            current_file = oldfile
            current_code = oldcode
            current_line = oldline
            del new[a + 1:a + 1 + limit]
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


def make_evaluable(line):
    if not isinstance(line, (list, tuple)):
        line = line,
    return [
        (type(a).__name__ + '(' + (
            make_evaluable(a.value)[0]
            if isinstance(a.value, datatypes)
            else pformat(a)
        ) + ')')
        if isinstance(a, datatypes)
        else a for a in line
        if a is not None
    ]


def evaluate(exp, error=None, args=None, funcargs=False):
    if not exp:
        return Null()
    reps = {
        '+': 'ADD',
        '-': 'SUB',
        '*': 'MULT',
        '/': 'DIV',
        '^': 'PWR',
        '%': 'MOD',
        '=': 'EQ',
        '|': 'INDEX',
    }
    new = [a for a in exp]
    new = eval_functions(eval_datatypes(new, error=error), error=error, args=args)
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
                settype = vals[1] if isinstance(vals, tuple) else type(new[a - 1])
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
                settype = vals[1] if isinstance(vals, tuple) else type(new[a - 1])
                new[a] = settype(vals[0] if isinstance(vals, tuple) else vals)
                del new[a - 1]
                a -= 1
        elif new[a] == '.':
            pass
            # Perform gettattr.
            # Get right hand argument from left hand argument.
            # Equivalent to left_hand.right_hand
            # Right hand argument should not be String,
            # it should be a regular word.
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
            right = evaluate_line(new, start=a + 1, error=error, args=args)[a + 1]#evaluate(replacekeys([new[a + 1]], args=args), error=error, args=args)
            new[a] = Boolean(Boolean(left) or Boolean(right))
            del new[a + 1]
            del new[a - 1]
            a -= 1
        elif new[a] == 'ONLY':
            if a - 1 < 0:
                call_error('ONLY requires a left hand argument.', 'argerr', error)
            if a + 1 >= len(new):
                call_error('ONLY requires a right hand argument.', 'argerr', error)
            argument = evaluate(replacekeys([new[a - 1]], args=args), error=error, args=args)
            if not isinstance(argument, (Integer, String, Array)):
                call_error('The ONLY keyword can only iterate over an Array, Integer, or String.', 'type')
            if isinstance(argument, Integer):
                argument = range(argument.value)
            else:
                argument = argument.value
            runcode = new[a + 1].strip()[1:-1].strip()
            output = []
            for value in argument:
                value = run(runcode, filename='keep', echo=False, raw=True, yielding=True, localargs=[value])
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
            if a > 0:
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
            value = run(new[a].strip()[1:-1].strip(), filename='keep', echo=True, raw=True, yielding=True, localargs=args)
            new[a] = Array(value)
            if not value:
                new[a] = Null()
            elif len(value) == 1:
                new[a] = value[0]
        elif new[a].startswith('(') or new[a].endswith(')'):
            if not new[a].startswith('('):
                call_error('Unmatched ' + pformat('(') + '.', 'syntax')
            if not new[a].endswith(')'):
                call_error('Unmatched ' + pformat(')') + '.', 'syntax')
            new[a] = Slice(new[a])
            a -= 1
        elif new[a] == 'ARRAY':
            contents = new[a + 1] if a < len(new) - 1 else []
            if contents:
                contents = evaluate(replacekeys([new[a + 1]], args=args), error=error, args=args)
            if not isinstance(contents, (tuple, list, String, Array, Alphabet)):
                contents = (contents,)
            new[a] = translate_datatypes(contents)
            if a < len(new) - 1:
                del new[a + 1]
        elif new[a] == 'ALPHABET':
            contents = new[a + 1] if a < len(new) - 1 else []
            if contents:
                contents = evaluate(replacekeys([new[a + 1]], args=args), error=error, args=args)
            if not isinstance(contents, (tuple, list, String, Array, Alphabet)):
                pass
            new[a] = Alphabet(contents)
            if a < len(new) - 1:
                del new[a + 1]
        elif new[a] in local_vars:
            new[a] = local_vars[new[a]]
        elif new[a] in global_vars:
            new[a] = global_vars[new[a]]
        elif new[a] in reserved_names:
            call_error('Invalid syntactical usage of reserved name.', 'syntax')
        elif new[a] not in functions:
            token = new[a]
            if len(token) > 100:
                token = token[:97] + '...'
            call_error('Undefined Token: ' + pformat(token), 'syntax', error)
        a += 1
    code = ','.join(make_evaluable(new))
    out = code
    if code and code != ',':
        try:
            out = eval(code)
            out = translate_datatypes(out, dotuple=not funcargs)
            if funcargs and not isinstance(out, tuple):
                out = out,
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
                    call_error('Local argument list index out of range, ' + str(key) + ' > ' + str(len(args) - 1) + '.', 'outofrange', line)
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
        if isinstance(args[0], (Array, Alphabet)):
            content = String(sep.value.join([str(a) for a in content.value]))
        elif isinstance(args[0], str):
            content = String(content)
        print(content.value, end=end.value)
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
    def get_functions(args):
        return Array(list(functions.keys()))

    @staticmethod
    def get_argv(args):
        if isinstance(args[0], Integer):
            if args[0].value < len(global_args):
                return global_args[args[0].value]
        return Array(global_args)


#
# VARIABLES
#

sig_c = SignalCatches()

current_file = ''
current_code = ''
current_line = 1
current_catch = {}

reserved_names = (
    'FILE',
    'LINE',
    '_',
    ',',
    'ERR',
    'PATH',

    'NEW',
    'IF',
    'ELIF',
    'ELSE',
    'WHILE',
    'FOR',
    'TRY',
    'CATCH',
    ':',
    'DEL',
    'IMPORT',
    'PYIMPORT',
    'UNIMPORT',
    'DEFINE', # Remake define statement.
    'SIG',
    'RAISE',
    'ERRORTAG',
    'YIELD',

    'ADD',
    'SUB',
    'MULT',
    'DIV',
    'PWR',
    'MOD',
    'EQ',
    'LT',
    'GT',
    'LE',
    'GE',
    'INDEX',
    'HAS',

    '+',
    '-',
    '*',
    '/',
    '^',
    '%',
    '=',
    '|',

    'AND',
    'OR',
    'ONLY',
    'TO',
    'SKIP',
    'ARRAY',
    'ALPHABET',

    'INTEGER',
    'FLOAT',
    'STRING',
    'REGEX',
    'TIMER',
    'BOOLEAN',
    'NULL',

    'READ',
    'LEN',
    'READFILE',
    'WRITEFILE',
    'TYPE',
    'ECHO',
    'WAIT',
    'GLOBALS',
    'LOCALS',
    'FUNCTIONS',
    'ARGV',

    'NOT',

    'EXIT',
)

mdcl_keywords = (
    'ADD',
    'SUB',
    'MULT',
    'DIV',
    'PWR',
    'MOD',
    'EQ',
    'LT',
    'GT',
    'LE',
    'GE',
    'INDEX',
    'HAS',
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
    set: Alphabet,
    type(None): Null,
}
builtin_types = tuple(set(datatypes_switch.values())) + (
    RegexString,
    Slice,
)

datatypes = copy(builtin_types)
local_vars = CompactDict()
global_vars = CompactDict()
global_args = [String(a) for a in sys.argv[1:]]

functions = {
    'INTEGER': BuiltinFunction('INTEGER',
        [['@', '*']],
        Integer),
    'FLOAT': BuiltinFunction('FLOAT',
        [['@', '*']],
        Float),
    'STRING': BuiltinFunction('STRING',
        [['@', '*']],
        String),
    'REGEX': BuiltinFunction('REGEX',
        [[String, '*']],
        RegexString),
    'TIMEDELTA': BuiltinFunction('TIMEDELTA',
        [['@', '*']],
        Timedelta),
    'DATE': BuiltinFunction('DATE',
        [['@', '*']],
        Date),
    'SLICE': BuiltinFunction('SLICE',
        [['@', '*']],
        Slice),
    'BOOLEAN': BuiltinFunction('BOOLEAN',
        [['@', '*']],
        Boolean),
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
    'WRITEFILE': BuiltinFunction('WRITEFILE',
        [[String], [String]],
        BFList.writefile),
    'TYPE': BuiltinFunction('TYPE',
        [['@']],
        BFList.get_type),
    'ECHO': BuiltinFunction('ECHO',
        [['@'], ['*', String], ['*', String]],
        BFList.echo),
    'WAIT': BuiltinFunction('WAIT',
        [[Integer, Float]],
        BFList.wait),
    'GLOBALS': BuiltinFunction('GLOBALS',
        [],
        BFList.get_globals),
    'LOCALS': BuiltinFunction('LOCALS',
        [],
        BFList.get_locals),
    'FUNCTIONS': BuiltinFunction('FUNCTIONS',
        [],
        BFList.get_functions),
    'ARGV': BuiltinFunction('ARGV',
        [[Integer, '*']],
        BFList.get_argv),

    'NOT': BuiltinFunction('NOT',
        [['@']],
        lambda x: Boolean(not x.value)),

    'EXIT': BuiltinFunction('EXIT',
        [],
        lambda x: (String(''), sys.exit())[0]),
}
