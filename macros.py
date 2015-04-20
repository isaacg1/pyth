import copy
import fractions
import itertools
import functools
import cmath
import math
import random
import re
import string
import sys
import collections
import numbers
import binascii
import hashlib
from ast import literal_eval


# Type checking
def is_num(a):
    return isinstance(a, numbers.Number)

def is_seq(a):
    return isinstance(a, collections.Sequence)

def is_col(a):
    return isinstance(a, collections.Iterable)

def is_hash(a):
    return isinstance(a, collections.Hashable)

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
    if isinstance(a, list):
        return [list(group) for group in func(a, *args, **kwargs)]
    if isinstance(a, set):
        return [set(group) for group in func(a, *args, **kwargs)]

    return [group for group in func(a, *args, **kwargs)]


# Function library. See data for letter -> function correspondences.
# !. All.
def Pnot(a):
    return not a


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
        intersection = filter(lambda b_elm: b_elm in a, b)
        if isinstance(a, str):
            return ''.join(intersection)
        if isinstance(a, tuple):
            return tuple(intersection)
        if isinstance(a, set):
            return set(intersection)
        else:
            return list(intersection)
    raise BadTypeCombinationError("@", a, b)


# %. int, str.
def mod(a, b):
    if isinstance(a, int) and is_seq(b):
        return b[::a]
    if is_num(a) and is_num(b) or isinstance(a, str):
        return a % b
    raise BadTypeCombinationError("%", a, b)


# ^. int, str, list.
def Ppow(a, b):
    if is_num(a) and is_num(b):
        return pow(a, b)
    if is_col(a) and isinstance(b, int):
        return itertools_norm(itertools.product, a, repeat=b)

    raise BadTypeCombinationError("^", a, b)


# *. int, str, list.
def times(a, b):
    if is_col(a) and is_col(b):
        return list(itertools.product(a, b))
    if is_num(a) and is_num(b) or\
            isinstance(a, int) and is_seq(b) or\
            is_seq(a) and isinstance(b, int):
        return a*b
    raise BadTypeCombinationError("*", a, b)


# (. All types
def Ptuple(*a):
    return a


# -. int, set.
def minus(a, b):
    if is_num(a) and is_num(b):
        return a-b
    if is_num(a) and is_col(b):
        if isinstance(b, str):
            return minus(str(a), b)
        if isinstance(b, list):
            return minus([a], b)
        if isinstance(b, set):
            return minus({a}, b)
        if isinstance(b, tuple):
            return minus((a,), b)
    if is_num(b) and is_col(a):
        if isinstance(a, str):
            return minus(a, str(b))
        if isinstance(a, list):
            return minus(a, [b])
        if isinstance(a, set):
            return minus(a, {b})
        if isinstance(a, tuple):
            return minus(a, (b,))
    if is_col(a) and is_col(b):
        difference = filter(lambda c: c not in b, a)
        if isinstance(a, str):
            return ''.join(difference)
        if isinstance(a, list):
            return list(difference)
        if isinstance(a, set):
            return set(difference)
        if isinstance(a, tuple):
            return tuple(difference)
    raise BadTypeCombinationError("-", a, b)


# '. str.
def read_file(a):
    if isinstance(a, str):
        b = [lin[:-1] if lin[-1] == '\n' else lin for lin in (open(a))]
        return b
    raise BadTypeCombinationError("'", a)


# _. All.
def neg(a):
    if is_num(a):
        return -a
    if is_seq(a):
        return a[::-1]
    if isinstance(a, dict):
        return {value: key for key, value in a.items()}
    raise BadTypeCombinationError("_", a)


# {. All.
def Pset(a=set()):
    if is_num(a):
        return set([a])
    if is_col(a):
        return set(a)
    raise BadTypeCombinationError("{", a)


# +. All.
def plus(a, b):
    if isinstance(a, set):
        if is_col(b):
            return a.union(b)
        else:
            return a.union({b})
    if isinstance(a, list) and not isinstance(b, list):
        return a+[b]
    if isinstance(b, list) and not isinstance(a, list):
        return [a]+b
    if isinstance(a, tuple) and not isinstance(b, tuple):
        return a+(b,)
    if isinstance(b, tuple) and not isinstance(a, tuple):
        return b+(a,)
    if is_num(a) and is_num(b) or\
            isinstance(a, list) and isinstance(b, list) or\
            isinstance(a, tuple) and isinstance(b, tuple) or\
            isinstance(a, str) and isinstance(b, str):
        return a+b
    raise BadTypeCombinationError("+", a, b)


# =. All.
copy = copy.deepcopy


# [. All.
def Plist(*a):
    return list(a)


# :. list.
def at_slice(a, b, c):
    if isinstance(a, str) and isinstance(b, str):
        if not isinstance(c, str):
            return bool(re.search(b, a))
        else:
            return re.sub(b, c, a)
    if isinstance(b, int) and (isinstance(c, int) or c==None):
        return a[slice(b, c)]

    # There is no nice ABC for this check.
    if hasattr(a, "__getitem__") and is_col(b):
        if is_col(c):
            c = itertools.cycle(c)
        else:
            c = itertools.repeat(c)
        
        if isinstance(a, str) or isinstance(a, tuple):
            indexable = list(a)
        else:
            indexable = a

        for index in b:
            if isinstance(a, str):
                indexable[index] = str(next(c))
            else:
                indexable[index] = next(c)

        if isinstance(a, tuple):
            return tuple(indexable)

        if isinstance(a, str):
            return "".join(indexable)

        return indexable

    raise BadTypeCombinationError(":", a, b, c)


# <. All.
def lt(a, b):
    if isinstance(a, set) and is_col(b):
        return a.issubset(b) and a != b
    if is_seq(a) and is_num(b):
        return a[:b]
    if is_num(a) and is_num(b) or\
            isinstance(a, list) and isinstance(b, list) or\
            isinstance(a, tuple) and isinstance(b, tuple) or\
            isinstance(a, str) and isinstance(b, str):
        return a < b
    raise BadTypeCombinationError("<", a, b)


# >. All.
def gt(a, b):
    if isinstance(a, set) and is_col(b):
        return a.issuperset(b) and a != b
    if is_seq(a) and is_num(b):
        return a[b:]
    if is_num(a) and is_num(b) or\
            isinstance(a, list) and isinstance(b, list) or\
            isinstance(a, tuple) and isinstance(b, tuple) or\
            isinstance(a, str) and isinstance(b, str):
        return a > b
    raise BadTypeCombinationError(">", a, b)


# /. All.
def div(a, b):
    if is_num(a) and is_num(b):
        return int(a // b)
    if is_seq(a):
        return a.count(b)
    raise BadTypeCombinationError("/", a, b)

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
    raise BadTypeCombinationError("a", a, b)

b = "\n"


# c. All
def chop(a, b=None):
    if is_num(a) and is_num(b):
        return a/b
    if isinstance(a, str) and isinstance(b, str):
        return a.split(b)
    if isinstance(a, str) and b is None:
        return a.split()
    # iterable, int -> chop a into pieces of length b
    if is_seq(a) and isinstance(b, int):
        return [a[i:i+b] for i in range(0, len(a), b)]
    # int, iterable -> split b into a pieces (distributed equally)
    if isinstance(a, int) and is_seq(b):
        m = len(b) // a  # min number of elements
        r = len(b) % a   # remainding elements
        begin, end = 0, m + (r > 0)
        l = []
        for i in range(a):
            l.append(b[begin:end])
            begin, end = end, end + m + (i + 1 < r)
        return l
    raise BadTypeCombinationError("c", a, b)


# C. int, str.
def Pchr(a):
    if isinstance(a, int):
        return chr(a)
    if isinstance(a, str):
        return ord(a[0])
    if is_col(a):
        return list(zip(*a))
    raise BadTypeCombinationError("C", a)


d = ' '


# e. All.
def end(a):
    if is_num(a):
        return a % 10
    if is_seq(a):
        return a[-1]
    raise BadTypeCombinationError("e", a)


# f. single purpose.
def Pfilter(a, b):
    if is_num(b):
        return next(filter(a, itertools.count(b)))
    if is_col(b):
        return list(filter(a, b))
    raise BadTypeCombinationError("f", a, b)
G = string.ascii_lowercase


# g. All.
def gte(a, b):
    if isinstance(a, set) and is_col(b):
        return a.issuperset(b)
    if is_seq(a) and is_num(b):
        return a[b-1:]
    if is_num(a) and is_num(b) or\
            isinstance(a, list) and isinstance(b, list) or\
            isinstance(a, tuple) and isinstance(b, tuple) or\
            isinstance(a, str) and isinstance(b, str):
        return a >= b
    raise BadTypeCombinationError("g", a, b)
H = {}


# h. int, str, list.
def head(a):
    if is_num(a):
        return a+1
    if is_seq(a):
        return a[0]
    raise BadTypeCombinationError("h", a)


# i. int, str
def base_10(a, b):
    if isinstance(a, str) and isinstance(b, int):
        return int(a, b)
    if is_seq(a) and is_num(b):
        return to_base_ten(a, b)
    if isinstance(a, int) and isinstance(b, int):
        return fractions.gcd(a, b)
    raise BadTypeCombinationError("i", a, b)


def to_base_ten(arb, base):
    # Special cases
    if base == 1:
        return len(arb)
    acc = 0
    for digit in arb:
        acc *= base
        acc += digit
    return acc


# j. str.
def join(a, b):
    if isinstance(a, int) and isinstance(b, int):
        return from_base_ten(a, b)
    if isinstance(a, str) and is_col(b):
        return a.join(list(map(lambda N: str(N), b)))
    if is_col(b):
        return str(a).join(list(map(lambda N: str(N), b)))
    raise BadTypeCombinationError("j", a, b)


def from_base_ten(arb, base):
    # Special cases
    if arb == 0:
        return [0]
    if base == 1:
        return [0]*arb
    #Main routine
    base_list = []
    work = arb
    while work > 0:
        base_list.append(work % base)
        work //= base
    return base_list[::-1]

k = ''


def Plen(a):
    if is_num(a):
        return math.log(a, 2)
    if is_col(a):
        return len(a)
    raise BadTypeCombinationError("l", a)


# m. Single purpose.
def Pmap(a, b):
    if isinstance(b, int):
        return list(map(a, range(b)))
    if is_col(b):
        return list(map(a, b))
    raise BadTypeCombinationError("m", a, b)
N = '"'


# n. All.
def ne(a, b):
    return a != b


# O. int, str, list
def rchoice(a):
    if isinstance(a, int):
        if a == 0:
            return random.random()
        return random.choice(urange(a))
    if is_col(a):
        return random.choice(list(a))
    raise BadTypeCombinationError("O", a)


# o. Single purpose.
def order(a, b):
    if is_col(b):
        if isinstance(b, str):
            return ''.join(sorted(b, key=a))
        else:
            return sorted(b, key=a)
    raise BadTypeCombinationError("o", a, b)


def isprime(num):
    return all(num % div != 0 for div in range(2, int(num ** .5 + 1)))


# P. int, str, list.
def primes_upper(a):
    if isinstance(a, int):
        if a < 2:
            return []
        working = a
        output = []
        for num in filter(isprime, range(2, int(a**.5 + 1))):
            while working % num == 0:
                output.append(num)
                working //= num
        if working != 1:
            output.append(working)
        return output
    if is_seq(a):
        return a[:-1]
    raise BadTypeCombinationError("P", a)


# p. All.
def Pprint(a, b=""):
    if isinstance(a, str):
        print(b, end=a)
    else:
        print(b, end=str(a))
    return 0


# q. All.
def equal(a, b):
    return a == b


# r. int, int or str,int.
def Prange(a, b):
    if isinstance(a, str) and isinstance(b, int):
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
            return [literal_eval(part) for part in a.split()]
    if isinstance(a, int) and isinstance(b, int):
        if a < b:
            return list(range(a, b))
        else:
            return list(range(a, b, -1))
    raise BadTypeCombinationError("r", a, b)


# s. int, str, list.
def Psum(a):
    if is_col(a) and not isinstance(a, str):
        if len(a) == 0:
            return 0
        return reduce(lambda b, c: plus(b, c), a[1:], a[0])
    if is_num(a) or isinstance(a, str):
        return int(a)
    raise BadTypeCombinationError("s", a)


def Psorted(a):
    if isinstance(a, str):
        return ''.join(sorted(a))
    if is_col(a):
        return sorted(a)
    raise BadTypeCombinationError("S", a)
T = 10


# t. int, str, list.
def tail(a):
    if is_num(a):
        return a-1
    if is_seq(a):
        return a[1:]
    raise BadTypeCombinationError("t", a)


# u. single purpose
def reduce(a, b, c=None):
    # Fixed point
    if c is None:
        counter = 0
        old_acc = b
        acc = a(b, counter)
        while old_acc != acc:
            counter += 1
            old_acc = acc
            acc = a(acc, counter)
        return acc
    
    # Reduce
    
    #Check for special fold case
    if b==float('inf'):
        b,c=c[1:],c[0]
    
    if is_seq(b) or isinstance(b, int):
        if isinstance(b, int):
            seq = range(b)
        else:
            seq = b
        acc = c
        while len(seq) > 0:
            h = seq[0]
            acc = a(acc, h)
            seq = seq[1:]
        return acc
    raise BadTypeCombinationError("u", a, b, c)


# U. int, str, list.
def urange(a):
    if isinstance(a, int):
        return list(range(a))
    if is_col(a):
        return list(range(len(a)))
    raise BadTypeCombinationError("U", a)


# X.
def assign_at(a, b, c):
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
            return a[:b % len(a)] + str(c) + a[(b % len(a))+1:]
        if isinstance(a, tuple):
            return a[:b % len(a)] + (c,) + a[(b % len(a))+1:]
    # Translate
    if is_seq(a) and is_seq(b) and is_seq(c):
        def trans_func(element):
            return c[b.index(element)] if element in b else element
        translation = map(trans_func, a)
        if isinstance(a, str) and isinstance(c, str):
            return ''.join(translation)
        else:
            return list(translation)
    # += in a list, X<int><list><any>
    if isinstance(a, int) and isinstance(b, list):
        b[a % len(b)] += c
        return b
    # += in a dict, X<any><dict><any>
    if isinstance(b, dict):
        if is_seq(a): a = tuple(a)
        if a in b:
            b[a] += c
        else:
            b[a] = c
        return b
    raise BadTypeCombinationError("X", a, b, c)


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
    raise BadTypeCombinationError("x", a, b)


# y. string, list.
def subsets(a):
    if is_num(a):
        return a*2
    if isinstance(a, str):
        if len(a) == 0:
            return [a]
        if len(a) == 1:
            return ['', a]
        else:
            others = subsets(a[:-1])
            out = others + list(map(lambda sub: sub + a[-1], others))
            return sorted(out, key=len)
    if is_seq(a):
        if len(a) == 0:
            return [a]
        if len(a) == 1:
            return [[], list(a)]
        else:
            others = subsets(a[:-1])
            out = others + list(map(lambda sub: sub + [a[-1]], others))
            return sorted(out, key=len)
    if isinstance(a, set):
        return subsets(sorted(list(a)))
    raise BadTypeCombinationError("y", a)


Y = []
Z = 0

def hash_repr(a):
    if isinstance(a, bool):
        return a and "1" or "0"

    if isinstance(a, str) or is_num(a):
        return repr(a)
    
    if isinstance(a, list) or isinstance(a, tuple):
        return "[{}]".format(", ".join(hash_repr(l) for l in a))

    if isinstance(a, set):
        return "[{}]".format(", ".join(hash_repr(l) for l in sorted(a)))

    if isinstance(a, dict):
        elements = ["({}, {})".format(hash_repr(k), hash_repr(a[k])) for k in sorted(a)]
        return "[{}]".format(", ".join(elements))

    raise BadTypeCombinationError(".h", a)

# .h. any
def Phash(a):
    return int(hashlib.sha256(hash_repr(a).encode("utf-8")).hexdigest(), 16)


def Phex_multitype(a, func):
    if isinstance(a, str):
        return "0x" + binascii.hexlify(a.encode("utf-8")).decode("utf-8")

    if isinstance(a, int):
        return hex(a)

    raise BadTypeCombinationError(func, a)


# .H. int/str
def Phex(a):
    return Phex_multitype(a, ".H")[2:]


# .B. int/str
def Pbin(a):
    return bin(int(Phex_multitype(a, ".B"), 16))[2:]


# .O. int/str
def Poct(a):
    return oct(int(Phex_multitype(a, ".O"), 16))[2:]


# .c. seq, int
def combinations(a, b):
    if not is_seq(a) or not isinstance(b, int):
        raise BadTypeCombinationError(".c", a, b)

    return itertools_norm(itertools.combinations, a, b)


# .C. iter, int
def combinations_with_replacement(a, b):
    if not is_seq(a) or not isinstance(b, int):
        raise BadTypeCombinationError(".C", a, b)

    return itertools_norm(itertools.combinations_with_replacement, a, b)


# .e. lambda, seq
def Penumerate(a, b):
    if is_col(b):
        return list(map(lambda arg: a(*arg), enumerate(b)))

    raise BadTypeCombinationError(".e", a, b)


# .F. format
def Pformat(a, b):
    if not isinstance(a, str):
        raise BadTypeCombinationError("F", a, b)
    if is_seq(b) and not isinstance(b, str):
        return a.format(*b)
    
    return a.format(b)


# .l. num, num
def log(a, b=math.e):
    if not is_num(a) or not is_num(b):
        raise BadTypeCombinationError(".l", a, b)

    return math.log(a, b)


# .m. func, seq or int
def minimal(a, b):
    if isinstance(b, int):
        seq = range(b)
    elif is_col(b):
        seq = b
    else:
        raise BadTypeCombinationError(".m", a, b)
    minimum = min(map(a, seq))
    return list(filter(lambda elem: a(elem) == minimum, seq))


# .M. func, seq or int
def maximal(a, b):
    if isinstance(b, int):
        seq = range(b)
    elif is_col(b):
        seq = b
    else:
        raise BadTypeCombinationError(".M", a, b)
    maximum = max(map(a, seq))
    return list(filter(lambda elem: a(elem) == maximum, seq))

# .n. mathematical constants
def Pnumbers(a):
    if a < 7 and isinstance(a, int):
        return [math.pi, math.e, 2**.5, (1+5**0.5)/2, float("inf"), -float("inf"), float("nan")][a]
    
    raise BadTypeCombinationError(".n", a)

# .p. seq
def permutations(a):
    if not is_seq(a):
        raise BadTypeCombinationError(".p", a)
    return itertools_norm(itertools.permutations, a, len(a))


# .P. seq, int
def permutations2(a, b):
    if not is_seq(a) or not isinstance(b, int):
        raise BadTypeCombinationError(".P", a, b)

    return itertools_norm(itertools.permutations, a, b)

# .q. N\A
def Pexit():
    sys.exit(0)

# .Q. N/A
@functools.lru_cache(1)
def eval_all_input():
    def eval_trim_line(line):
        return literal_eval(line.rstrip("\n"))
    return list(map(eval_trim_line, sys.stdin))


# .r. seq
def run_length_encoding(a):
    if is_seq(a):
        if len(a) == 0:
            return []
        rle = []
        running_count = 1
        current_elem = a[0]
        for elem in a[1:]:
            if elem == current_elem:
                running_count += 1
            else:
                rle.append([current_elem, running_count])
                current_elem = elem
                running_count = 1
        rle.append([current_elem, running_count])
        return rle
    if is_col(a):
        return run_length_encoding(sorted(a))

    raise BadTypeCombinationError(".r", a)

# .s. str, str
def stripchars(a, b):
    if isinstance(a, str) and isinstance(b, str):
        return a.strip(b)

    raise BadTypeCombinationError(".s", a, b)


# .S. seq, int
def shuffle(a):
    if isinstance(a, list):
        random.shuffle(a)
        return a
    if isinstance(a, str):
        tmp_list = list(a)
        random.shuffle(tmp_list)
        return ''.join(tmp_list)
    if is_seq(a):
        tmp_list = list(a)
        random.shuffle(tmp_list)
        return tmp_list
    if isinstance(a, int):
        tmp_list = list(range(a))
        random.shuffle(tmp_list)
        return tmp_list

    raise BadTypeCombinationError('.S', a, b)


# .t. num, int
def trig(a, b):
    if not is_num(a) or not isinstance(b, int):
        raise BadTypeCombinationError(".t", a, b, c)

    funcs = [math.sin, math.cos, math.tan,
             math.asin, math.acos, math.atan,
             math.degrees, math.radians,
             math.sinh, math.cosh, math.tanh,
             math.asinh, math.acosh, math.atanh]

    return funcs[b](a)

# .w. write
def Pwrite(a, b="foo.txt"):
    if not isinstance(b, str):
        raise BadTypeCombinationError(".w", a, b)
    with open(b, 'a') as f:
        f.write(("\n".join(map(str, a)) if is_seq(a) and not isinstance(a, str) else str(a))+"\n")

# .x. col
def product(a):
    if is_col(a) and not isinstance(a, str):
        if len(a) == 0:
            return 1
        return reduce(lambda b, c: times(b, c), a[1:], a[0])
    
    if is_num(a):
        return random.seed(a)

    raise BadTypeCombinationError(".x", a)

# .z. N/A
@functools.lru_cache(1)
def all_input():
    def trim_line(line):
        return line.rstrip("\n")
    return list(map(trim_line, sys.stdin))


# .&. int, int
def bitand(a, b):
    if isinstance(a, int) and isinstance(b, int):
        return a & b

    raise BadTypeCombinationError(".&", a, b)


# .|. int, int
def bitor(a, b):
    if isinstance(a, int) and isinstance(b, int):
        return a | b
    if is_col(a) and is_col(b):
        union = set(a) | set(b)
        if isinstance(a, list):
            return list(union)
        if isinstance(a, str):
            return ''.join(union)
        if isinstance(a, tuple):
            return tuple(union)
        return union

    raise BadTypeCombinationError(".|", a, b)


# .<. int/seq, int
def leftshift(a, b):
    if not isinstance(b, int):
        raise BadTypeCombinationError(".<", a, b)

    if is_seq(a):
        b %= len(a)
        return a[b:] + a[:b]

    if isinstance(a, int):
        return a << b

    raise BadTypeCombinationError(".<", a, b)


# .>. int/seq, int
def rightshift(a, b):
    if not isinstance(b, int):
        raise BadTypeCombinationError(".>", a, b)

    if is_seq(a):
        b %= len(a)
        return a[-b:] + a[:-b]

    if isinstance(a, int):
        return a >> b

    raise BadTypeCombinationError(".>", a, b)


# ._. int
def sign(a):
    if not is_num(a):
        raise BadTypeCombinationError("._", a)

    if a < 0:
        return -1
    if a > 0:
        return 1
    else:
        return 0


# .-. seq, seq
def remove(a, b):
    if not is_seq(a) or not is_col(b):
        raise BadTypeCombinationError(".-", a, b)

    seq = list(a)
    to_remove = list(b)
    for elem in to_remove:
        if elem in seq:
            del seq[seq.index(elem)]

    if isinstance(a, str):
        return ''.join(seq)
    if isinstance(a, tuple):
        return tuple(seq)
    else:
        return seq

# .:, int/seq, int
def substrings(a, b):
    if is_seq(a):
        seq = a
    elif isinstance(a, int):
        seq = list(range(a))
    else:
        raise BadTypeCombinationError(".:", a, b)
    if isinstance(b, int):
        step = b
    elif isinstance(b, float):
        step = int(b * len(seq))
    elif is_col(b):
        step = len(b)
    else:
        raise BadTypeCombinationError(".:", a, b)
    return [seq[start:start+step] for start in range(len(seq)-step+1)]
