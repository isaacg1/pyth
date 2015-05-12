no_init_paren = ('f', 'm', 'o', 'u', '.e', '.m', '.M', '.U')
end_statement = ('B', 'R', '.u')
variables = 'bdGHkNQTYzZ'

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
    'D': (('@memoized\ndef ', ':'), 1),
    'E': (('else:', ), 0),
    'F': (('for ', ' in num_to_range(', '):'), 2),
    'I': (('if ', ':'), 1),
    'W': (('while ', ':'), 1),
    '#': (('while True:\n try:', '\n except Exception:\n  break'), 0, 1),
    }

# Arbitrary format operators - use for assignment, infix, etc.
# All surrounding strings, arity
c_to_i = {
    '~':  (('', '+=', ''), 2),
    '=':  (('assign(\'', '\',', ')'), 2),
    '&':  (('(', ' and ', ')'), 2),
    '|':  (('(', ' or ', ')'), 2),
    ']':  (('[', ']'), 1),
    '}':  (('(', ' in ', ')'), 2),
    '?':  (('(', ' if ', ' else ', ')'), 3),
    ',':  (('(', ',', ')'), 2),
    'B':  (('break', ), 0),
    'J':  (('assign("J",', ')'), 1),
    'K':  (('assign("K",', ')'), 1),
    'R':  (('return ', ''), 1),
    '.*': (('*(', ')'), 1),
    '.u': (('*(', ')'), 1),
    '.)': (('', '.pop()'), 1),
    '.(': (('', '.pop(', ')'), 2),
    '.=': (('assign(\'', '\',', ')'), 2),
    }

# Simple functions only.
# Extensible is allowed, nothing else complicated is.
# -1 means extensible
# name,arity
c_to_f = {
    '`': ('repr', 1),
    '!': ('Pnot', 1),
    '@': ('lookup', 2),
    '%': ('mod', 2),
    '^': ('Ppow', 2),
    '*': ('times', 2),
    '(': ('Ptuple', -1),
    '-': ('minus', 2),
    '_': ('neg', 1),
    '+': ('plus', 2),
    '[': ('Plist', -1),
    '{': ('Pset', 1),
    "'": ('read_file', 1),
    ':': ('at_slice', 3),
    '<': ('lt', 2),
    '>': ('gt', 2),
    '/': ('div', 2),
    ' ': ('', 1),
    '\n': ('', 1),
    'a': ('append', 2),
    'C': ('Pchr', 1),
    'c': ('chop', 2),
    'e': ('end', 1),
    'f': ('Pfilter(lambda T:', 2),
    'g': ('gte', 2),
    'h': ('head', 1),
    'i': ('base_10', 2),
    'j': ('join', 2),
    'l': ('Plen', 1),
    'm': ('Pmap(lambda d:', 2),
    'n': ('ne', 2),
    'O': ('rchoice', 1),
    'o': ('order(lambda N:', 2),
    'P': ('primes_upper', 1),
    'p': ('Pprint', 2),
    'q': ('equal', 2),
    'r': ('Prange', 2),
    'S': ('Psorted', 1),
    's': ('Psum', 1),
    't': ('tail', 1),
    'U': ('urange', 1),
    'u': ('reduce(lambda G, H:', 3),
    'v': ('eval', 1),
    'w': ('input', 0),
    'X': ('assign_at', 3),
    'x': ('index', 2),
    'y': ('subsets', 1),
    '.A': ('all', 1),
    '.a': ('abs', 1),
    '.B': ('Pbin', 1),
    '.c': ('combinations', 2),
    '.C': ('combinations_with_replacement', 2),
    '.d': ('dict', 1),
    '.D': ('divmod', 2),
    '.E': ('any', 1),
    '.e': ('Penumerate(lambda k, Y:', 2),
    '.f': ('float', 1),
    '.F': ('Pformat', 2),
    '.H': ('Phex', 1),
    '.h': ('Phash', 1),
    '.i': ('interleave', 2),
    '.j': ('Pcomplex', 2),
    '.l': ('log', 2),
    '.m': ('minimal(lambda b:', 2),
    '.M': ('maximal(lambda Z:', 2),
    '.n': ('Pnumbers', 1),
    '.O': ('Poct', 1),
    '.p': ('permutations', 1),
    '.P': ('permutations2', 2),
    '.q': ('Pexit', 0),
    '.Q': ('eval_all_input', 0),
    '.r': ('rotate', 2),
    '.R': ('Pround', 2),
    '.S': ('shuffle', 1),
    '.s': ('stripchars', 2),
    '.t': ('trig', 2),
    '.U': ('reduce2(lambda b, Z:', 2),
    '.w': ('Pwrite', 2),
    '.x': ('product', 1),
    '.z': ('all_input', 0),
    '.^': ('pow', 3),
    '.&': ('bitand', 2),
    '.|': ('bitor', 2),
    '.<': ('leftshift', 2),
    '.>': ('rightshift', 2),
    '._': ('sign', 1),
    '.-': ('remove', 2),
    '.:': ('substrings', 2),
    '.{': ('unique', 1),
    }

replacements = {
    '\\': ('"{0}"', 1),
    'V': ('FNU', 0),
    'A': ('=,{0}{1}', 2),
    'L': ('DybR', 0),
    'M': ('DgGHR', 0),
    '.N': ('D:NTYR', 0),
    }

#Provides parsing functions and arity conditions for syntactical sugar
#<non-zero>=: Augmented assignment
#<binary>F: Fold operator

syntax_sugar = {
    '=': (lambda c, r: r[:2] + c+r[1:], lambda n: n),
    'F': (lambda c, r: ".U" + c + c_to_f['.U'][0][15:19:3] + r[1:],
          lambda n: n == 2)
}

# Gives next function header to use - for filter, map, reduce.
# map: d, k, b
# filter: T, Y, Z
# order: N, Z,
# reduce: (G,H), (N,T)
# enumerate: (k, Y), (b, Z)

next_c_to_f = {
    'f': [('Pfilter(lambda Y:', 2), ('Pfilter(lambda Z:', 2), ],
    'm': [('Pmap(lambda k:', 2), ('Pmap(lambda b:', 2), ],
    'o': [('order(lambda Z:', 2), ],
    'u': [('reduce(lambda N, T:', 3), ],
    '.e': [('Penumerate(lambda b, Z:', 2), ],
    '.U': [('reduce2(lambda k, Y:', 2), ],
    }

# For autoinitializers. One shot, not rotating.
next_c_to_i = {
    'J': (('J'), 0),
    'K': (('K'), 0),
    }

# Prependers.
prepend = {
    'Q': "=Qvw",
    'z': "=zw",
    }
