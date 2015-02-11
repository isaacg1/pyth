import copy
import fractions
from itertools import *
from math import *
from random import *
from re import *
import string
import sys
import collections


# Type checking - num class
def isnum(a):
    return isinstance(a, int) or isinstance(a, float)


# Function library. See data for letter -> function correspondences.
# !. All.
def Pnot(a):
    return not a


# @.
def lookup(a, b):
    if isinstance(a, dict):
        return a[b]
    else:
        if isinstance(b, int):
            return a[b % len(a)]
        else:
            intersection = filter(lambda b_elm: b_elm in a, b)
            if isinstance(a, str):
                return ''.join(intersection)
            else:
                return list(intersection)


# %. int, str.
def mod(a, b):
    if isinstance(a, int) and not isnum(b):
        return b[::a]
    return a % b


# ^. int, str, list. Uses Psum
def Ppow(a, b):
    if isnum(a):
        return pow(a, b)
    else:
        if isinstance(a, str):
            return [''.join(group) for group in product(a, repeat=b)]
        elif isinstance(a, list):
            return [list(group) for group in product(a, repeat=b)]
        elif isinstance(a, set):
            return [set(group) for group in product(a, repeat=b)]
        else:
            return [group for group in product(a, repeat=b)]


# *. int, str, list.
def times(a, b):
    if isinstance(a, collections.Iterable) and \
       isinstance(b, collections.Iterable):
        return list(product(a, b))
    else:
        return a*b


# (. All types
def Ptuple(*a):
    return a


# -. int, set.
def minus(a, b):
    if isnum(a) and isnum(b):
        return a-b
    if isnum(a) and isinstance(b, str):
        return minus(str(a), b)
    if isnum(a) and isinstance(b, list):
        return minus([a], b)
    if isnum(a) and isinstance(b, set):
        return minus({a}, b)
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


# {. All.
def Pset(a):
    if isnum(a):
        return set([a])
    else:
        return set(a)


# +. All.
def plus(a, b):
    if isinstance(a, list) and not isinstance(b, list):
        return a+[b]
    if isinstance(a, set):
        return a.union(b)
    if isinstance(b, list) and not isinstance(a, list):
        return [a]+b
    if isinstance(a, tuple) and not isinstance(b, tuple):
        return a+(b,)
    if isinstance(b, tuple) and not isinstance(a, tuple):
        return b+(a,)
    return a+b


# =. All.
copy = copy.deepcopy


# [. All.
def Plist(*a):
    return list(a)


# :. list.
def at_slice(a, b, c):
    if isinstance(b, str):
        if not isinstance(c, str):
            return bool(search(b, a))
        else:
            return sub(b, c, a)
    return a[slice(b, c)]


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


## a. All
#def Pand(a, b):
#    if isinstance(a, int):
#        return a & b
#    else:
#        intersection = set(a) & set(b)
#        if isinstance(a, str):
#            return ''.join(sorted(intersection))
#        if isinstance(a, list):
#            return list(sorted(intersection))
#        else:
#            return intersection
b = "\n"


# c. All
def chop(a, b=None):
    if isnum(a):
        return a/b
    if isinstance(b, str):
        return a.split(b)
    if b is None:
        return a.split()
    return list(map(lambda d: a[b*d:b*(d+1)], range(ceil(len(a)/b))))


# C. int, str.
def Pchr(a):
    if isinstance(a, int):
        return chr(a)
    if isinstance(a, str):
        return ord(a[0])
    return list(zip(*a))


d = ' '


# e. All.
def end(a):
    if isnum(a):
        return a % 10
    return a[-1]


# f. single purpose.
def Pfilter(a, b):
    if isnum(b):
        return next(filter(a, count(b)))
    else:
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
def base_10(a, b):
    if isinstance(a, str):
        return int(a, b)
    if isinstance(a, list):
        return to_base_ten(a, b)
    if isinstance(a, int):
        return fractions.gcd(a, b)


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
    if isinstance(a, int):
        return from_base_ten(a, b)
    return a.join(list(map(lambda N: str(N), b)))


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
    if isnum(a):
        return log(a, 2)
    else:
        return len(a)


# m. Single purpose.
def Pmap(a, b):
    if isinstance(b, int):
        return list(map(a, range(b)))
    return list(map(a, b))
N = '"'


# n. All.
def ne(a, b):
    return a != b


# O. int, str, list
def rchoice(a):
    if isinstance(a, int):
        return choice(urange(a))
    return choice(list(a))


# o. Single purpose.
def order(a, b):
    if isinstance(b, str):
        return ''.join(sorted(b, key=a))
    return sorted(b, key=a)


def isprime(num):
    return all(num % div != 0 for div in range(2, int(num ** .5 + 1)))


# P. int, str, list.
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
    return a[:-1]


# p. All.
def Pprint(a, b=""):
    print(b, end=a)
    return 0


# q. All.
def equal(a, b):
    return a == b


# r. int, int or str,int.
def Prange(a, b=None):
    if isinstance(a, str) and isinstance(b, int):
        if not b:
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
            return [eval(part) for part in a.split()]
    if isinstance(a, int):
        if a < b:
            return list(range(a, b))
        else:
            return list(range(b, a))[::-1]


# s. int, str, list.
def Psum(a):
    if isinstance(a, list) or isinstance(a, tuple):
        return reduce(lambda b, c: b+c, a[1:], a[0])
    else:
        return int(a)


def Psorted(a):
    if isinstance(a, str):
        return ''.join(sorted(a))
    else:
        return sorted(a)
T = 10


# t. int, str, list.
def tail(a):
    if isnum(a):
        return a-1
    return a[1:]


# u. single purpose
def reduce(a, b, c):
    # Reduce
    if isinstance(b, collections.Iterable):
        acc = c
        seq = b
        while len(seq) > 0:
            h = seq[0]
            acc = a(acc, h)
            seq = seq[1:]
        return acc
    # Fixed point / increasing sequence
    else:
        counter = 0
        old_acc = c
        acc = a(c, counter)
        while old_acc != acc:
            counter += 1
            old_acc = acc
            acc = a(acc, counter)
        return acc


# U. int, str, list.
def urange(a):
    if isinstance(a, int):
        return list(range(a))
    if isinstance(a, tuple) and len(a) == 2:
        return list(range(a[0], a[1]))
    return list(range(len(a)))


# X.
def assign_at(a, b, c):
    # Assign at
    if isinstance(a, dict):
        a[b] = c
        return a
    if isnum(b):
        if isinstance(a, list):
            a[b % len(a)] = c
            return a
        if isinstance(a, str):
            return a[:b % len(a)] + str(c) + a[(b % len(a))+1:]
    # Translate
    if isinstance(a, str) and isinstance(b, str) or \
       isinstance(a, list) and isinstance(b, list):
        def trans_func(element):
            return c[b.index(element)] if element in b else element
        translation = map(trans_func, a)
        if isinstance(c, str):
            return ''.join(translation)
        else:
            return list(translation)
    # += in a list, X<int><list><any>
    if isinstance(b, list):
        b[a % len(b)] += c
        return b
    # += in a dict, X<any><dict><any>
    if isinstance(b, dict):
        b[a] += c
        return b


# x. int, str, list.
def index(a, b):
    if isinstance(a, int):
        return a ^ b
    if b in a:
        return a.index(b)
    # replicate functionality from str.find
    else:
        return -1


# y. string, list.
def subsets(a):
    if isnum(a):
        return a*2
    else:
        if len(a) == 1:
            return [[] if not isinstance(a, str) else '', a]
        else:
            def to_type(elem):
                return [elem] if not isinstance(a, str) else elem
            others = subsets(a[:-1])
            out = others + list(map(lambda sub: sub + to_type(a[-1]), others))
            return sorted(out, key=len)

Y = []
Z = 0
