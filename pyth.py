############################################################################
#                            Pyth version 1.0.6                            #
#                          Posted before 7-7-2014                          #
# Added correct incarnations of J and K to print list. Changed O to be     #
# random sample. Made comma the pairing function - ,(_,_) -> (_,_).        #
# Added one argument range - L. lte removed, because gte exists. Added     #
# the original code to the debug output. Numeric literals of over one      #
# character must be prependeded with .                                     #
#                                                                          #
# This python program is an interpreter for the pyth programming language. #
# It is still in development - expect new versions often.                  #
#                                                                          #
# To use, provide pyth code on one line of stdin.                          #
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

def parse(code,spacing="\n "):
    assert type(code)==type('')
    # If we've reached the end of the string, give up.
    if len(code)==0:
        return '',''
    # Separate active character from the rest of the code.
    active_char=code[0]
    rest_code=code[1:]
    # Deal with numbers
    if active_char == ".":
        output=""
        while (len(rest_code)>0
               and rest_code[0] in ".0123456789"
               and (output+rest_code[0]).count(".")<=1):
            output+=rest_code[0]
            rest_code=rest_code[1:]
        return output,rest_code
    if active_char in ".0123456789":
        return active_char,rest_code
    # String literals
    if active_char=='"':
        output=active_char
        while (len(rest_code)>0
               and output.count('"')<2):
            output+=rest_code[0]
            rest_code=rest_code[1:]
        if output[-1]!='"':
            output+='"'
        return output,rest_code
    # Python code literals
    if active_char=='$':
        output=''
        while (len(rest_code)>0
               and rest_code[0]!='$'):
            output+=rest_code[0]
            rest_code=rest_code[1:]
        return output,rest_code[1:]
    # End paren is magic.
    if active_char==')':
        return '',rest_code
    # Backslash is more magic.
    if active_char=='\\':
        if rest_code=='':
            return '',''
        else:
            return '','\\'+rest_code
    # Designated variables
    if active_char in variables:
        return active_char,rest_code
    # Now for the two letter variables/functions
    if active_char=='#':
        assert len(rest_code)>0
        return rest_code[0]*2,rest_code[1:]
    # And for general functions
    global c_to_f
    global next_c_to_f
    if active_char in c_to_f:
        func_name,arity=c_to_f[active_char]
        init_paren = (active_char not in no_init_paren)
        # Swap what variables are used in the map, filter or reduce.
        if active_char in next_c_to_f:
            temp=c_to_f[active_char]
            c_to_f[active_char]=next_c_to_f[active_char][0]
            next_c_to_f[active_char]=next_c_to_f[active_char][1:]+[temp]
        # Recurse until terminated by end paren or EOF
        # or received enough arguments
        args_list=[]
        parsed='Not empty'
        while len(args_list) != arity and parsed != '':
            parsed,rest_code=parse(rest_code)
            args_list.append(parsed)
        # Build the output string.
        py_code=func_name
        if init_paren:
            py_code+='('
        if len(args_list)>0 and args_list[-1]=='':
            args_list=args_list[:-1]
        py_code+=','.join(args_list)
        py_code+=')'
        return py_code,rest_code
    # General format functions/operators
    global c_to_i
    if active_char in c_to_i:
        infixes,arity=c_to_i[active_char]
        # Make J and K into normal variables, if necessary.
        if active_char in next_c_to_i:
            c_to_i[active_char]=next_c_to_i[active_char]
        args_list=[]
        parsed='Not empty'
        while len(args_list) != arity and parsed != '':
            parsed,rest_code=parse(rest_code)
            args_list.append(parsed)
        # Statements that cannot have anything after them
        if active_char in end_statement:
            rest_code=")"+rest_code
        py_code=infixes[0]
        for i in range(len(args_list)):
            py_code+=args_list[i]
            py_code+=infixes[i+1]
        return py_code, rest_code
    # Statements:
    if active_char in c_to_s:
        # Handle the initial portion (head)
        infixes,arity=c_to_s[active_char]
        args_list=[]
        parsed='Not empty'
        while len(args_list) != arity and parsed != '':
            parsed,rest_code=parse(rest_code)
            args_list.append(parsed)
        part_py_code=infixes[0]
        for i in range(len(args_list)):
            part_py_code+=args_list[i]
            part_py_code+=infixes[i+1]
        # Handle the body - ends object as well.
        assert rest_code != ''
        args_list=[]
        parsed='Not empty'
        while parsed != '':
            # Prepend print to any line starting with a function, var or safe infix.
            if len(rest_code)>0:
                if ((rest_code[0] not in 'p ' and rest_code[0] in c_to_f) or
                rest_code[0] in variables or
                (rest_code[0] in 'JK' and c_to_i[rest_code[0]]==next_c_to_i[rest_code[0]]) or
                rest_code[0] in "@&|]'?;\".0123456789#,"):
                    rest_code='p"\\n"'+rest_code
            parsed,rest_code=parse(rest_code,spacing+' ')
            args_list.append(parsed)
        # Trim the '' away and combine.
        if args_list[-1]=='':
            args_list=args_list[:-1]
        all_pieces=[part_py_code]+args_list
        return spacing.join(all_pieces),rest_code
    print("Something's wrong.")
    print("Current char is ",active_char)
    print("The rest of the code is ",rest_code)
    raise NotImplementedError

import random
import copy
import string
# Function library, descriptions of everything.
# +=                                # ~     Y - Sets
# repr                              # `     Y - General
def _not(a):return not a            # !     Y - General
# _[_]                              # @     Y - Ints
# # is special - 2 character variable       Y - General
# $ is special - python literal             Y - General
def mod(a,b):return a%b             # %     Y - Lists, Sets
# pow                               # ^     Y - non num
# and                               # &     Y - General
def times(a,b):return a*b           # *     Y - sets
def _tuple(*a):return a             # (     Y - general
# ) is special - end extensible             Y - general
def minus(a,b):
    if type(a)==type(set()):
        return a.difference(b)
    return a-b                      # -     Y
def neg(a):                         # _     Y
        return -a
def plus(a,b):
    if type(a)==type(set()):
        return a.union(b)
    if type(b)==type(set()):
        return b.union(a)
    return a+b                      # +     Y
# = deepcopy                        # =     Y
copy = copy.deepcopy
def _list(*a):return list(a)        # [     Y
# set                               # {     Y
# [_]                               # ]     Y
# in                                # }     Y
# or                                # |     Y
# break out of all containing       # )     Y
def at_slice(a,b,c=None):           # :     Y
    if c:
        return a[slice(b,c)]
    else:
        return a[slice(b)]
# _.pop()                           # ;     Y
def head(a):return a[0]             # '     Y
# " is special - string literal             Y
# Pairing                           # ,     Y
def lt(a,b):                        # <     Y
    if type(a)==type(set()):
        return a.issubset(b) and a!=b
    return a<b
# . is special - numbers            # .     Y
def gt(a,b):                        # >     Y
    if type(a)==type(set()):
        return a.issuperset(b) and a!=b
    return a>b
def div(a,b):return a//b            # /     Y
# if else                           # ?     Y
# 0-9 are special - numbers         # 0-9   Y
# (x)                               #| |    Y
# all                               # A     Y
# .append()                         # a     Y
# break                             # B     Y
b="\n"                              # b     Y
# chr                               # C     Y
def _chr(a):
    if type(a)==type(0):
        return chr(a)
    if type(a)==type(''):
        return ord(a[0])
def count(a,b):return a.count(b)    # c     Y
# def                               # D     Y
# variable - associated with map    # d     Y
d=' '
# else                              # E     Y
def lower(a):return a.lower()       # e     Y
# for                               # F     Y
def _filter(a,b):                   # f     Y
    return list(filter(a,b))
# variable - associated with reduce # G     Y
G=string.ascii_lowercase
def gte(a,b):                       # g     Y
    if type(a)==type(set()):
        return a.issuperset(b)
    return a>=b
# variable - associated with reduce # H     Y
H={}
def read_file():                    # h     Y
    a="\n".join(open(input()))
    return a
# h assigns the text of the user 
# inputted file to the variable given.
# if                                # I     Y
def _round(a,b=None):               # i     Y
    if b is None:
        return float(a)
    if b is 0:
        return int(a)
    return round(a,b)
# Autoinitializing variable         # J     Y
def join(a,b):                      # j     Y
    return a.join(list(map(lambda N:str(N),b)))
# Autoinitializing variable         # K     Y
k=''                                # k     Y
def lrange(a):                      # L     Y
    if type(a)==type(0):
        return list(range(a))
    return list(range(len(a)))
# len                               # l     Y
# max                               # M     Y
def _map(a,b):return list(map(a,b)) # m     Y
N=None                              # N     Y
# min                               # n     Y
def rchoice(a):                     # O     Y
    return random.choice(list(a))
# order (sorted with key)           # o     Y
def order(a,b):
    if type(b)==type(''):
        return ''.join(sorted(b, key=a))
    return sorted(b, key=a)
def split(a,b=None):                # P     Y
    if b:
        return a.split(b)
    else:
        return a.split()
def _print(a,b=""):                 # p     Y
    print(b,end=a)
def quotient(a,b):return a/b        # Q     Y
def equal(a,b):return a==b          # q     Y
# return                            # R     Y
def _range(a,b=None):               # r     Y
    if b:
        return list(range(a,b))
    else:
        return list(range(a))
# sorted                            # S     Y
def _sum(a):
    return reduce(lambda b,c:b+c,a) # s     Y
# T is associated with filter       # T     Y
T=10
def tail(a):return a[1:]            # t     Y
def upper(a):return a.upper()       # U     Y
def reduce(a,b):                    # u     Y
    acc=b[0]
    seq=b[1:]
    while len(seq)>0:
        h=seq[0]
        acc=a(acc,h)
        seq=seq[1:]
    return acc
def rev(a): return a[::-1]          # V     Y
# eval(parse                        # v     Y
# while                             # W     Y
# input                             # w     Y
def index(a,b):                     # X     Y
    if b in a:
        return a.index(b)
    # replicate functionality from str.find
    else:
        return -1
# exec(general_parse                # x     Y
Y=[]                                # Y     Y
# any                               # y     Y
Z=0                                 # Z     Y
def _zip(a,b):return list(zip(a,b)) # z     Y

no_init_paren='fmou'
end_statement='BR'
variables='bdGHkNTYZ'

# To do: even preassociated variables deserve to be initialized.
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

c_to_s={
    'D':(('def ',':'),1),
    'E':(('else:'),0),
    'F':(('for ',' in ',':'),2),
    'I':(('if ',':'),1),
    'W':(('while ',':'),1),
    }
# Arbitrary format operators - use for assignment, infix, etc.
# All surrounding strings, arity
c_to_i={
    '~':(('','+=',''),2),
    '@':(('','[',']'),2),
    '&':(('(',' and ',')'),2),
    '|':(('(',' or ',')'),2),
    '=':(('','=copy(',')'),2),
    ']':(('[',']'),1),
    '}':(('(',' in ',')'),2),
    '?':(('(',' if ',' else ',')'),3),
    ',':(('(',',',')'),2),
    ';':(('','.pop()',),1),
    'a':(('','.append(',')'),2),
    'B':(('break',),0),
    'J':(('J=copy(',')'),1),
    'K':(('K=',''),1),
    'R':(('return ',''),1),
    'x':(('exec(general_parse(','))'),1),
    }

# Simple functions only.
# Extensible is allowed, nothing else complicated is.
# -1 means extensible
# name,arity
c_to_f={
    '`':('repr',1),
    '!':('_not',1),
    '%':('mod',2),
    '^':('pow',2),
    '*':('times',2),
    '(':('_tuple',-1),
    '-':('minus',2),
    '_':('neg_1r',1),
    '+':('plus',2),
    '[':('_list',-1),
    '{':('set',1),
    "'":('head',1),
    ':':('at_slice',3),
    '<':('lt',2),
    '>':('gt',2),
    '/':('div',2),
    ' ':('',1),
    '\t':('',1),
    'A':('all',1),
    'C':('_chr',1),
    'c':('count',2),
    'e':('lower',1),
    'f':('_filter(lambda T:',2),
    'g':('gte',2),
    'h':('read_file',0),
    'i':('_round',2),
    'j':('join',2),
    'L':('lrange',1),
    'l':('len',1),
    'M':('max',1),
    'm':('_map(lambda d:',2),
    'O':('rchoice',1),
    'o':('order(lambda N:',2),
    'P':('split',2),
    'p':('_print',2),
    'Q':('quotient',2),
    'q':('equal',2),
    'r':('_range',2),
    'S':('sorted',1),
    's':('_sum',1),
    't':('tail',1),
    'U':('upper',1),
    'u':('reduce(lambda G,H:',2),
    'V':('rev',1),
    'v':('eval',1),
    'w':('input',0),
    'X':('index',2),
    'z':('_zip',2),
    }

# Gives next function header to use - for filter, map, reduce.
# map: d, k, b
# filter: T, Y, Z
# reduce: (G,H), (N,T)

next_c_to_f={
    'f':[('_filter(lambda Y:',2), ('_filter(lambda Z:',2),],
    'm':[('_map(lambda k:',2), ('_map(lambda b:',2),],
    'o':[('order(lambda Z:',2),],
    'u':[('reduce(lambda N,T:',2),],
    }

# For autoinitializers. One shot, not rotating.
next_c_to_i={
    'J':(('J'),0),
    'K':(('K'),0),
    }
    
assert set(c_to_f.keys())&set(c_to_i.keys())==set()
# Run it!
def general_parse(code):
    args_list=[]
    parsed='Not empty'
    while parsed != '':
        # Prepend print to any line starting with a function, var or safe infix.
        if len(code)>0:
            if ((code[0] not in 'p ' and code[0] in c_to_f) or
            code[0] in variables or
            (code[0] in 'JK' and c_to_i[code[0]]==next_c_to_i[code[0]]) or
            code[0] in "@&|]'?;\".0123456789#,"):
                code='p"\\n"'+code
        parsed,code=parse(code)
        # Necessary for backslash not to infinite loop
        if code and code[0]=='\\':
            code=code[1:]
        args_list.append(parsed)
    # Build the output string.
    py_code='\n'.join(args_list[:-1])
    return py_code
code=input()
print(code)
py_code=general_parse(code)
print(py_code)
print('='*50)
exec(py_code)
