import binascii
import cmath
import collections
import copy
import datetime
import fractions
import functools
import hashlib
import itertools
import math
import numbers
import operator
import random
import re
import string
import sys
import time
import urllib.request
from ast import literal_eval
import zlib

from data import c_to_f

# Type checking
def is_num(a):
    return isinstance(a, numbers.Number)


def is_seq(a):
    return isinstance(a, collections.Sequence)


def is_col(a):
    return isinstance(a, collections.Iterable)


def is_hash(a):
    return isinstance(a, collections.Hashable)


def is_lst(a):
    return isinstance(a, list) or isinstance(a, tuple)


# Error handling
class BadTypeCombinationError(Exception):

    def __init__(self, func, *args):
        self.args = args
        self.func = func

    def __str__(self):
        error_message = "\nError occured in function: %s" % self.func
        for i in range(len(self.args)):
            arg = self.args[i]
            arg_type = str(type(arg)).split("'")[1]
            error_message += "\nArg %d: %r, type %s." % (i + 1, arg, arg_type)
        return error_message


# Itertools type normalization
def itertools_norm(func, a, *args, **kwargs):
    if isinstance(a, str):
        return ["".join(group) for group in func(a, *args, **kwargs)]
    if isinstance(a, set):
        return [set(group) for group in func(a, *args, **kwargs)]
    else:
        return [list(group) for group in func(a, *args, **kwargs)]


def unknown_types(func, name, *args):
    if len(args) == 1:
        a, = args
        if is_seq(a) and not (isinstance(a, str) and len(a) == 1):
            return list(map(func, a))
    if len(args) == 2:
        a, b = args
        if is_seq(a) and not (isinstance(a, str) and len(a) == 1):
            return list(map(lambda left:func(left, b), a))
        elif is_seq(b) and not (isinstance(b, str) and len(b) == 1):
            return list(map(lambda right:func(a, right), b))
    raise BadTypeCombinationError(name, *args)

# The environment in which the generated Python code is run.
# All functions and all variables must be added to it.
environment = {}


# Infinite Iterator. Used in .f, .V
def infinite_iterator(start):
    def successor(char):
        if char.isalpha():
            if char == 'z':
                return 'a', True
            if char == 'Z':
                return 'A', True
            return chr(ord(char) + 1), False
        elif char.isdigit():
            if char == '9':
                return '0', True
            return chr(ord(char) + 1), False
        else:
            return chr(ord(char) + 1), False

    if is_num(start):
        while True:
            yield start
            start += 1

    # Replicates the behavior of ruby's .succ
    if isinstance(start, str):
        while True:
            yield start
            alphanum_locs = [loc for loc in range(len(start))
                             if start[loc].isalnum() and ord(start[loc]) < 128]
            if alphanum_locs:
                locs = alphanum_locs[::-1]
            elif start:
                locs = range(len(start))[::-1]
            else:
                locs = []
                succ_char = 'a'
            for inc_loc in locs:
                inc_char = start[inc_loc]
                succ_char, carry = successor(inc_char)
                start = start[:inc_loc] + succ_char + start[inc_loc + 1:]
                if not carry:
                    break
            else:
                start = succ_char + start

    raise BadTypeCombinationError("infinite_iterator, probably .V", start)
environment['infinite_iterator'] = infinite_iterator


# memoizes function calls, key = repr of input.
class memoized(object):

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        args_repr = repr(args)
        if args_repr in self.cache:
            return self.cache[args_repr]
        else:
            value = self.func(*args)
            self.cache[args_repr] = value
            return value
environment['memoized'] = memoized


# If argument is a number, turn it into a range.
def num_to_range(arg):
    if isinstance(arg, int) and arg > 0:
        return range(arg)
    if is_num(arg):
        return urange(arg)

    return arg
environment['num_to_range'] = num_to_range


# Implicit print
def imp_print(a):
    if a is not None:
        print(a)
    return a
environment['imp_print'] = imp_print


# F on unary function. Repeated application.
def repeat(func, start, repetitions):
    if not isinstance(repetitions, int):
        raise BadTypeCombinationError("F", repetitions, start)
    value = start
    for _ in range(repetitions):
        value = func(value)
    return value
environment['repeat'] = repeat


# F on binary function. Fold.
def fold(func, lst):
    if func == environment[c_to_f['*'][0]]:
        if not lst:
            return 1
        if not is_col(lst): 
            return factorial(lst)
    if not lst:
        if func == environment[c_to_f['+'][0]]:
            return []
        else:
            return 0
    return reduce2(func, lst)
environment['fold'] = fold


# Lookup from the environment, ignoring lambdas.
def env_lookup(var):
    return environment[var]
environment['env_lookup'] = env_lookup


# Function library. See data for letter -> function correspondences.
# =. N/A
def assign(a, b):
    if isinstance(a, str):
        if len(a) == 1:
            environment[a] = copy.deepcopy(b)
            return environment[a]
        else:
            var_names = a.strip('[]').split(',')
            if is_seq(b) and len(var_names) == len(b) == 2 and \
                    all(len(var_name) == 1 for var_name in var_names):
                output = []
                for var_name, item in zip(var_names, b):
                    environment[var_name] = copy.deepcopy(item)
                    output.append(environment[var_name])
                return output
    raise BadTypeCombinationError("=", a, b)
environment['assign'] = assign


# ~. N/A
def post_assign(a, b):
    if isinstance(a, str):
        if len(a) == 1:
            old_a = environment[a]
            environment[a] = copy.deepcopy(b)
            return old_a
    raise BadTypeCombinationError("~", a, b)
environment['post_assign'] = post_assign


# !. All.
def Pnot(a):
    return not a
environment['Pnot'] = Pnot


# @.
def lookup(a, b):
    if is_num(a) and is_num(b):
        return a ** (1 / b)
    if isinstance(a, dict):
        if isinstance(b, list):
            b = tuple(b)
        return a[b]
    if is_seq(a) and isinstance(b, int):
        return a[b % len(a)]
    if is_col(a) and is_col(b):
        if isinstance(a, str):
            intersection = [b_elem for  b_elem in b
                            if isinstance(b_elem, str) and b_elem in a]
        else:
            intersection = [b_elem for b_elem in b if b_elem in a]
        if isinstance(a, str):
            return ''.join(intersection)
        if isinstance(a, set):
            return set(intersection)
        else:
            return list(intersection)
    return unknown_types(lookup, "@", a, b)
environment['lookup'] = lookup


# %. int, str.
def mod(a, b):
    if isinstance(a, int) and is_seq(b):
        return b[::a]
    if isinstance(a, complex) and is_num(b):
        return (a.real % b) + (a.imag % b) * 1j
    if is_num(a) and is_num(b):
        return a % b
    if isinstance(a, str):
        if is_lst(b):
            return a % tuple(b)
        else:
            return a % b
    return unknown_types(mod, "%", a, b)
environment['mod'] = mod


# ^. int, str, list.
def Ppow(a, b):
    if is_num(a) and is_num(b):
        return pow(a, b)
    if is_col(a) and isinstance(b, int):
        return itertools_norm(itertools.product, a, repeat=b)

    return unknown_types(Ppow, "^", a, b)
environment['Ppow'] = Ppow


# *. int, str, list.
def times(a, b):
    if is_col(a) and is_col(b):
        prod = list(itertools.product(a, b))
        if isinstance(a, str) and isinstance(b, str):
            return[''.join(pair) for pair in prod]
        else:
            return [list(pair) for pair in prod]
    if is_num(a) and is_num(b):
        return a * b
    if isinstance(a, int) and is_seq(b):
        return a * b
    if is_seq(a) and isinstance(b, int):
        if b < 0:
            return -b * a[::-1]
        else:
            return a * b
    return unknown_types(times, "*", a, b)
environment['times'] = times


# (. All types
def Ptuple(*a):
    return a
environment['Ptuple'] = Ptuple


# -. int, set.
def minus(a, b):
    if is_num(a) and is_num(b):
        return a - b
    if is_num(a) and is_col(b):
        if isinstance(b, str):
            return minus(str(a), b)
        if is_lst(b):
            return minus([a], b)
        if isinstance(b, set):
            return minus({a}, b)
    if is_num(b) and is_col(a):
        if isinstance(a, str):
            return minus(a, str(b))
        if is_lst(a):
            return minus(a, [b])
        if isinstance(a, set):
            return minus(a, {b})
    if is_col(a) and is_col(b):
        if isinstance(b, str):
            difference = [c for c in a if not isinstance(c, str) or c not in b]
        else:
            difference = [c for c in a if c not in b]
        if isinstance(a, str):
            return ''.join(difference)
        if is_lst(a):
            return list(difference)
        if isinstance(a, set):
            return set(difference)
    return unknown_types(minus, "-", a, b)
environment['minus'] = minus


# '. str.
def read_file(a):
    if isinstance(a, str):
        if any(a.lower().endswith("." + i) for i in
               ["png", "jpg", "jpeg", "gif", "svg", "ppm", "pgm", "pbm"]):
            from PIL import Image
            img = Image.open(a)
            data = list(img.getdata())

            # If alpha all 255, take out alpha
            if len(data[0]) > 3 and all(i[3] == 255 for i in data):
                data = [i[:3] for i in data]

            # Check grayscale
            if all(i.count(i[0]) == len(i) for i in data):
                data = [i[0] for i in data]

            data = chop(data, img.size[0])
            return data

        if a.startswith("http"):
            b = list(map(str, urllib.request.urlopen(a)))
        else:
            b = open(a)

        b = [lin[:-1] if lin[-1] == '\n' else lin for lin in b]
        return b

    return unknown_types(read_file, "'", a)
environment['read_file'] = read_file


# _. All.
def neg(a):
    if is_num(a):
        return -a
    if is_seq(a):
        return a[::-1]
    if isinstance(a, dict):
        return {value: key for key, value in a.items()}
    return unknown_types(neg, "_", a)
environment['neg'] = neg


# {. All.
def uniquify(a):
    if is_seq(a):
        try:
            seen = set()
            out = []
            for elem in a:
                if not elem in seen:
                    out.append(elem)
                    seen.add(elem)
        except TypeError:
            out = []
            for elem in a:
                if not elem in out:
                    out.append(elem)
        if isinstance(a, str):
            return ''.join(out)
        return out
    if is_col(a):
        return sorted(a)
    return unknown_types(uniquify, '{', a)
environment['uniquify'] = uniquify


# }. in
def Pin(a, b):
    if isinstance(a, int) and isinstance(b, int):
        if a < b:
            return list(range(a, b + 1))
        return list(range(b, a + 1))[::-1]
    if is_col(b):
        return a in b
    return unknown_types(Pin, '}', a, b)
environment['Pin'] = Pin


# +. All.
def plus(a, b):
    if isinstance(a, set):
        if is_col(b):
            return a.union(b)
        else:
            return a.union({b})
    if is_lst(a) and not is_lst(b):
        return list(a) + [b]
    if is_lst(b) and not is_lst(a):
        return [a] + list(b)
    if is_lst(a) and is_lst(b):
        return list(a) + list(b)
    if is_num(a) and is_num(b) or\
            isinstance(a, str) and isinstance(b, str):
        return a + b
    if is_num(a) and isinstance(b, str):
        return str(a) + b
    if isinstance(a, str) and is_num(b):
        return a + str(b)
    return unknown_types(plus, "+", a, b)
environment['plus'] = plus


# [. All.
def Plist(*a):
    return list(a)
environment['Plist'] = Plist

# ]. All.
def singleton(a):
    return [a]
environment['singleton'] = singleton

# :. list.
def at_slice(a, b, c=0):
    if isinstance(a, str) and isinstance(b, str):
        if isinstance(c, str):
            return re.sub(b, c, a)
        if c == 0:
            return bool(re.search(b, a))
        if c == 1:
            return [m.group(0) for m in re.finditer(b, a)]
        if c == 2:
            def first_group(matchobj):
                return matchobj.group(1)
            return re.sub(b, first_group, a)
        if c == 3:
            return re.split(b, a)
        if c == 4:
            return [[m.group(0)] + list(m.groups()) for m in re.finditer(b, a)]
        return unknown_types(at_slice, ":", a, b, c)
    if is_seq(a) and isinstance(b, int) and isinstance(c, int):
        return a[slice(b, c)]

    if is_num(a) and is_num(b) and is_num(c):
        if c > 0:
            work = a
            gen_range = []
            if a <= b:
                def cont_test(work):
                    return work < b
                step = c
            else:
                def cont_test(work):
                    return work > b
                step = -c
            while cont_test(work):
                gen_range.append(work)
                work += step
            return gen_range
        elif c < 0:
            return at_slice(b, a, -c)[::-1]

    # There is no nice ABC for this check.
    if hasattr(a, "__getitem__") and is_col(b):
        if is_col(c):
            rep_c = itertools.cycle(c)
        else:
            rep_c = itertools.repeat(c)

        if isinstance(a, str) or isinstance(a, tuple):
            indexable = list(a)
        else:
            indexable = a

        for repl_index in b:
            if isinstance(a, str):
                indexable[repl_index] = str(next(rep_c))
            else:
                indexable[repl_index] = next(rep_c)

        if isinstance(a, str):
            return "".join(indexable)

        return indexable

    return unknown_types(at_slice, ":", a, b, c)
environment['at_slice'] = at_slice


# <. All.
def lt(a, b):
    if isinstance(a, set) and is_col(b):
        return a.issubset(b) and a != b
    if is_seq(a) and isinstance(b, int):
        return a[:b]
    if isinstance(a, int) and is_seq(b):
        if a >= len(b):
            if isinstance(b, str):
                return ''
            else:
                return []
        return b[:len(b) - a]
    if isinstance(a, complex) or isinstance(b, complex):
        return abs(a) < abs(b)
    if is_num(a) and is_num(b) or\
            isinstance(a, list) and isinstance(b, list) or\
            isinstance(a, tuple) and isinstance(b, tuple) or\
            isinstance(a, str) and isinstance(b, str):
        return a < b
    return unknown_types(lt, "<", a, b)
environment['lt'] = lt


# >. All.
def gt(a, b):
    if isinstance(a, set) and is_col(b):
        return a.issuperset(b) and a != b
    if is_seq(a) and isinstance(b, int):
        return a[b:]
    if isinstance(a, int) and is_seq(b):
        if a >= len(b):
            return b
        return b[len(b) - a:]
    if isinstance(a, complex) or isinstance(b, complex):
        return abs(a) > abs(b)
    if is_num(a) and is_num(b) or\
            isinstance(a, list) and isinstance(b, list) or\
            isinstance(a, tuple) and isinstance(b, tuple) or\
            isinstance(a, str) and isinstance(b, str):
        return a > b
    return unknown_types(gt, ">", a, b)
environment['gt'] = gt


# /. All.
def div(a, b):
    if is_num(a) and is_num(b):
        return int(a // b)
    if is_seq(a):
        return a.count(b)
    return unknown_types(div, "/", a, b)
environment['div'] = div


# a. List, Set.
def append(a, b):
    if isinstance(a, list):
        a.append(b)
        return a
    if isinstance(a, set):
        if is_hash(b):
            a.add(b)
            return a
        else:
            a.add(tuple(b))
            return a
    if is_num(a) and is_num(b):
        return abs(a - b)
    return unknown_types(append, "a", a, b)
environment['append'] = append

environment['b'] = "\n"


# c. All
def chop(a, b=None):
    if is_num(a) and is_num(b):
        return a / b
    if isinstance(a, str) and isinstance(b, str):
        return a.split(b)
    if isinstance(a, str) and b is None:
        return a.split()
    # iterable, int -> chop a into pieces of length b
    if is_seq(a) and isinstance(b, int):
        return [a[i:i + b] for i in range(0, len(a), b)]
    # int, iterable -> split b into a pieces (distributed equally)
    if isinstance(a, int) and is_seq(b):
        m = len(b) // a  # min number of elements
        r = len(b) % a   # remainding elements
        begin_ind, end_ind = 0, m + (r > 0)
        l = []
        for i in range(a):
            l.append(b[begin_ind:end_ind])
            begin_ind, end_ind = end_ind, end_ind + m + (i + 1 < r)
        return l
    # seq, col of ints -> chop seq at number locations.
    if is_seq(a) and is_col(b):
        if all(isinstance(elem, int) for elem in b) and not isinstance(b, str):
            locs = sorted(b)
            return [a[i:j] for i, j in zip([0] + locs, locs + [len(a)])]
    if is_seq(a):
        output = [[]]
        for elem in a:
            if elem == b:
                output.append([])
            else:
                output[-1].append(elem)
        return output
    return unknown_types(chop, "c", a, b)
environment['chop'] = chop


# C. int, str.
def Pchr(a):
    if isinstance(a, int):
        try:
            return chr(a)
        except (ValueError, OverflowError):
            return ''.join(chr(digit) for digit in from_base_ten(a, 256))
    if isinstance(a, complex):
        return a.real - a.imag * 1j
    if is_num(a):
        return Pchr(int(a))
    if isinstance(a, str):
        return to_base_ten([ord(char) for char in a], 256)
    if is_col(a):
        trans = list(zip(*a))
        if all(isinstance(sublist, str) for sublist in a):
            return [''.join(row) for row in trans]
        else:
            return [list(row) for row in trans]
    return unknown_types(Pchr, "C", a)
environment['Pchr'] = Pchr


environment['d'] = ' '


# e. All.
def end(a):
    if isinstance(a, complex):
        return a.imag
    if is_num(a):
        return a % 10
    if is_seq(a):
        return a[-1]
    return unknown_types(end, "e", a)
environment['end'] = end


# E.
def eval_input():
    return literal_eval(input())
environment['eval_input'] = eval_input


# f. single purpose.
def Pfilter(a, b=1):
    if is_num(b):
        return next(counter for counter in itertools.count(b) if a(counter))
    if is_col(b):
        return list(filter(a, b))
    return unknown_types(Pfilter, "f", a, b)
environment['Pfilter'] = Pfilter
environment['G'] = string.ascii_lowercase


# g. All.
def gte(a, b):
    if isinstance(a, set) and is_col(b):
        return a.issuperset(b)
    if is_seq(a) and isinstance(b, int):
        return a[b - 1:]
    if is_num(a) and is_num(b) or\
            isinstance(a, list) and isinstance(b, list) or\
            isinstance(a, tuple) and isinstance(b, tuple) or\
            isinstance(a, str) and isinstance(b, str):
        return a >= b
    return unknown_types(gte, "g", a, b)
environment['gte'] = gte
environment['H'] = {}


# h. int, str, list.
def head(a):
    if is_num(a):
        return a + 1
    if is_seq(a):
        return a[0]
    return unknown_types(head, "h", a)
environment['head'] = head


# i. int, str
def base_10(a, b):
    if isinstance(a, str) and isinstance(b, int):
        if not a:
            return 0
        return int(a, b)
    if is_seq(a) and is_num(b):
        return to_base_ten(a, b)
    if isinstance(a, int) and isinstance(b, int):
        return fractions.gcd(a, b)
    return unknown_types(base_10, "i", a, b)
environment['base_10'] = base_10


def to_base_ten(arb, base):
    # Special cases
    if abs(base) == 1:
        return len(arb)
    if len(arb) < 2:
        return arb[0] if arb else 0
    digits = []
    it = iter(arb)
    if len(arb) % 2 != 0:
        digits.append(next(it))
    for digit in it:
        digits.append(digit * base + next(it))
    return to_base_ten(digits, base * base)


# j. str.
def join(a, b=None):
    if b is None:
        a, b = '\n', a
    if isinstance(a, int) and isinstance(b, int):
        return from_base_ten(a, b)
    if isinstance(a, str) and is_col(b):
        return a.join(list(map(str, b)))
    if is_col(b):
        return str(a).join(list(map(str, b)))
    return unknown_types(join, "j", a, b)
environment['join'] = join


def from_base_ten(arb, base):
    # Special cases
    if arb == 0:
        return [0]
    if abs(base) == 1:
        return [0] * arb
    # Main routine
    base_list = []
    it = reversed(from_base_ten(arb, base * base) if abs(arb) >= abs(base) else [arb])
    digit = next(it)
    clock = 0
    work = 0
    while clock >= 0 or work != 0:
        if clock == 0:
            work += digit
            try:
                digit = next(it)
                clock = 2
            except StopIteration:
                digit = 0
        clock -= 1
        work, remainder = divmod(work, base)
        if remainder < 0:
            work += 1
            remainder -= base
        if work == -1 and base > 0:
            work = 0
            remainder -= base
        base_list.append(remainder)
    return base_list[::-1]

environment['k'] = ''


# l. any
def Plen(a):
    if is_num(a):
        if isinstance(a, complex) or a < 0:
            return cmath.log(a, 2)
        return math.log(a, 2)

    if is_col(a):
        return len(a)
    return unknown_types(Plen, "l", a)
environment['Plen'] = Plen


# m. Single purpose.
def Pmap(a, b):
    if is_num(b):
        return list(map(a, urange(b)))
    if is_col(b):
        return list(map(a, b))
    return unknown_types(Pmap, "m", a, b)
environment['Pmap'] = Pmap
environment['N'] = '"'


# n. All.
def ne(a, b):
    return not equal(a, b)
environment['ne'] = ne


# O. int, str, list
def rchoice(a):
    if isinstance(a, int):
        if a == 0:
            return random.random()
        if a < 0:
            random.seed(-a)
            return
        if a > 0:
            return random.randrange(a)
    if is_num(a):
        # random.uniform works for both complex and float
        return random.uniform(0, a)
    if is_seq(a):
        return random.choice(a)
    if is_col(a):
        return random.choice(list(a))
    return unknown_types(rchoice, "O", a)
environment['rchoice'] = rchoice


# o. Single purpose.
def order(a, b):
    if is_num(b):
        b = urange(b)
    if is_col(b):
        if isinstance(b, str):
            return ''.join(sorted(b, key=a))
        else:
            return sorted(b, key=a)
    return unknown_types(order, "o", a, b)
environment['order'] = order


# P. int, str, list.
def primes_pop(a):
    if isinstance(a, int):
        if a < 0:
            # Primality testing
            return len(primes_pop(-a)) == 1
        if a < 2:
            return []
        def simple_factor(a):
            working = a
            output = []
            num = 2
            while num * num <= working:
                while working % num == 0:
                    output.append(num)
                    working //= num
                num += 1
            if working != 1:
                output.append(working)
            return output
        if a < 10 ** 4:
            return simple_factor(a)
        else:
            try:
                from sympy import factorint
                factor_dict = factorint(a)
                factors_with_mult = [[fact for _ in range(
                    factor_dict[fact])] for fact in factor_dict]
                return sorted(sum(factors_with_mult, []))
            except:
                return simple_factor(a)
    if is_num(a):
        return cmath.phase(a)
    if is_seq(a):
        return a[:-1]
    return unknown_types(primes_pop, "P", a)
environment['primes_pop'] = primes_pop


# p. All.
def Pprint(a):
    print(a, end='')
    return a
environment['Pprint'] = Pprint


# q. All.
def equal(a, b):
    return a == b
environment['equal'] = equal


# r. int, int or str,int.
def Prange(a, b):
    def run_length_encode(a):
        return [[len(list(group)), key] for key, group in itertools.groupby(a)]

    if isinstance(b, int):
        if isinstance(a, str):
            if b == 0:
                return a.lower()
            if b == 1:
                return a.upper()
            if b == 2:
                return a.swapcase()
            if b == 3:
                return a.title()
            if b == 4:
                return a.capitalize()
            if b == 5:
                return string.capwords(a)
            if b == 6:
                return a.strip()
            if b == 7:
                return [Pliteral_eval(part) for part in a.split()]
            if b == 8:
                return run_length_encode(a)
            if b == 9:
                # Run length decoding, format "<num><char><num><char>",
                # e.g. "12W3N6S1E"
                return re.sub(r'(\d+)(\D)',
                              lambda match: int(match.group(1))
                              * match.group(2), a)

        if is_seq(a):
            if b == 8:
                return run_length_encode(a)
            if b == 9:
                if all(isinstance(key, str) for group_size, key in a):
                    return ''.join(key * group_size for group_size, key in a)
                else:
                    return sum(([copy.deepcopy(key)] * group_size
                                for group_size, key in a), [])
            return unknown_types(Prange, "r", a, b)

        if isinstance(a, int):
            if a < b:
                return list(range(a, b))
            else:
                return list(range(a, b, -1))
        return unknown_types(Prange, "r", a, b)
    if isinstance(a, str) and isinstance(b, str):
        a_val = Pchr(a)
        b_val = Pchr(b)
        ab_range = Prange(a_val, b_val)
        return [''.join(chr(char_val) for char_val in join(str_val, 256))
                for str_val in ab_range]
    if isinstance(a, int) and is_seq(b):
        return Prange(b, a)
    return unknown_types(Prange, "r", a, b)
environment['Prange'] = Prange


# s. int, str, list.
def Psum(a):
    if is_col(a) and not isinstance(a, str):
        if len(a) == 0:
            return 0
        if all(isinstance(elem, str) for elem in a):
            return ''.join(a)
        if len(a) > 100:
            cutoff = len(a) // 2
            first = a[:cutoff]
            second = a[cutoff:]
            return plus(Psum(first), Psum(second))
        return reduce(lambda b, c: plus(b, c), a[1:], a[0])
    if isinstance(a, complex):
        return a.real
    if a == '':
        return 0
    if is_num(a) or isinstance(a, str):
        return int(a)
    return unknown_types(Psum, "s", a)
environment['Psum'] = Psum


# S. seq
def Psorted(a):
    if isinstance(a, str):
        return ''.join(sorted(a))
    if is_col(a):
        return sorted(a)
    if isinstance(a, int):
        return list(range(1, a + 1))
    if is_num(a):
        return Psorted(int(a))
    return unknown_types(Psorted, "S", a)
environment['Psorted'] = Psorted
environment['T'] = 10


# t. int, str, list.
def tail(a):
    if is_num(a):
        return a - 1
    if is_seq(a):
        return a[1:]
    return unknown_types(tail, "t", a)
environment['tail'] = tail


# u. single purpose
def reduce(a, b, c=None):
    # Fixed point / Loop
    if c is None:
        counter = 0
        results = [copy.deepcopy(b)]
        acc = a(b, counter)
        while acc not in results:
            counter += 1
            results.append(copy.deepcopy(acc))
            acc = a(acc, counter)
        return copy.deepcopy(acc)

    # Reduce
    if is_seq(b) or is_num(b):
        if is_num(b):
            seq = urange(b)
        else:
            seq = b
        acc = c
        while len(seq) > 0:
            h = seq[0]
            acc = a(acc, h)
            seq = seq[1:]
        return acc
    return unknown_types(reduce, "u", a, b, c)
environment['reduce'] = reduce


# U. int, str, list.
def urange(a):
    if isinstance(a, int):
        if a >= 0:
            return list(range(a))
        else:
            return list(range(a, 0))
    if is_num(a):
        return urange(int(a))
    if is_col(a):
        return list(range(len(a)))
    return unknown_types(urange, "U", a)
environment['urange'] = urange


# v. str.
def preprocess_eval(a):
    if isinstance(a, str):
        if a and a[0] == '0':
            to_eval = a.lstrip('0')
            if not to_eval or not to_eval[0].isdecimal():
                to_eval = '0' + to_eval
            return to_eval
        else:
            return a
    return unknown_types(preprocess_eval, 'v', a)


def Pliteral_eval(a):
    if isinstance(a, str):
        return literal_eval(preprocess_eval(a))
    return unknown_types(Pliteral_eval, 'v', a)
environment['Pliteral_eval'] = Pliteral_eval


def Punsafe_eval(a):
    if isinstance(a, str):
        return eval(preprocess_eval(a))
    return unknown_types(Punsafe_eval, 'v', a)
environment['Punsafe_eval'] = Punsafe_eval


# X.
def assign_at(a, b, c=None):
    # Assign at
    if isinstance(a, dict):
        if isinstance(b, list):
            b = tuple(b)
        a[b] = c
        return a
    if isinstance(b, int):
        if isinstance(a, list):
            a[b % len(a)] = c
            return a
        if isinstance(a, str):
            return a[:b % len(a)] + str(c) + a[(b % len(a)) + 1:]
        if isinstance(a, tuple):
            return a[:b % len(a)] + (c,) + a[(b % len(a)) + 1:]
        return unknown_types(assign_at, "X", a, b, c)
    # Translate
    if is_seq(a) and is_seq(b) and (c is None or is_seq(c)):
        if c is None:
            c = b[::-1]

        def trans_func(element):
            return c[b.index(element) % len(c)] if element in b else element
        translation = map(trans_func, a)
        if isinstance(a, str) and isinstance(c, str):
            return ''.join(translation)
        else:
            return list(translation)
    # += in a list, X<int><list><any>
    if isinstance(a, int) and is_lst(b):
        b[a % len(b)] = plus(b[a % len(b)], c)
        return b
    # += in a dict, X<any><dict><any>
    if isinstance(b, dict):
        if isinstance(a, list):
            a = tuple(a)
        if a in b:
            b[a] = plus(b[a], c)
        else:
            b[a] = c
        return b
    # Insert in a string, X<int><str><any>
    if isinstance(a, int) and isinstance(b, str):
        if not isinstance(c, str):
            c = str(c)
        return b[:a] + c + b[a:]
    return unknown_types(assign_at, "X", a, b, c)
environment['assign_at'] = assign_at


# x. int, str, list.
def index(a, b):
    if isinstance(a, int) and isinstance(b, int):
        return a ^ b
    if is_seq(a) and not (isinstance(a, str) and not isinstance(b, str)):
        if b in a:
            return a.index(b)
        # replicate functionality from str.find
        else:
            return -1
    if is_lst(b):
        return [index for index, elem in enumerate(b) if elem == a]
    if isinstance(a, str):
        return index(a, str(b))
    return unknown_types(index, "x", a, b)
environment['index'] = index


# y. string, list.
def subsets(a):
    if is_num(a):
        return a * 2
    if is_col(a):
        def powerset(col):
            return itertools.chain.from_iterable(
                itertools.combinations(col, i) for i in range(0, len(col) + 1))
        return itertools_norm(powerset, a)
    return unknown_types(subsets, "y", a)
environment['subsets'] = subsets


environment['Y'] = []
environment['Z'] = 0


def hash_repr(a):
    if isinstance(a, bool):
        return "1" if a else "0"

    if isinstance(a, str) or is_num(a):
        return repr(a)

    if isinstance(a, list) or isinstance(a, tuple):
        return "[{}]".format(", ".join(hash_repr(l) for l in a))

    if isinstance(a, set):
        return "[{}]".format(", ".join(hash_repr(l) for l in sorted(a)))

    if isinstance(a, dict):
        elements = ["({}, {})".format(hash_repr(k), hash_repr(a[k]))
                    for k in sorted(a)]
        return "[{}]".format(", ".join(elements))

    return unknown_types(hash_repr, ".h", a)


def hex_multitype(a, func):
    if isinstance(a, str):
        return "0x" + (binascii.hexlify(a.encode("utf-8")).decode("utf-8") or "0")

    if isinstance(a, int):
        return hex(a)

    return unknown_types(hex_multitype, func, a)


# .h. any
def Phash(a):
    return int(hashlib.sha256(hash_repr(a).encode("utf-8")).hexdigest(), 16)
environment['Phash'] = Phash


# .a num/seq of num/seq of 2 seq of num
def Pabs(a):
    if is_num(a):
        return abs(a)
    if isinstance(a, tuple) or isinstance(a, list):
        if not a:
            return 0
        if is_num(a[0]):
            return sum(num ** 2 for num in a) ** .5
        if len(a) == 2:
            return sum((num1 - num2) ** 2 for num1, num2 in zip(*a)) ** .5

    return unknown_types(Pabs, ".a", a)
environment['Pabs'] = Pabs


# .b lambda, 2 ints or cols
def binary_map(a, b, c=None):
    if c is None:
        b, c = zip(*b)
    if is_num(b):
        b = urange(b)
    if is_num(c):
        c = urange(c)
    if is_col(b) and is_col(c):
        return list(map(a, b, c))
    return unknown_types(binary_map, ".b", a, b, c)
environment['binary_map'] = binary_map


# .B. int/str
def Pbin(a):
    if isinstance(a, int) or isinstance(a, str):
        return bin(int(hex_multitype(a, ".B"), 16))[2:]
    return unknown_types(Pbin, ".B", a)
environment['Pbin'] = Pbin


# .c. seq, int
def combinations(a, b):
    if isinstance(a, int) and isinstance(b, int):
        # compute n C r
        n, r = a, min(b, a - b)
        if r == 0:
            return 1
        if r < 0:
            r = max(b, a - b)
            if r < 0:
                return 0

        num = functools.reduce(operator.mul, range(n, n - r, -1), 1)
        den = math.factorial(r)

        return num // den

    if is_col(a) and isinstance(b, int):
        return itertools_norm(itertools.combinations, a, b)

    return unknown_types(combinations, ".c", a, b)

environment['combinations'] = combinations


# .C. iter, int
def combinations_with_replacement(a, b):
    if not is_col(a) or not isinstance(b, int):
        return unknown_types(combinations_with_replacement, ".C", a, b)

    return itertools_norm(itertools.combinations_with_replacement, a, b)
environment['combinations_with_replacement'] = combinations_with_replacement


# .d num, list of 2-elem lists
def dict_or_date(a):
    if isinstance(a, int):
        if a == 0:
            return time.time()
        if a == 1:
            return time.process_time()
        if 2 <= a <= 9:
            today = datetime.datetime.now()
            attributes = [today.year,
                          today.month,
                          today.day,
                          today.hour,
                          today.minute,
                          today.second,
                          today.microsecond]
            if a == 2:
                return attributes
            if a < 9:
                return attributes[a - 3]
            if a == 9:
                return today.weekday()
    if is_num(a):
        time.sleep(abs(a))
        return
    if is_col(a):
        return dict(a)
    return unknown_types(dict_or_date, ".d", a)
environment['dict_or_date'] = dict_or_date


# .D num, num or seq, int or seq, col
def divmod_or_delete(a, b):
    if is_num(a) and is_num(b):
        return list(divmod(a, b))
    elif is_seq(a) and is_num(b):
        return divmod_or_delete(a, [b])
    elif is_seq(a) and is_col(b):
        output = [e for i, e in enumerate(a) if i not in b]
        if isinstance(a, str):
            return "".join(output)
        return output
    return unknown_types(divmod_or_delete, '.D', a, b)
environment['divmod_or_delete'] = divmod_or_delete


# .e. lambda, seq
def Penumerate(a, b):
    if is_col(b):
        return list(map(lambda arg: a(*arg), enumerate(b)))

    return unknown_types(Penumerate, ".e", a, b)
environment['Penumerate'] = Penumerate


# .E. col/num
def Pany(a):
    if is_col(a):
        return any(a)
    if is_num(a):
        return int(math.ceil(a))
    return unknown_types(Pany, ".E", a)
environment['Pany'] = Pany


# .f. lambda, int, num or str.
def first_n(a, b, c=1):
    if not isinstance(b, int):
        return unknown_types(first_n, ".f", a, b, c)
    if is_num(c) or isinstance(c, str):
        return list(itertools.islice(filter(a, infinite_iterator(c)), b))
    elif is_col(c):
        return list(itertools.islice(filter(a, c), b))
    return unknown_types(first_n, ".f", a, b, c)
environment['first_n'] = first_n


# .F. format
def Pformat(a, b):
    if not isinstance(a, str):
        return unknown_types(Pformat, ".F", a, b)
    if is_seq(b) and not isinstance(b, str):
        return a.format(*b)

    return a.format(b)
environment['Pformat'] = Pformat


# .g lambda, seq
def group_by(a, b):
    if is_num(b):
        seq = urange(b)
    elif is_col(b):
        seq = b
    else:
        return unknown_types(group_by, ".g", a, b)
    key_sort = sorted(seq, key=a)
    grouped = itertools.groupby(key_sort, key=a)
    if isinstance(b, str):
        return list(map(lambda group: ''.join(group[1]), grouped))
    else:
        return list(map(lambda group: list(group[1]), grouped))
environment['group_by'] = group_by


# .H. int/str
def Phex(a):
    if isinstance(a, int) or isinstance(a, str):
        return hex_multitype(a, ".H")[2:]
    return unknown_types(Phex, ".H", a)
environment['Phex'] = Phex


# .i. seq, seq
def interleave(a, b):
    if is_seq(a) and is_seq(b):
        overlap = min(len(a), len(b))
        longer = max((a, b), key=len)
        inter_overlap = [item for sublist in zip(a, b) for item in sublist]
        if isinstance(a, str) and isinstance(b, str):
            return ''.join(inter_overlap) + longer[overlap:]
        else:
            return inter_overlap + list(longer[overlap:])
    if is_col(a) and not is_seq(a):
        return interleave(sorted(list(a)), b)
    if is_col(b) and not is_seq(b):
        return interleave(a, sorted(list(b)))
    return unknown_types(interleave, ".i", a, b)
environment['interleave'] = interleave


# .I. lambda, any
def invert(a, b):
    if not is_num(b):
        return unknown_types(invert, ".I", a, b)
    inv = 1.
    if a(inv) == b:
        return inv
    while a(inv) < b:
        inv *= 2
    delta = inv / 2
    while delta > 1e-20:
        if a(inv) == b:
            return inv
        if a(inv - delta) > b:
            inv -= delta
        elif a(inv - delta) == b:
            return inv - delta
        delta /= 2
    return inv
environment['invert'] = invert


# .j. int, int
def Pcomplex(a=0, b=1):
    if not is_num(a) and is_num(b):
        return unknown_types(Pcomplex, ".j", a, b)
    return a + b * complex(0, 1)
environment['Pcomplex'] = Pcomplex


# .l. num, num
def log(a, b=math.e):
    if not is_num(a) or not is_num(b):
        return unknown_types(log, ".l", a, b)
    if a < 0:
        return cmath.log(a, b)

    return math.log(a, b)
environment['log'] = log


# .m. func, seq or int
def minimal(a, b):
    if is_num(b):
        seq = urange(b)
    elif is_col(b):
        seq = b
    else:
        return unknown_types(minimal, ".m", a, b)
    minimum = min(map(a, seq))
    return list(filter(lambda elem: a(elem) == minimum, seq))
environment['minimal'] = minimal


# .M. func, seq or int
def maximal(a, b):
    if is_num(b):
        seq = urange(b)
    elif is_col(b):
        seq = b
    else:
        return unknown_types(maximal, ".M", a, b)
    maximum = max(map(a, seq))
    return list(filter(lambda elem: a(elem) == maximum, seq))
environment['maximal'] = maximal


# .n. mathematical constants
def Pnumbers(a):
    if isinstance(a, int) and a < 7:
        return [math.pi,
                math.e,
                2**.5,
                (1 + 5**0.5) / 2,
                float("inf"),
                -float("inf"),
                float("nan")][a]

    if is_lst(a):
        # Algorithm from:
        # http://stackoverflow.com/a/2158532/3739851
        # cc by-sa 3.0
        # Altered to use is_lst
        def flatten(l):
            for el in l:
                if is_lst(el):
                    for sub in flatten(el):
                        yield sub
                else:
                    yield el

        return list(flatten(a))

    return unknown_types(Pnumbers, ".n", a)
environment['Pnumbers'] = Pnumbers


# .O. int/str. Octal, average
def Poct(a):
    if is_col(a) and all(map(is_num, a)):
        if len(a) == 0:
            return 0.0
        else:
            return sum(a) / len(a)
    elif isinstance(a, int) or isinstance(a, str):
        return oct(int(hex_multitype(a, ".O"), 16))[2:]
    return unknown_types(Poct, ".O", a)
environment['Poct'] = Poct


# .p. seq
def permutations(a):
    if is_num(a):
        a = urange(a)
    if not is_col(a):
        return unknown_types(permutations, ".p", a)
    return itertools_norm(itertools.permutations, a, len(a))
environment['permutations'] = permutations


# .P. seq, int
def permutations2(a, b):
    if isinstance(a, int) and isinstance(b, int):
        # compute n P r
        return functools.reduce(operator.mul, range(a - b + 1, a + 1), 1)

    if is_col(a) and isinstance(b, int):
        return itertools_norm(itertools.permutations, a, b)

    if isinstance(a, int) and isinstance(b, str):
        return "".join(permutations2(a, list(b)))

    if isinstance(a, int) and is_col(b):
        # Algorithm modified from
        # http://stackoverflow.com/a/6784359/1938435
        # cc by-sa 3.0
        items = list(b)
        result = []
        a %= math.factorial(len(items))
        for x in range(len(items) - 1, -1, -1):
            fact = math.factorial(x)
            index = a // fact
            a -= index * fact
            result.append(items[index])
            del items[index]
        return result

    return unknown_types(permutations2, ".P", a, b)
environment['permutations2'] = permutations2


# .q. N\A
def Pexit():
    sys.exit(0)
environment['Pexit'] = Pexit


# .Q. N/A
@functools.lru_cache(1)
def eval_all_input():
    return [literal_eval(val) for val in all_input()]
environment['eval_all_input'] = eval_all_input


# .r col, seq
def rotate(a, b):
    if is_col(a) and is_seq(b):
        def trans_func(elem):
            if elem in b:
                elem_index = b.index(elem)
                return b[(elem_index + 1) % len(b)]
            else:
                return elem
        trans_a = map(trans_func, a)
        if isinstance(a, str):
            return ''.join(trans_a)
        if isinstance(a, set):
            return set(trans_a)
        return list(trans_a)

    return unknown_types(rotate, ".r", a, b)
environment['rotate'] = rotate


# .R num, num
def Pround(a, b):
    if is_num(a) and b == 0:
        return int(round(a))
    if is_num(a) and isinstance(b, int):
        return round(a, b)
    if is_num(a) and is_num(b):
        round_len = 0
        while round(b, round_len) != b and round_len < 15:
            round_len += 1
        return round(a, round_len)
    return unknown_types(Pround, ".R", a, b)
environment['Pround'] = Pround


# .s. str, str / seq, any
def Pstrip(a, b):
    if isinstance(a, str) and isinstance(b, str):
        return a.strip(b)
    if is_seq(a):
        if is_col(b):
            strip_items = list(b)
        else:
            strip_items = [b]
        seq = copy.deepcopy(a)
        while seq and seq[0] in strip_items:
            seq.pop(0)
        while seq and seq[-1] in strip_items:
            seq.pop()
        return seq
    return unknown_types(Pstrip, ".s", a, b)
environment['Pstrip'] = Pstrip


# .S. seq, int
def shuffle(a):
    if isinstance(a, list):
        random.shuffle(a)
        return a
    if isinstance(a, str):
        tmp_list = list(a)
        random.shuffle(tmp_list)
        return ''.join(tmp_list)
    if is_col(a):
        tmp_list = list(a)
        random.shuffle(tmp_list)
        return tmp_list
    if is_num(a):
        tmp_list = urange(a)
        random.shuffle(tmp_list)
        return tmp_list

    return unknown_types(shuffle, '.S', a)
environment['shuffle'] = shuffle


# .t. num, int
def trig(a, b=' '):
    if is_num(a) and isinstance(b, int):

        funcs = [math.sin, math.cos, math.tan,
                 math.asin, math.acos, math.atan,
                 math.degrees, math.radians,
                 math.sinh, math.cosh, math.tanh,
                 math.asinh, math.acosh, math.atanh]

        return funcs[b](a)

    if is_lst(a):
        width = max(len(row) for row in a)
        padded_matrix = [list(row) + (width - len(row)) * [b] for row in a]
        transpose = list(zip(*padded_matrix))
        if all(isinstance(row, str) for row in a) and isinstance(b, str):
            normalizer = ''.join
        else:
            normalizer = list
        norm_trans = [normalizer(padded_row) for padded_row in transpose]
        return norm_trans
    return unknown_types(trig, ".t", a, b)
environment['trig'] = trig


# .T. list
def transpose(a):
    if is_col(a):
        if not a:
            return a
        lol = [urange(elem) if is_num(elem) else elem for elem in a]
        cols = max(len(sublist) for sublist in lol)
        trans = [[] for _ in range(cols)]
        for sublist in lol:
            for index, elem in enumerate(sublist):
                trans[index].append(elem)
        if all(isinstance(sublist, str) for sublist in lol):
            return list(map(''.join, trans))
        else:
            return list(map(list, trans))
    return unknown_types(transpose, ".T", a)
environment['transpose'] = transpose


# .u. lambda, seq, any
def cu_reduce(a, b, c=None):
    if c is None:
        counter = 0
        results = [copy.deepcopy(b)]
        acc = a(b, counter)
        while acc not in results:
            counter += 1
            results.append(copy.deepcopy(acc))
            acc = a(acc, counter)
        return results
    if is_seq(b) or is_num(b):
        if is_num(b):
            seq = urange(b)
        else:
            seq = b
        acc = c
        results = [copy.deepcopy(acc)]
        while len(seq) > 0:
            h = seq[0]
            acc = a(acc, h)
            seq = seq[1:]
            results.append(copy.deepcopy(acc))
        return results
environment['cu_reduce'] = cu_reduce


# .U. lambda, seq
def reduce2(a, b):
    if is_seq(b) or isinstance(b, int):
        if is_num(b):
            whole_seq = urange(b)
        else:
            whole_seq = b
        if len(whole_seq) == 0:
            return unknown_types(reduce2, ".U", a, b)

        acc = whole_seq[0]
        seq = whole_seq[1:]

        while len(seq) > 0:
            h = seq[0]
            acc = a(acc, h)
            seq = seq[1:]
        return acc
    return unknown_types(reduce2, ".U", a, b)
environment['reduce2'] = reduce2


# .w. write
def Pwrite(a, b=''):
    if not isinstance(b, str):
        return unknown_types(Pwrite, ".w", a, b)

    if b.startswith("http"):
        if isinstance(a, dict):
            a = "&".join("=".join(i) for i in a.items())
        return [lin[:-1] if lin[-1] == '\n' else lin for lin
                in urllib.request.urlopen(b, a.encode("UTF-8"))]

    prefix = b.split('.')[0] if b else 'o'
    suffix = b.split('.')[1] if '.' in b else None

    if is_lst(a):
        from PIL import Image
        suffix = suffix if suffix else 'png'

        if not is_lst(a[0][0]):
            a = [[(i, i, i) for i in j] for j in a]
        else:
            a = [[tuple(i) for i in j] for j in a]

        header = "RGBA" if len(a[0][0]) > 3 else "RGB"
        img = Image.new(header, (len(a[0]), len(a)))

        img.putdata(Psum(a))
        img.save(prefix + "." + suffix)
    else:
        suffix = suffix if suffix else "txt"

        with open(prefix + '.' + suffix, 'a', encoding='iso-8859-1') as f:
            if is_seq(a) and not isinstance(a, str):
                f.write("\n".join(map(str, a)) + "\n")
            else:
                f.write(str(a) + "\n")

environment['Pwrite'] = Pwrite


# .W lambda, lambda, any
def apply_while(a, b, c):
    condition = a
    function = b
    value = c
    while condition(value):
        value = function(value)
    return value
environment['apply_while'] = apply_while


# .x try except
def Pexcept(a, b):
    try:
        return a()
    except:
        return b()
environment['Pexcept'] = Pexcept


# .y All subsets, all orders
def all_subset_orders(a):
    if is_num(a):
        a = urange(a)
    if not is_col(a):
        return unknown_types(all_subset_orders, ".y", a)
    def all_subsets_all_orders(a):
        return  itertools.chain.from_iterable(itertools.permutations(a, r) for r in range(len(a)+1))
    return itertools_norm(all_subsets_all_orders, a)
environment['all_subset_orders'] = all_subset_orders

# .z. N/A
@functools.lru_cache(1)
def all_input():
    return [l.rstrip("\n") for l in sys.stdin]
environment['all_input'] = all_input


# .Z. string
def compress(a):
    if isinstance(a, str):
        a = a.encode('iso-8859-1')
        try:
            a = zlib.decompress(a)
        except:
            a = zlib.compress(a, 9)
        return a.decode('iso-8859-1')

    return unknown_types(compress, ".Z", a)
environment['compress'] = compress


"""
To encode into this format, use the following Pyth expression:

J"Your string here"++hSJeSJCi-RChSJCMJ-hCeSJChSJ

Basically, subtract the character value of the smallest character from every character,
then base encode in the minimal possible base, convert back to a string, and stick
the smallest two characters at the front.
"""


# .". Special - str
def packed_str(pack):
    if not isinstance(pack, str):
        return unknown_types(packed_str, '."', pack)
    assert len(pack) >= 2, '." needs bounds.'
    lowest = pack[0]
    highest = pack[1]
    offset = ord(lowest)
    base = ord(highest) - ord(lowest) + 1
    int_rep = Pchr(pack[2:])
    reduced = from_base_ten(int_rep, base)
    final = ''.join(chr(a + offset) for a in reduced)
    return final
environment['packed_str'] = packed_str


# .&. int, int
def bitand(a, b):
    if isinstance(a, int) and isinstance(b, int):
        return a & b

    return unknown_types(bitand, ".&", a, b)
environment['bitand'] = bitand


# .|. int, int
def bitor(a, b):
    if isinstance(a, int) and isinstance(b, int):
        return a | b
    if is_col(a) and is_col(b):
        union = set(a) | set(b)
        if is_lst(a):
            return list(union)
        if isinstance(a, str):
            return ''.join(union)
        return union

    return unknown_types(bitor, ".|", a, b)
environment['bitor'] = bitor


# .<. int/seq, int
def leftshift(a, b):
    if not isinstance(b, int):
        return unknown_types(leftshift, ".<", a, b)

    if is_seq(a):
        if not a:
            return a
        b %= len(a)
        return a[b:] + a[:b]

    if isinstance(a, int):
        return a << b

    return unknown_types(leftshift, ".<", a, b)
environment['leftshift'] = leftshift


# .>. int/seq, int
def rightshift(a, b):
    if not isinstance(b, int):
        return unknown_types(rightshift, ".>", a, b)

    if is_seq(a):
        if not a:
            return a
        b %= len(a)
        return a[-b:] + a[:-b]

    if isinstance(a, int):
        return a >> b

    return unknown_types(rightshift, ".>", a, b)
environment['rightshift'] = rightshift


# ./. seq/int
def partition(a):
    if is_seq(a):
        all_splits = []
        for n in range(len(a)):  # 0, 1, ..., len(a)-1 splits
            for idxs in itertools.combinations(range(1, len(a)), n):
                all_splits.append(
                    [a[i:j] for i, j in zip((0,) + idxs, idxs + (None,))])
        return all_splits

    if isinstance(a, int) and a >= 0:
        @memoized
        def integer_partition(number):
            result = set()
            result.add((number, ))
            for x in range(1, number):
                for y in integer_partition(number - x):
                    result.add(tuple(sorted((x, ) + y)))
            return result
        return list(map(list, sorted(integer_partition(a))))

    return unknown_types(partition, "./", a)
environment['partition'] = partition


# ._. int
def sign(a):
    if is_seq(a):
        return [a[:end] for end in range(1, len(a) + 1)]
    if is_num(a):
        if a < 0:
            return -1
        if a > 0:
            return 1
        else:
            return 0
    return unknown_types(sign, "._", a)
environment['sign'] = sign


# .-. seq, seq
def remove(a, b):
    if not is_col(a) or not is_col(b):
        return unknown_types(remove, ".-", a, b)

    seq = list(a)
    to_remove = list(b)
    for elem in to_remove:
        if elem in seq:
            del seq[seq.index(elem)]

    if isinstance(a, str):
        return ''.join(seq)
    return seq
environment['remove'] = remove


# .+. seq
def deltas(a):
    if is_seq(a):
        return [minus(a[i+1], x) for i,x in enumerate(a[:-1])]
    return unknown_types(deltas, ".+", a)
environment['deltas'] = deltas    

# .:, int/seq, int
def substrings(a, b=None):
    if is_seq(a):
        seq = a
    elif is_num(a):
        seq = urange(a)
    else:
        return unknown_types(substrings, ".:", a, b)
    if is_col(b):
        return sum(([seq[start:start + step]
                     for step in b if start + step <= len(seq)]
                    for start in range(len(seq))), [])
    if isinstance(b, int):
        step = b
    elif isinstance(b, float):
        step = int(b * len(seq))
    elif not b:
        all_substrs = [substrings(seq, step)
                       for step in range(1, len(seq) + 1)]
        return list(itertools.chain.from_iterable(all_substrs))
    else:
        return unknown_types(substrings, ".:", a, b)
    return [seq[start:start + step] for start in range(len(seq) - step + 1)]
environment['substrings'] = substrings


# .{. All.
def Pset(a=set()):
    if is_num(a):
        return set([a])
    if is_col(a):
        try:
            return set(a)
        except TypeError:
            return set(map(tuple, a))
    return unknown_types(Pset, ".{", a)
environment['Pset'] = Pset


# .! factorial
def factorial(a):
    if isinstance(a, int):
        return math.factorial(a)
    if is_num(a):
        return math.gamma(a + 1)
    return unknown_types(factorial, '.!', a)
environment['factorial'] = factorial


# .[. str, str, int
def pad(a, b, c):
    if isinstance(a, str) and isinstance(b, str) and isinstance(c, int):
        pad_len = c if len(a) == 0 else (c - len(a)) % c
        return a + (b * pad_len)[:pad_len]
    if isinstance(b, str) and isinstance(c, str) and isinstance(a, int):
        pad_len = a if len(b) == 0 else (a - len(b)) % a
        pad_string = (c * pad_len)[:pad_len]
        return pad_string[:pad_len // 2] + b + pad_string[pad_len // 2:]
    if isinstance(c, str) and isinstance(a, str) and isinstance(b, int):
        pad_len = b if len(c) == 0 else (b - len(c)) % b
        return (a * pad_len)[:pad_len] + c

    if is_seq(a) and isinstance(c, int):
        pad_len = c if len(a) == 0 else (c - len(a)) % c
        return list(a) + [b] * pad_len
    if is_seq(b) and isinstance(a, int):
        pad_len = a if len(b) == 0 else (a - len(b)) % a
        return [c] * (pad_len // 2) + list(b) + [c] * ((pad_len + 1) // 2)
    if is_seq(c) and isinstance(b, int):
        pad_len = b if len(c) == 0 else (b - len(c)) % b
        return [a] * pad_len + list(c)

    return unknown_types(pad, ".[", a, b, c)
environment['pad'] = pad
