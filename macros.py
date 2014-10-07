import copy
import math
import random
import re
import string
import sys


# Type checking - num class
def isnum(a):
    return isinstance(a, int) or isinstance(a, float)


# Function library. See data for letter -> function correspondences.
# !. All.
def Pnot(a):
    return not a


# %. int, str.
def mod(a, b):
    return a % b


# *. int, str, list.
def times(a, b):
    return a*b


# (. All types
def Ptuple(*a):
    return a


# -. int, set.
def minus(a, b):
    if isnum(a):
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
    a = [lin[:-1] if lin[-1] == '\n' else lin for lin in (open(input()))]
    return a


# _. All.
def neg(a):
    if isnum(a):
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
def Plist(*a):
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
    if not isnum(a) and isnum(b):
        return a[:b]
    return a < b


# >. All.
def gt(a, b):
    if isinstance(a, set):
        return a.issuperset(b) and a != b
    if not isnum(a) and isnum(b):
        return a[b:]
    return a > b


# /. All.
def div(a, b):
    if isnum(a):
        return int(a // b)
    return a.count(b)


# a. All
def Pand(a, b):
    if isinstance(a, int):
        return a & b
    else:
        intersection = set(a) & set(b)
        if isinstance(a, str):
            return ''.join(sorted(intersection))
        if isinstance(a, list):
            return list(sorted(intersection))
        else:
            return intersection
b = "\n"


# c. All
def chop(a, b=None):
    if isnum(a):
        return a/b
    if isinstance(b, str):
        return a.split(b)
    if b is None:
        return a.split()
    return list(map(lambda d: a[b*d:b*(d+1)], range(math.ceil(len(a)/b))))


# C. int, str.
def Pchr(a):
    if isinstance(a, int):
        return chr(a)
    if isinstance(a, str):
        return ord(a[0])


d = ' '


# e. All.
def end(a):
    if isnum(a):
        return a % 10
    return a[-1]


# f. single purpose.
def Pfilter(a, b):
    return list(filter(a, b))
G = string.ascii_lowercase


# g. All.
def gte(a, b):
    if isinstance(a, set):
        return a.issuperset(b)
    if not isnum(a) and isnum(b):
        return a[b-1:]
    return a >= b
H = {}


# h. int, str, list.
def head(a):
    if isnum(a):
        return a+1
    return a[0]


# i. int, str
def int_2(a, b=0):
    if not b:
        return float(a)
    return int(a, b)


# j. str.
def join(a, b):
    if isinstance(a, int):
        return convert_base(a, b)
    return a.join(list(map(lambda N: str(N), b)))


def convert_base(arb, base):
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


# m. Single purpose.
def Pmap(a, b):
    return list(map(a, b))


# M. str, list.
def move_slice(a, b, c=None):
    if isinstance(b, str):
        if c is None:
            return re.sub(b, '', a)
        elif c is 0:
            return not not re.search(b, a)
        else:
            return re.sub(b, c, a)
    if c in None:
        return a[slice(0, b)]
    else:
        return a[slice(b, b+c)]
N = '"'


# n. All.
def ne(a, b):
    return a != b


# O. int, str, list
def rchoice(a):
    if isinstance(a, int):
        return random.choice(Prange(a))
    return random.choice(list(a))


# o. Single purpose.
def order(a, b):
    if isinstance(b, str):
        return ''.join(sorted(b, key=a))
    return sorted(b, key=a)


def isprime(num):
    return all(num % div != 0 for div in range(2, int(num ** .5 + 1)))


# P. str.
def primes_upper(a):
    if isinstance(a, int):
        working = a
        output = []
        for num in filter(isprime, range(2, int(a**.5 + 1))):
            while working % num == 0:
                output.append(num)
                working //= num
        if working != 1:
            output.append(working)
        return output
    return a.upper()


# p. All.
def Pprint(a, b=""):
    print(b, end=a)
    return 0
# Q. Unimplemented.


# q. All.
def equal(a, b):
    return a == b


# r. int.
def Prange(a, b=None):
    if b:
        if a < b:
            return list(range(a, b))
        else:
            return list(range(b, a))[::-1]
    else:
        return list(range(a))


# s. int, str, list.
def Psum(a):
    if isinstance(a, list):
        return reduce(lambda b, c: b+c, a)
    else:
        return int(a)
T = 10


# t. int, str, list.
def tail(a):
    if isnum(a):
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
    if isinstance(a, tuple) and len(a) == 2:
        return list(range(a[0], a[1]))
    return list(range(len(a)))


# x. int, str, list.
def index(a, b):
    if isinstance(a, int):
        return a ^ b
    if b in a:
        return a.index(b)
    # replicate functionality from str.find
    else:
        return -1


# y. String.
def space_sep(a):
    return [eval(bit) for bit in a.split()]
Y = []
Z = 0
