#!/usr/bin/env python3
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
import copy as c
import sys
import io
import cmd
import traceback

from extra_parse import PythParseError, UnsafeInputError, str_parse_next
from macros import environment, BadTypeCombinationError, memoized
from data import lambda_f, end_statement, variables, c_to_s, c_to_i, c_to_f, \
    optional_final_args, replacements, rotate_back_replacements, lambda_vars, \
    next_c_to_i, prepend
from lexer import lex

sys.setrecursionlimit(100000)

lambda_stack = []
preps_used = set()
state_maintaining_depth = 0

# Parse it!


def general_parse(code, safe_mode):
    # Parsing
    args_list = []
    tokens = lex(code)
    while tokens != []:
        to_print = add_print(tokens)
        parsed, tokens = parse(tokens, safe_mode)
        if to_print:
            parsed = 'imp_print(' + parsed + ')'
        # Finish semicolon parsing
        if tokens and tokens[0] == ';':
            tokens = tokens[1:]
        args_list.append(parsed)
    # Build the output string.
    args_list = add_preps(preps_used, safe_mode) + args_list
    py_code = '\n'.join(args_list)
    return py_code


def parse(tokens, safe_mode, spacing="\n "):
    assert isinstance(tokens, list)
    # If we've reached the end of the string, finish up.
    if not tokens:
        if lambda_stack:
            return lambda_stack[-1], []
        else:
            preps_used.add('Q')
            return 'Q', []
    # Separate active character from the rest of the code.
    active_token = tokens[0]
    rest_tokens = tokens[1:]
    assert isinstance(active_token, str)
    # Deal with numbers
    if active_token == '.':
        raise PythParseError(active_token, rest_tokens)
    if active_token[0] in "0123456789"\
       or active_token[0] == '.' and active_token[1] in "0123456789":
        return active_token, rest_tokens
    # String literals
    if active_token[0] == '"':
        return str_parse_next(active_token), rest_tokens
    if active_token[:2] == '."':
        string = str_parse_next(active_token[1:])
        return "%s(%s)" % (c_to_f['."'][0], string), rest_tokens
    # Python code literals
    if active_token[0] == '$':
        if safe_mode:
            raise UnsafeInputError(active_token, rest_tokens)
        else:
            return active_token.strip('$'), rest_tokens
    # End paren is magic (early-end current function/statement).
    if active_token == ')':
        return '', rest_tokens
    if active_token == ';':
        # Inside a lambda, return the innermost lambdas leading variable.
        if lambda_stack or state_maintaining_depth:
            return 'env_lookup({!r})'.format((lambda_stack or ['Q'])[-1]), rest_tokens
        # Semicolon is more magic (early-end all active functions/statements).
        if not rest_tokens:
            return '', [';']
        else:
            return '', [';'] + rest_tokens
    # Designated variables
    if active_token in variables:
        if active_token in prepend:
            preps_used.add(active_token)
        return active_token, rest_tokens
    if active_token[0] == '\\':
        if active_token[1] in '"\\':
            return '"\\%s"' % active_token[1], rest_tokens
        else:
            return '"%s"' % active_token[1], rest_tokens
    # Replace replaements
    if active_token in replacements:
        return replace_parse(active_token, rest_tokens, safe_mode, spacing)
    # Syntactic sugar handling.
    if rest_tokens and (active_token in c_to_f or active_token in c_to_i):
        sugar_char = rest_tokens[0]
        remainder = rest_tokens[1:]
        if active_token in c_to_f:
            arity = c_to_f[active_token][1]
        else:
            arity = c_to_i[active_token][1]

        # Sugar Chaining
        sugar_chars = 'FMLBRID#VW'
        sugar_active_tokens = [active_token]
        while sugar_char in sugar_chars and remainder and remainder[0] in sugar_chars:
            sugar_active_tokens += sugar_char
            sugar_char = remainder[0]
            remainder = remainder[1:]
        if arity > 0:
            if sugar_char == 'F':
                if arity == 1:
                    # Unary: Repeated application
                    rep_arg1, post1 = parse(remainder, safe_mode)
                    rep_arg2, post2 = parse(post1, safe_mode)
                    func, rest = parse(sugar_active_tokens + ['b'], safe_mode)
                    assert not rest, "Sugar parse F repeat failed"
                    func = "lambda b:" + func
                    return "repeat({}, {}, {})".format(func, rep_arg1, rep_arg2), post2
                if arity == 2:
                    # <binary function/infix>F: Fold operator
                    fold_list, post_fold = next_seg(remainder, safe_mode)
                    if len(sugar_active_tokens) == 1\
                            and sugar_active_tokens[0] in c_to_f\
                            and not sugar_active_tokens[0] in lambda_f:
                        parsed_list, rest = parse(fold_list, safe_mode)
                        assert not rest, "Sugar parse F fold simple failed"
                        func = c_to_f[sugar_active_tokens[0]][0]
                        return "fold({}, {})".format(func, parsed_list), post_fold
                    reduce_arg1 = lambda_vars['.U'][0][0]
                    reduce_arg2 = lambda_vars['.U'][0][-1]
                    full_fold, rest = parse([".U"] + sugar_active_tokens +
                                            [reduce_arg1, reduce_arg2] + fold_list, safe_mode)
                    assert not rest, "Sugar parse F fold failed"
                    return full_fold, post_fold
                if arity > 2:
                    # Just splat it - it's a common use case.
                    splat_list, post_splat = next_seg(remainder, safe_mode)
                    full_splat, rest = parse(sugar_active_tokens + ['.*'] + splat_list, safe_mode)
                    assert not rest, "Sugar parse F splat failed"
                    return full_splat, post_splat

            # <function>M: Map operator
            if sugar_char == 'M':
                m_arg = lambda_vars['m'][0][0]
                if arity == 1:
                    map_target, post_map = next_seg(remainder, safe_mode)
                    full_map, rest = parse(['m'] + sugar_active_tokens + [m_arg] + map_target, safe_mode)
                    assert not rest, "Sugar parse M 1 arg failed"
                    return full_map, post_map
                else:
                    map_target, post_map = next_seg(remainder, safe_mode)
                    full_map, rest = parse(['m'] + sugar_active_tokens + ['F', m_arg] + map_target, safe_mode)
                    assert not rest, "Sugar parse M 2+ args failed"
                    return full_map, post_map

            # <binary function>L<any><seq>: Left Map operator
            # >LG[1 2 3 4 -> 'm>Gd[1 2 3 4'.
            if sugar_char == 'L':
                if arity >= 2:
                    m_arg = lambda_vars['m'][0][0]
                    lmap_lambda_args, remainder = next_n_segs(arity - 1, remainder, safe_mode)
                    lmap_target, post_lmap = next_seg(remainder, safe_mode)
                    full_lmap, rest = parse(['m'] + sugar_active_tokens +
                                            lmap_lambda_args + [m_arg] + lmap_target, safe_mode)
                    assert not rest, "Sugar parse L failed"
                    return full_lmap, post_lmap

            # <function>V<seq><seq> Vectorize operator.
            # Equivalent to <func>MC,<seq><seq>.
            if sugar_char == 'V':
                vmap_target, post_vmap = next_n_segs(2, remainder, safe_mode)
                full_vmap, rest = parse(sugar_active_tokens + ['M', 'C', ','] + vmap_target, safe_mode)
                assert not rest, "Sugar parse V failed"
                return full_vmap, post_vmap

            # <function>W<condition><arg><rgs> Condition application operator.
            # Equivalent to ?<condition><function><arg><args><arg>
            if sugar_char == 'W':
                condition, rest_tokens1 = parse(remainder, safe_mode)
                arg1, _ = state_maintaining_parse(rest_tokens1, safe_mode)
                func, rest_tokens2b = parse(sugar_active_tokens + rest_tokens1, safe_mode)
                return ('(%s if %s else %s)' % (func, condition, arg1), rest_tokens2b)

            # <function>B<arg><args> -> ,<arg><function><arg><args>
            # <unary function>I<any> Invariant operator.
            # Equivalent to q<func><any><any>
            if sugar_char in 'BI':
                dup_dict = {
                    'B': '[{},{}]',
                    'I': '{}=={}',
                }
                dup_format = dup_dict[sugar_char]
                dup_parsed, _ = state_maintaining_parse(remainder, safe_mode)
                non_dup_parsed, post_dup = parse(sugar_active_tokens + remainder, safe_mode)
                return dup_format.format(dup_parsed, non_dup_parsed), post_dup

            # Right operators
            # R is Map operator
            # D is Sort operator
            # # is Filter operator - it looks like a strainer.
            if sugar_char in 'RD#':
                func_dict = {
                    'R': 'm',
                    'D': 'o',
                    '#': 'f',
                }
                func_char = func_dict[sugar_char]
                lambda_arg = lambda_vars[func_char][0][0]
                rop_args, post_rop = next_n_segs(arity, remainder, safe_mode)
                full_rop, rest = parse([func_char] + sugar_active_tokens + [lambda_arg] + rop_args, safe_mode)
                assert not rest, 'Sugar parse %s failed' % sugar_char
                return full_rop, post_rop

    # =<function/infix>, ~<function/infix>: augmented assignment.
    if active_token in ('=', '~'):
        if augment_assignment_test(rest_tokens):
            return augment_assignment_parse(active_token, rest_tokens, safe_mode)

    # And for general functions
    if active_token in c_to_f:
        if active_token in lambda_f:
            return lambda_function_parse(active_token, rest_tokens, safe_mode)
        else:
            return function_parse(active_token, rest_tokens, safe_mode)
    # General format functions/operators
    if active_token in c_to_i:
        return infix_parse(active_token, rest_tokens, safe_mode)
    # Statements:
    if active_token in c_to_s:
        return statement_parse(active_token, rest_tokens, safe_mode, spacing)
    # If we get here, the character has not been implemented.
    # There is no non-ASCII support.
    raise PythParseError(active_token, rest_tokens)


def next_seg(code, safe_mode):
    _, rest = state_maintaining_parse(code, safe_mode)
    pyth_seg = code[:len(code) - len(rest)]
    return pyth_seg, rest


def next_n_segs(n, code, safe_mode):
    if not isinstance(n, int):
        assert n == float('inf'), "arities must be either ints or infinity"
        raise RuntimeError # Can't use unbounded arity function in this context.
    global c_to_i
    global state_maintaining_depth
    saved_c_to_i = c.deepcopy(c_to_i)
    state_maintaining_depth += 1
    remainder = code
    for _ in range(n):
        _, remainder = parse(remainder, safe_mode)
    state_maintaining_depth -= 1
    c_to_i = saved_c_to_i
    return code[:len(code) - len(remainder)], remainder


def state_maintaining_parse(code, safe_mode):
    global c_to_i
    global state_maintaining_depth
    saved_c_to_i = c.deepcopy(c_to_i)
    state_maintaining_depth += 1
    py_code, rest_tokens = parse(code, safe_mode)
    state_maintaining_depth -= 1
    c_to_i = saved_c_to_i
    return py_code, rest_tokens


def augment_assignment_test(rest_tokens):
    func_token = rest_tokens[0]
    return func_token not in variables and func_token not in next_c_to_i and func_token != ','


def augment_assignment_parse(active_token, rest_tokens, safe_mode):
    following_vars = [token for token in rest_tokens if token in variables or token in next_c_to_i]
    var_token = (following_vars + ['Q'])[0]
    return parse([active_token, var_token] + rest_tokens, safe_mode)

def gather_args(active_token, rest_tokens, arity, safe_mode):
    # Recurse until terminated by end paren or EOF
    # or received enough arguments
    args_list = []
    while (len(args_list) != arity
           and not (not rest_tokens
                    and (arity == float('inf')
                         or (active_token in optional_final_args
                             and len(args_list) >= arity - optional_final_args[active_token])))):
        parsed, rest_tokens = parse(rest_tokens, safe_mode)
        if not parsed:
            break
        args_list.append(parsed)
    return args_list, rest_tokens


def lambda_function_parse(active_token, rest_tokens, safe_mode):
    func_name, arity = c_to_f[active_token]
    var = lambda_vars[active_token][0]
    # Swap what variables are used in lambda functions.
    saved_lambda_vars = lambda_vars[active_token]
    lambda_vars[active_token] = lambda_vars[active_token][1:] + [var]
    lambda_stack.append(var[0])
    # Take one argument, the lambda.
    lambda_parsed, rest_tokens = parse(rest_tokens, safe_mode)
    # Rotate back.
    lambda_vars[active_token] = saved_lambda_vars
    lambda_stack.pop()
    partial_args_list, rest_tokens = gather_args(active_token, rest_tokens, arity-1, safe_mode)
    args_list = [lambda_parsed] + partial_args_list
    py_code = '%s(lambda %s:%s)' % (func_name, var, ','.join(args_list))
    return py_code, rest_tokens


def function_parse(active_token, rest_tokens, safe_mode):
    func_name, arity = c_to_f[active_token]
    args_list, rest_tokens = gather_args(active_token, rest_tokens, arity, safe_mode)
    py_code = '%s(%s)' % (func_name, ','.join(args_list))
    return py_code, rest_tokens


def infix_parse(active_token, rest_tokens, safe_mode):
    infixes, arity = c_to_i[active_token]
    args_list = []
    # Lambda infix(es)
    if active_token == '.W':
        lambda_stack.extend(['Z', 'H'])
    while len(args_list) != arity:
        if (not rest_tokens
                and active_token in optional_final_args
                and len(args_list) >= arity - optional_final_args[active_token]):
            args_list.append('')
            break
        parsed, rest_tokens = parse(rest_tokens, safe_mode)
        if not parsed:
            break
        args_list.append(parsed)
        if active_token == '.W' and len(args_list) <= 2:
            lambda_stack.pop()
    # Statements that cannot have anything after them
    if active_token in end_statement:
        rest_tokens = [")"] + rest_tokens
    py_code = infixes.format(*args_list)
    # Advance infixes.
    if active_token in next_c_to_i:
        c_to_i[active_token] = next_c_to_i[active_token]
    return py_code, rest_tokens


def statement_parse(active_token, rest_tokens, safe_mode, spacing):
    # Handle the initial portion (head)
    # addl_spaces denotes the amount of extra spacing needed.
    if len(c_to_s[active_token]) == 2:
        infixes, arity = c_to_s[active_token]
        addl_spaces = ''
    else:
        infixes, arity, num_spaces = c_to_s[active_token]
        addl_spaces = ' ' * num_spaces
    # Handle newlines in infix segments
    infixes = infixes.replace("\n", spacing[:-1])
    args_list, rest_tokens = gather_args(active_token, rest_tokens, arity, safe_mode)
    # Handle the body - ends object as well.
    body_lines = []
    while rest_tokens:
        to_print = add_print(rest_tokens)
        parsed, rest_tokens = parse(rest_tokens, safe_mode, spacing + addl_spaces + ' ')
        if not parsed:
            break
        if to_print:
            parsed = 'imp_print(%s)' % parsed
        body_lines.append(parsed)
    if body_lines == []:
        body_lines = ['pass']
    # Combine pieces - intro, statement, conclusion.
    total_spacing = spacing + addl_spaces
    body = total_spacing + total_spacing.join(body_lines)
    args_list.append(body)
    return infixes.format(*args_list), rest_tokens


def replace_parse(active_token, rest_tokens, safe_mode, spacing):
    # Rotate replacements.
    repl_list = replacements[active_token][0]
    saved_replacements = replacements[active_token]
    replacements[active_token] = replacements[active_token][1:] + [repl_list]
    parsed, remainder = parse(repl_list + rest_tokens, safe_mode, spacing)
    # Rotate back in some cases.
    if active_token in rotate_back_replacements:
        replacements[active_token] = saved_replacements
    return parsed, remainder


# Prependers are magic. Automatically prepend to program if present.
def add_preps(preps, safe_mode):
    return [parse(prepend[var], safe_mode)[0] for var in sorted(preps)]


# Prepend print to any line starting with a function, var or
# safe infix.
def add_print(code):
    if len(code) > 0:
        if code[0] in c_to_s or code[0] in replacements or\
           code[0] in ('=', '~', 'B', 'R', 'p', ' ', '\n', ')', ';'):
            return False
        if code[0] in next_c_to_i:
            return c_to_i[code[0]] == next_c_to_i[code[0]]
        return True


# Pyth eval
def pyth_eval(a):
    if not isinstance(a, str):
        raise BadTypeCombinationError(".v", a)
    return eval(parse(lex(a), True)[0], environment)
environment['pyth_eval'] = pyth_eval


# Preprocessor for multi-line mode.
def preprocess_multiline(code_lines_with_newlines):
    # Reading a file keeps trailing newlines, remove them.
    cleaned_code_lines = [line.rstrip("\n") for line in code_lines_with_newlines]

    # Deal with comments starting with ; and metacommands.
    indent = 2
    i = 0
    end_found = False
    while i < len(cleaned_code_lines):
        code_line = cleaned_code_lines[i].lstrip()
        if code_line.startswith(";"):
            meta_line = code_line[1:].strip()
            cleaned_code_lines.pop(i)

            if meta_line.startswith("indent"):
                try:
                    indent = int(meta_line.split()[1])
                except ValueError:
                    print("Error: expected number after indent meta-command")
                    sys.exit(1)

            elif meta_line.startswith("end"):
                cleaned_code_lines = cleaned_code_lines[:i]
                end_found = True

        elif end_found:
            cleaned_code_lines.pop(i)

        else:
            i += 1

    indent_level = 0
    for linenr, line in enumerate(cleaned_code_lines):
        new_indent_level = 0

        # Deal with indentation.
        for _ in range(indent_level + 1):
            # Allow an increase of at lost one indent level per line.
            if line.startswith("\t"):
                line = line[1:]
            elif line.startswith(" " * indent):
                line = line[indent:]
            else:
                break

            new_indent_level += 1

        # Detect in-line comments.
        in_string = False
        consecutive_spaces = 0
        i = 0
        while i < len(line):
            char = line[i]
            if in_string:
                if char == "\"":
                    in_string = False
                elif char == "\\":
                    i += 1  # Nothing after a backslash can close the string.

            elif char == " ":
                consecutive_spaces += 1
            elif char == "\"":
                consecutive_spaces = 0
                in_string = True
            elif char == "\\":
                consecutive_spaces = 0
                i += 1  # Skip one-character string.
            else:
                consecutive_spaces = 0

            if consecutive_spaces == 2:
                line = line[:i - 1]
                break

            i += 1

        # If this line was non-empty after stripping inline comments, set the
        # new indent level to this line, otherwise keep the old indent level.
        if line.strip():
            indent_level = new_indent_level

        # Strip trailing whitespace, unless the line ends with
        # an uneven amount of backslashes, then
        # keep one trailing whitespace if present.
        stripped_line = line.rstrip()
        if (len(stripped_line) - len(stripped_line.rstrip("\\"))) % 2 == 1:
            stripped_line = line[:len(stripped_line) + 1]

        cleaned_code_lines[linenr] = stripped_line

    return "".join(cleaned_code_lines)


def run_code(code, inp):
    global c_to_i
    global replacements
    global preps_used

    old_stdout, old_stdin = sys.stdout, sys.stdin

    sys.stdout = io.StringIO()
    sys.stdin = io.StringIO(inp)

    error = None

    saved_env = c.deepcopy(environment)
    saved_c_to_i = c.deepcopy(c_to_i)
    saved_replacements = c.deepcopy(replacements)

    preps_used = set()

    try:
        safe_mode_setting = False
        exec(general_parse(code, safe_mode_setting), environment)
    except SystemExit:
        pass
    except Exception as e:
        error = e

    for key in list(environment):
        del environment[key]
    for key in saved_env:
        environment[key] = saved_env[key]
    c_to_i = saved_c_to_i
    replacements = saved_replacements

    result = sys.stdout.getvalue()

    sys.stdout = old_stdout
    sys.stdin = old_stdin

    return result, error

class Repl(cmd.Cmd):
    output = ""
    prompt = ">>> "
    intro = """Welcome to the Pyth REPL.
Each input line will be compiled and executed, and the results of
each one will be passed into the next one's input stream.
"""

    def __init__(self, debug_flag_on):
        self.debug_on = debug_flag_on
        cmd.Cmd.__init__(self)

    def default(self, code):
        global preps_used

        old_stdout, old_stdin = sys.stdout, sys.stdin

        sys.stdout = io.StringIO()
        sys.stdin = io.StringIO(self.output)

        preps_used = set()
        pyth_code_gen = general_parse(code, False)
        if self.debug_on:
            print(pyth_code_gen, file=sys.stderr)
            print('=' * 50, file=sys.stderr)
        try:
            exec(pyth_code_gen, environment)
        except Exception:
            traceback.print_exc()

        self.output = sys.stdout.getvalue()

        sys.stdout = old_stdout
        sys.stdin = old_stdin

        print(self.output, end="")

    def do_EOF(self, line):
        # Shut up, linter
        return True or line or self

    @property
    @memoized
    def docs(self): #Cache the docs so don't read multiple times
        with open("rev-doc.txt") as doc_file:
            docs_dict = {}
            for line in doc_file.read().split("Tokens:\n")[1].split("\n")[:-1]:
                token = (line.split(" ")[0] if not line.startswith(" ") else "space")
                lines = docs_dict.get(token, [])
                lines.append(line)
                docs_dict[token] = lines
            string_docs_dict = {}
            for token, lines in docs_dict.items():
                string_docs_dict[token] = '\n'.join(lines)
            return string_docs_dict

    def do_help(self, line):
        if line:
            print(self.docs.get(line, "%s is not a valid token" % line) if not
                  all(i in "123456789." for i in line) else self.docs["0123456789."])
        else:
            print("""This is the REPL for Pyth, an extremely concise language.
Use "help [token]" to get information about that token, or read rev-doc.txt""")

    def postloop(self):
        print()

    def complete(self):
        pass

if __name__ == '__main__':
    is_interactive = sys.stdin.isatty()
    # Check for command line flags.
    # If debug is on, print code, python code, separator.
    # If help is on, print help message.
    if is_interactive and (("-r" in sys.argv[1:]
                            or "--repl" in sys.argv[1:]) \
                           or all(flag in ("-d", "--debug") for flag in sys.argv[1:])):
        Repl("-d" in sys.argv[1:] or "--debug" in sys.argv[1:]).cmdloop()

    elif len(sys.argv) > 1 and \
            "-h" in sys.argv[1:] \
            or "--help" in sys.argv[1:]:
        print("""This is the Pyth -> Python compliler and executor.
Give file containing Pyth code as final command line argument.

Command line flags:
-c or --code:   Give code as final command arg, instead of file name.
-r or --repl:   Enter REPL mode.
-d or --debug   Show input code, generated python code.
-s or --safe    Run in safe mode. Safe mode does not permit execution of
                arbitrary Python code. Meant for online interpreter.
-l or --line    Run specified runnable line. Runnable lines are those not
                starting with ; or ), and not empty. 0-indexed.
                Specify line with 2nd to last argument. Fails on Windows.
-h or --help    Show this help message.
-m or --multi   Enable multi-line mode.
-M or --no-memoization
                Turn off automatic function memoization.
-D or --only-debug
                Turn off code execution and show only debug informations.
-x    --execute-stdin
                Instead of reading code from file or commandline, use the
                first line of STDIN. Only short-form flags can be used with
                -x, as one argument. (-xcd)
-n    --newline Trim trailing newline from file input.

See opening comment in pyth.py for more info.""")
    else:
        file_or_string = sys.argv[-1]
        if len(sys.argv) == 2 and sys.argv[1][0] == '-':
            flags = sys.argv[1:]
        else:
            flags = sys.argv[1:-1]
        verbose_flags = [flag for flag in flags if flag[:2] == '--']
        short_flags = [flag for flag in flags if flag[:2] != '--']

        def flag_on(short_form, long_form):
            return any(short_form in flag for flag in short_flags) or \
                long_form in verbose_flags
        debug_on = flag_on('d', '--debug')
        code_on = flag_on('c', '--code')
        safe_mode_on = flag_on('s', '--safe')
        line_on = flag_on('l', '--line')
        multiline_on = flag_on('m', '--multiline')
        memo_off = flag_on('M', '--no-memoization')
        only_debug = flag_on('D', '--only-debug')
        execute_stdin = flag_on('x', '--execute-stdin')
        trim_newline = flag_on('n', '--newline')
        if execute_stdin:
            assert len(sys.argv) == 2, "-x is not compatible with multiple command line arguments"
            code_lines = sys.stdin.readlines()
            code_on = False
        if safe_mode_on:
            c_to_f['v'] = ('Pliteral_eval', 1)
            del c_to_f['.w']
        if line_on:
            line_num = int(sys.argv[-2])
        if memo_off:
            c_to_s['D'] = c_to_s['D without memoization']
        if code_on and (line_on or multiline_on):
            print("Error: multiline input from command line.")
        else:
            if code_on:
                pyth_code = file_or_string
            else:
                if not execute_stdin:
                    code_lines = list(open(file_or_string, encoding='iso-8859-1', newline=''))
                if line_on:
                    runable_code_lines = [code_line[:-1]
                                          for code_line in code_lines
                                          if code_line[0] not in ';)\n']
                    pyth_code = runable_code_lines[line_num]
                elif multiline_on:
                    pyth_code = preprocess_multiline(code_lines)
                else:
                    end_marker = '; end\n'
                    if end_marker in code_lines:
                        end_line = code_lines.index(end_marker)
                        pyth_code = ''.join(code_lines[:end_line])
                    else:
                        pyth_code = ''.join(code_lines)
                    if trim_newline and len(pyth_code) > 0 and pyth_code[-1] == '\n':
                        pyth_code = pyth_code[:-1]

            py_code_line = general_parse(pyth_code, safe_mode_on)
            # Debug message
            if debug_on or only_debug:
                print('{:=^50}'.format(' ' + str(len(pyth_code)) + ' chars '),
                      file=sys.stderr)
                print(pyth_code, file=sys.stderr)
                print('=' * 50, file=sys.stderr)
                print(py_code_line, file=sys.stderr)
                print('=' * 50, file=sys.stderr)

            if safe_mode_on and not only_debug:
                # To limit memory use to 200 MB so that it doesn't crash heroku:

                try:
                    import resource
                    resource.setrlimit(resource.RLIMIT_AS, (2*10**8, 2*10**8))
                except:
                    # I think this fails on Windows? In that case I'll just discard the error.
                    pass
                # to fix most security problems, we will disable the use of
                # unnecessary parts of the python
                # language which should never be needed for golfing code.
                # (eg, import statements)

                code_to_remove_tools =\
                    "del __builtins__['__import__']\n"
                # remove import capability
                code_to_remove_tools += "del __builtins__['open']\n"
                # remove capability to read/write to files

                # while this is hardly an exaustive list,
                # and while blacklisting in general
                # should not be used for security, it does
                # solve many security problems.
                exec(code_to_remove_tools + py_code_line, environment)
                # ^ is still evil.

                # Honestly, I'd just whitelist your custom functions
                # and discard anything
                # that doesn't match the whitelist of functions.

                # Anyway, hope you don't mind me patching things up here.
                # Email any questions to

                # PS: Security shouldn't be a black mark to Pyth.
                # I think it's a really neat idea!

            elif not safe_mode_on and not only_debug:
                safe_mode_on = False
                exec(py_code_line, environment)
