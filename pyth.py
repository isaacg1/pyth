#!/usr/bin/python3
############################################################################
# This python program is an interpreter for the pyth programming language. #
# It is still in development - expect new versions often.                  #
#                                                                          #
# To use, provide pyth code as first command line argument.                #
# Further input on further lines.                                          #
# Prints out resultant python code for debugging purposes, then runs the   #
# pyth program.                                                            #
#                                                                          #
# More information:                                                        #
# The parse function takes a string of pyth code, and returns a single     #
# python expression ready to be executed.                                  #
# general_parse is the same but for multiple expressions.                  #
# This program also defines the built-ins that the resultant expression    #
# uses, once expanded.                                                     #
############################################################################


def parse(code, spacing="\n "):
    assert isinstance(code, str)
    # If we've reached the end of the string, give up.
    if len(code) == 0:
        return '', ''
    # Separate active character from the rest of the code.
    active_char = code[0]
    rest_code = code[1:]
    # Deal with numbers
    if active_char in ".0123456789":
        return num_parse(active_char, rest_code)
    # String literals
    if active_char == '"':
        return str_parse(active_char, rest_code)
    # Python code literals
    if active_char == '$':
        return python_parse(active_char, rest_code)
    # End paren is magic (early-end current function/statement).
    if active_char == ')':
        return '', rest_code
    # Backslash is more magic (early-end all active functions/statements).
    if active_char == ';':
        if rest_code == '':
            return '', ''
        else:
            return '', ';'+rest_code
    # Designated variables
    if active_char in variables:
        return active_char, rest_code
    # Replace replaements
    if active_char in replacements:
        return replace_parse(active_char, rest_code)
    # And for general functions
    global c_to_f
    global next_c_to_f
    if active_char in c_to_f:
        func_name, arity = c_to_f[active_char]
        init_paren = (active_char not in no_init_paren)
        # Swap what variables are used in the map, filter or reduce.
        if active_char in next_c_to_f:
            temp = c_to_f[active_char]
            c_to_f[active_char] = next_c_to_f[active_char][0]
            next_c_to_f[active_char] = next_c_to_f[active_char][1:] + [temp]
        # Recurse until terminated by end paren or EOF
        # or received enough arguments
        args_list = []
        parsed = 'Not empty'
        while len(args_list) != arity and parsed != '':
            parsed, rest_code = parse(rest_code)
            args_list.append(parsed)
        # Build the output string.
        py_code = func_name
        if init_paren:
            py_code += '('
        if len(args_list) > 0 and args_list[-1] == '':
            args_list = args_list[:-1]
        py_code += ','.join(args_list)
        py_code += ')'
        return py_code, rest_code
    # General format functions/operators
    global c_to_i
    if active_char in c_to_i:
        infixes, arity = c_to_i[active_char]
        # Make J and K into normal variables, if necessary.
        if active_char in next_c_to_i:
            c_to_i[active_char] = next_c_to_i[active_char]
        args_list = []
        parsed = 'Not empty'
        while len(args_list) != arity and parsed != '':
            parsed, rest_code = parse(rest_code)
            args_list.append(parsed)
        # Statements that cannot have anything after them
        if active_char in end_statement:
            rest_code = ")" + rest_code
        py_code = infixes[0]
        for i in range(len(args_list)):
            py_code += args_list[i]
            py_code += infixes[i+1]
        return py_code, rest_code
    # Statements:
    if active_char in c_to_s:
        # Handle the initial portion (head)
        infixes, arity = c_to_s[active_char]
        args_list = []
        parsed = 'Not empty'
        while len(args_list) != arity and parsed != '':
            parsed, rest_code = parse(rest_code)
            args_list.append(parsed)
        part_py_code = infixes[0]
        for i in range(len(args_list)):
            part_py_code += args_list[i]
            part_py_code += infixes[i+1]
        # Handle the body - ends object as well.
        assert rest_code != ''
        args_list = []
        parsed = 'Not empty'
        while parsed != '':
            # Prepend print to any line starting with a function, var or
            # safe infix.
            if len(rest_code) > 0:
                if ((rest_code[0] not in 'p ' and rest_code[0] in c_to_f) or
                    rest_code[0] in "\\" or
                    rest_code[0] in variables or
                    rest_code[0] in "@&|]'?;\".0123456789#,Q" or
                    (rest_code[0] in 'JK' and
                        c_to_i[rest_code[0]] == next_c_to_i[rest_code[0]])):
                    rest_code = 'p"\\n"' + rest_code
            parsed, rest_code = parse(rest_code, spacing+' ')
            args_list.append(parsed)
        # Trim the '' away and combine.
        if args_list[-1] == '':
            args_list = args_list[:-1]
        # Special bit for repeat ... until loops.
        if active_char == 'U':
            header = spacing[:-1].join(args_list+[part_py_code])
            all_pieces = [header]+args_list
        else:
            all_pieces = [part_py_code] + args_list
        return spacing.join(all_pieces), rest_code
    print("Something's wrong.")
    print("Current char is ", active_char)
    print("The rest of the code is ", rest_code)
    raise NotImplementedError


def num_parse(active_char, rest_code):
    output = active_char
    while len(rest_code) > 0 \
        and rest_code[0] in ".0123456789" \
        and (output+rest_code[0]).count(".") <= 1:
        output += rest_code[0]
        rest_code = rest_code[1:]
    return output, rest_code


def str_parse(active_char, rest_code):
   output = active_char
   while len(rest_code) > 0 and output.count('"') < 2:
       output += rest_code[0]
       rest_code = rest_code[1:]
   if output[-1] != '"':
       output += '"'
   return output, rest_code


def python_parse(active_char, rest_code):
        output = ''
        while (len(rest_code) > 0
               and rest_code[0] != '$'):
            output += rest_code[0]
            rest_code = rest_code[1:]
        return output, rest_code[1:]

def replace_parse(active_char, rest_code):
    format_str, format_num = replacements[active_char]
    format_chars = tuple(rest_code[:format_num])
    new_code = format_str.format(*format_chars) + rest_code[format_num:]
    return parse(new_code, spacing)
import copy
import math
import random
import re
import string
import sys


# Function library. See later for letter -> function correspondences.
# !. All.
def _not(a):
    return not a


# %. int, str.
def mod(a, b):
    return a % b


# *. int, str, list.
def times(a, b):
    return a*b


# (. All types
def _tuple(*a):
    return a


# -. int, set.
def minus(a, b=None):
    if isinstance(a, int):
        return a-b
    difference = filter(lambda c: c not in b, a)
    if isinstance(a, str):
        return ''.join(difference)
    if isinstance(a, list):
        return list(difference)
    else:
        return set(difference)


# '. single purpose.
def read_file():
    a = "\n".join(open(input()))
    return a


# _. All.
def neg(a):
    if isinstance(a, int):
        return -a
    else:
        return a[::-1]


# +. All.
def plus(a, b):
    if isinstance(a, set):
        return a.union(b)
    if isinstance(b, set):
        return b.union(a)
    return a+b


# =. All.
copy = copy.deepcopy


# [. All.
def _list(*a):
    return list(a)


# :. list.
def at_slice(a, b, c=None):
    if c:
        return a[slice(b, c)]
    else:
        return a[slice(b)]



# <. All.
def lt(a, b):
    if isinstance(a, set):
        return a.issubset(b) and a != b
    return a < b


# >. All.
def gt(a, b):
    if isinstance(a, set):
        return a.issuperset(b) and a != b
    return a > b


# /. All.
def div(a, b):
    if isinstance(a, int):
        return a // b
    return a.count(b)


# a. All
def _and(a, b):
    if isinstance(a, int):
        return a&b
    else:
        intersection = set(a) & set(b)
        if isinstance(a, str):
            return str(intersection)
        if isinstance(a, list):
            return list(intersection)
        else:
            return intersection
b = "\n"


# c. All
def chop(a, b=None):
    if isinstance(a, int):
        return a/b
    if isinstance(b, str):
        return a.split(b)
    if b is None:
        return a.split()
    return list(map(lambda d: a[b*d:b*(d+1)], range(math.ceil(len(a)/b))))



# C. int, str.
def _chr(a):
    if isinstance(a, int):
        return chr(a)
    if isinstance(a, str):
        return ord(a[0])


d = ' '


# e. All.
def end(a):
    if isinstance(a, int):
        return a%10
    return a[-1]


# f. single purpose.
def _filter(a, b):
    return list(filter(a, b))
G = string.ascii_lowercase


# g. All.
def gte(a, b):
    if isinstance(a, set):
        return a.issuperset(b)
    return a >= b
H = {}


# h. int, str, list.
def head(a):
    if isinstance(a, int):
        return a+1
    return a[0]


# i. int, str
def int_2(a, b=0):
    if not b:
        return float(a)
    return int(a, b)


# j. str.
def join(a, b):
    return a.join(list(map(lambda N: str(N), b)))
k = ''


# m. Single purpose.
def _map(a, b):
    return list(map(a, b))


# M. str, list.
def move_slice(a, b, c=None):
    if not c:
        return a[slice(0, b)]
    else:
        return a[slice(b, b+c)]
N = ","


# n. All.
def ne(a, b):
    return a != b
    

# O. int, str, list
def rchoice(a):
    if isinstance(a, int):
        return random.choice(_range(a))
    return random.choice(list(a))


# o. Single purpose.
def order(a, b):
    if isinstance(a, str):
        return ''.join(sorted(b, key=a))
    return sorted(b, key=a)


def isprime(num):
    return all(num % div != 0 for div in range(2, int(num**.5 +1)))


# P. str.
def primes_upper(a):
    if isinstance(a, int):
        working = a
        output = []
        for num in filter(isprime, range(2, int(a**.5 + 1))):
            while working%num == 0:
                output.append(num)
                working//=num
        if working != 1:
            output.append(working)
        return output
    return a.upper()


# p. All.
def _print(a, b=""):
    print(b, end=a)
# Q. Unimplemented.


# q. All.
def equal(a, b):
    return a == b


# r. int.
def _range(a, b=None):
    if b:
        if a < b:
            return list(range(a, b))
        else:
            return list(range(b, a))[::-1]
    else:
        return list(range(a))


# s. int, str, list.
def _sum(a):
    if isinstance(a, list):
        return reduce(lambda b, c: b+c, a)
    else:
        return int(a)
T = 10


# t. int, str, list.
def tail(a):
    if isinstance(a, int):
        return a-1
    return a[1:]


# u. single purpose
def reduce(a, b):
    acc = b[0]
    seq = b[1:]
    while len(seq) > 0:
        h = seq[0]
        acc = a(acc, h)
        seq = seq[1:]
    return acc


# V. int, str, list.
def urange(a):
    if isinstance(a, int):
        return list(range(a))
    return list(range(len(a)))


# x. str, list.
def index(a, b):
    if b in a:
        return a.index(b)
    # replicate functionality from str.find
    else:
        return -1


def space_sep(a):
    return [eval(bit) for bit in a.split()]
Y = []
Z = 0


no_init_paren = 'fmou'
end_statement = 'BR'
variables = 'bdGHkNTYZ'

# To do: even preassociated variables deserve to be initialiZed.
# Variables cheat sheet:
# b = "\n"
# d is for map, d=' '
# G is for reduce, G=string.ascii_lowercase (abc..xyz)
# H is for reduce, H = {}
# k = ''
# J - Autoinitializer - copies, no stringing.
# K - Autoinitializer - can be strung (KJw), no copy.
# N = None, second option variable for map,filter,reduce
# T is for filter, second variable option for reduce, T=10
# Y = []
# Z = 0

c_to_s = {
    'D': (('def ', ':'), 1),
    'E': (('else:', ), 0),
    'F': (('for ', ' in ', ':'), 2),
    'I': (('if ', ':'), 1),
    'W': (('while ', ':'), 1),
    }
# Arbitrary format operators - use for assignment, infix, etc.
# All surrounding strings, arity
c_to_i = {
    '~': (('', '+=', ''), 2),
    '@': (('', '[', ']'), 2),
    '&': (('(', ' and ', ')'), 2),
    '|': (('(', ' or ', ')'), 2),
    '=': (('', '=copy(', ')'), 2),
    ']': (('[', ']'), 1),
    '}': (('(', ' in ', ')'), 2),
    '?': (('(', ' if ', ' else ', ')'), 3),
    ',': (('(', ',', ')'), 2),
    'B': (('break', ), 0),
    'J': (('J=copy(', ')'), 1),
    'K': (('K=', ''), 1),
    'L': (('def space_sep(b): return ', ''), 1,),
    'R': (('return ', ''), 1),
    'Q': (('Q=copy(', ')'), 1),
    'X': (('exec(general_parse(','))'), 1),
    'z': (('z=copy(', ')'), 1),
    }

# Simple functions only.
# Extensible is allowed, nothing else complicated is.
# -1 means extensible
# name,arity
c_to_f = {
    '`': ('repr', 1),
    '!': ('_not', 1),
    '%': ('mod', 2),
    '^': ('pow', 2),
    '*': ('times', 2),
    '(': ('_tuple', -1),
    '-': ('minus', 2),
    '_': ('neg', 1),
    '+': ('plus', 2),
    '[': ('_list', -1),
    '{': ('set', 1),
    "'": ('read_file', 0),
    ':': ('at_slice', 3),
    '<': ('lt', 2),
    '>': ('gt', 2),
    '/': ('div', 2),
    ' ': ('', 1),
    '\t': ('', 1),
    '\n': ('', 1),
    'A': ('re.sub', 3),
    'a': ('_and', 2),
    'C': ('_chr', 1),
    'c': ('chop', 2),
    'e': ('end', 1),
    'f': ('_filter(lambda T:', 2),
    'g': ('gte', 2),
    'h': ('head', 1),
    'i': ('int_2', 2),
    'j': ('join', 2),
    'l': ('len', 1),
    'M': ('move_slice', 3),
    'm': ('_map(lambda d:', 2),
    'n': ('ne', 2),
    'O': ('rchoice', 1),
    'o': ('order(lambda N:', 2),
    'P': ('primes_upper', 1),
    'p': ('_print', 2),
    'q': ('equal', 2),
    'r': ('_range', 2),
    'S': ('sorted', 1),
    's': ('_sum', 1),
    't': ('tail', 1),
    'U': ('urange', 1),
    'u': ('reduce(lambda G, H:', 2),
    'v': ('eval', 1),
    'w': ('input', 0),
    'x': ('index', 2),
    'y': ('space_sep', 1),
    }

replacements = {
    '\\': ('"{0}"', 1),
    'V': ('FNU', 0),
    }

# Gives next function header to use - for filter, map, reduce.
# map: d, k, b
# filter: T, Y, Z
# order: N, Z,
# reduce: (G,H), (N,T)

next_c_to_f = {
    'f': [('_filter(lambda Y:', 2), ('_filter(lambda Z:', 2), ],
    'm': [('_map(lambda k:', 2), ('_map(lambda b:', 2), ],
    'o': [('order(lambda Z:', 2), ],
    'u': [('reduce(lambda N,T:', 2), ],
    }

# For autoinitializers. One shot, not rotating.
next_c_to_i = {
    'J': (('J'), 0),
    'K': (('K'), 0),
    'L': (('def all(Z): return ', ''), 1),
    'Q': (('Q'), 0),
    'z': (('z'), 0),
    }

# Prependers.
prepend = {
    'Q': "Qvw",
    'z': "zw",
    }

assert set(c_to_f.keys()) & set(c_to_i.keys()) == set()


# Run it!
def general_parse(code):
    # Prependers are magic. Automatically prepend to program if present.
    # First occurance must not be in a string.
    for prep_char in prepend:
        if prep_char in code:
            first_loc = code.index(prep_char)
            if first_loc == 0 or \
                code[:first_loc].count('"') % 2 == 0 and \
                code[first_loc-1] != "\\":
                code = prepend[prep_char] + code
    args_list = []
    parsed = 'Not empty'
    while parsed != '':
        # Prepend print to any line starting with a function, var or
        # safe infix.
        if len(code) > 0:
            if ((code[0] not in 'p ' and code[0] in c_to_f) or
                code[0] in variables or
                code[0] in "@&|]'?;\".0123456789#," or
                ((code[0] in 'JK' or code[0] in prepend) and
                    c_to_i[code[0]] == next_c_to_i[code[0]])):
                    code = 'p"\\n"'+code
        parsed, code = parse(code)
        # Necessary for backslash not to infinite loop
        if code and code[0] == ';':
            code = code[1:]
        args_list.append(parsed)
    # Build the output string.
    py_code = '\n'.join(args_list[:-1])
    return py_code
# Check for command line flags.
# If debug is on, print code, python code, separator.
# If help is on, print help message.
if len(sys.argv) > 1 and "-h" in sys.argv[1:] or "--help" in sys.argv[1:]:
    print("""This is the Pyth -> Python compliler and executor.
Give file containing Pyth code as final command line argument.

Command line flags:
-c or --code to give code as final command argument, instead of file name.
-d or --debug to show input code, generated python code.
-h or --help to show this help message.""")
else:
    if len(sys.argv) > 1 and "-c" in sys.argv[1:] \
        or "--code" in sys.argv[1:] \
        or "-cd" in sys.argv[1:] \
        or "-dc" in sys.argv[1:]:
        code = sys.argv[-1]
        py_code = general_parse(code)
    else:
        code = list(open(sys.argv[-1]))[0][:-1]
        py_code = general_parse(code)
    if len(sys.argv) > 1 and "-d" in sys.argv[1:] \
    or "--debug" in sys.argv[1:] \
    or "-cd" in sys.argv[1:] \
    or "-dc" in sys.argv[1:]:
        print('='*50)
        print(code)
        print('='*50)
        print(py_code)
        print('='*50)
    exec(py_code)
