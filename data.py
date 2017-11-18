lambda_f = ('f', 'm', 'o', 'u', '.b', '.e', '.f', '.g', '.I',
            '.m', '.M', '.u', '.U')
end_statement = ('B', 'R', '.*')
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
    'D': ('@memoized\ndef {0}:{1}', 1),
    'D without memoization': ('def {0}:{1}', 1),
    'F': ('for {0} in num_to_range({1}):{2}', 2),
    'I': ('if {0}:{1}', 1),
    'W': ('while {0}:{1}', 1),
    '#': ('while True:\n try:{0}\n except Exception:\n  break', 0, 1),
    '.V': ('for b in infinite_iterator({0}):{1}', 1),
    'else': ('else:{0}', 0),
}

# Arbitrary format operators - use for assignment, infix, etc.
# All surrounding strings, arity
c_to_i = {
    '=': ('assign(\'{0}\',{1})', 2),
    '~': ('post_assign(\'{0}\',{1})', 2),
    '&': ('({0} and {1})', 2),
    '|': ('({0} or {1})', 2),
    '?': ('({1} if {0} else {2})', 3),
    ',': ('[{0},{1}]', 2),
    'B': ('break', 0),
    'J': ('assign("J",{0})', 1),
    'K': ('assign("K",{0})', 1),
    'R': ('return {0}', 1),
    '.W': ('apply_while(lambda H:{0}, lambda Z:{1}, {2})', 3),
    '.x': ('Pexcept(lambda:{0}, lambda:{1})', 2),
    '.*': ('*({0})', 1),
    '.)': ('{0}.pop()', 1),
    '.(': ('{0}.pop({1})', 2),
}

# Simple functions only.
# Extensible is allowed, nothing else complicated is.
# name,arity
c_to_f = {
    '`': ('repr', 1),
    '!': ('Pnot', 1),
    '@': ('lookup', 2),
    '%': ('mod', 2),
    '^': ('Ppow', 2),
    '*': ('times', 2),
    '(': ('Ptuple', float("inf")),
    '-': ('minus', 2),
    '_': ('neg', 1),
    '+': ('plus', 2),
    '[': ('Plist', float("inf")),
    ']': ('singleton', 1),
    '{': ('uniquify', 1),
    '}': ('Pin', 2),
    "'": ('read_file', 1),
    ':': ('at_slice', 3),
    '<': ('lt', 2),
    '>': ('gt', 2),
    '/': ('div', 2),
    ' ': ('', 1),
    '\n': ('imp_print', 1),
    'a': ('append', 2),
    'C': ('Pchr', 1),
    'c': ('chop', 2),
    'E': ('eval_input', 0),
    'e': ('end', 1),
    'f': ('Pfilter', 2),
    'g': ('gte', 2),
    'h': ('head', 1),
    'i': ('base_10', 2),
    'j': ('join', 2),
    'l': ('Plen', 1),
    'm': ('Pmap', 2),
    'n': ('ne', 2),
    'O': ('rchoice', 1),
    'o': ('order', 2),
    'P': ('primes_pop', 1),
    'p': ('Pprint', 1),
    'q': ('equal', 2),
    'r': ('Prange', 2),
    'S': ('Psorted', 1),
    's': ('Psum', 1),
    't': ('tail', 1),
    'U': ('urange', 1),
    'u': ('reduce', 3),
    'v': ('Punsafe_eval', 1),
    'w': ('input', 0),
    'X': ('assign_at', 3),
    'x': ('index', 2),
    'y': ('subsets', 1),
    '.A': ('all', 1),
    '.a': ('Pabs', 1),
    '.B': ('Pbin', 1),
    '.b': ('binary_map', 3),
    '.c': ('combinations', 2),
    '.C': ('combinations_with_replacement', 2),
    '.d': ('dict_or_date', 1),
    '.D': ('divmod_or_delete', 2),
    '.E': ('Pany', 1),
    '.e': ('Penumerate', 2),
    '.f': ('first_n', 3),
    '.F': ('Pformat', 2),
    '.g': ('group_by', 2),
    '.H': ('Phex', 1),
    '.h': ('Phash', 1),
    '.i': ('interleave', 2),
    '.I': ('invert', 2),
    '.j': ('Pcomplex', 2),
    '.l': ('log', 2),
    '.m': ('minimal', 2),
    '.M': ('maximal', 2),
    '.n': ('Pnumbers', 1),
    '.O': ('Poct', 1),
    '.p': ('permutations', 1),
    '.P': ('permutations2', 2),
    '.q': ('Pexit', 0),
    '.Q': ('eval_all_input', 0),
    '.r': ('rotate', 2),
    '.R': ('Pround', 2),
    '.S': ('shuffle', 1),
    '.s': ('Pstrip', 2),
    '.t': ('trig', 2),
    '.T': ('transpose', 1),
    '.U': ('reduce2', 2),
    '.u': ('cu_reduce', 3),
    '.v': ('pyth_eval', 1),
    '.w': ('Pwrite', 2),
    '.y': ('all_subset_orders', 1),
    '.z': ('all_input', 0),
    '.Z': ('compress', 1),
    '."': ('packed_str', 1),
    '.^': ('pow', 3),
    '.&': ('bitand', 2),
    '.|': ('bitor', 2),
    '.<': ('leftshift', 2),
    '.>': ('rightshift', 2),
    './': ('partition', 1),
    '._': ('sign', 1),
    '.-': ('remove', 2),
    '.+': ('deltas', 1),
    '.:': ('substrings', 2),
    '.{': ('Pset', 1),
    '.!': ('factorial', 1),
    '.[': ('pad', 3),
}

optional_final_args = {
    ':': 1,
    'c': 1,
    'f': 1,
    'j': 1,
    'u': 1,
    'X': 1,
    '.b': 1,
    '.f': 1,
    '.j': 2,
    '.l': 1,
    '.u': 1,
    '.w': 1,
    '.:': 1,
    '.{': 1,
    '.t': 1,
}

replacements = {
    'V': [['F', 'N'], ['F', 'H'], ['F', 'b'], ],
    'A': [['=', ',', 'G', 'H'], ],
    'L': [['D', 'y', 'b', 'R'], ['D', "'", 'b', 'R'], ],
    'M': [['D', 'g', 'G', 'H', 'R'], ['D', 'n', 'G', 'H', 'R'], ],
    '.N': [['D', ':', 'N', 'T', 'Y', 'R'], ['D', 'X', 'N', 'T', 'Y', 'R'], ],
    '.?': [[')', 'else'], ],
}

rotate_back_replacements = ('V',)


# Gives next function header to use - for filter, map, reduce.

lambda_vars = {
    'f': ['T', 'Y', 'Z'],
    'm': ['d', 'k', 'b'],
    'o': ['N', 'Z'],
    'u': ['G, H', 'N, T'],
    '.b': ['N, Y'],
    '.e': ['k, b', 'Y, Z'],
    '.f': ['Z'],
    '.g': ['k'],
    '.I': ['G'],
    '.m': ['b'],
    '.M': ['Z'],
    '.u': ['N, Y'],
    '.U': ['b, Z', 'k, Y'],
}

# For autoinitializers. One shot, not rotating.
next_c_to_i = {
    'J': (('J'), 0),
    'K': (('K'), 0),
}

# Prependers.
prepend = {
    'Q': ["=", "Q", "E"],
    'z': ["=", "z", "w"],
}
