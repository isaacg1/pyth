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
from extra_parse import *
from macros import environment, BadTypeCombinationError, memoized
from data import *
import copy as c
import sys
import io
import cmd

sys.setrecursionlimit(100000)

lambda_stack = []
preps_used = set()
state_maintaining_depth = 0

# Parse it!


def general_parse(code):
    # Parsing
    args_list = []
    parsed = 'Not empty'
    while code != '':
        to_print = add_print(code)
        parsed, code = parse(code)
        if to_print:
            parsed = 'imp_print(' + parsed + ')'
        # Finish semicolon parsing
        if code and code[0] == ';':
            code = code[1:]
        args_list.append(parsed)
    # Build the output string.
    args_list = add_preps(preps_used) + args_list
    py_code = '\n'.join(args_list)
    return py_code


def parse(code, spacing="\n "):
    # If we've reached the end of the string, finish up.
    if code == '':
        if lambda_stack:
            return lambda_stack[0], ''
        else:
            preps_used.add('Q')
            return 'Q', ''
    # Separate active character from the rest of the code.
    active_char = code[0]
    rest_code = code[1:]
    # Deal with alternate command table
    if active_char == ".":
        assert len(rest_code) >= 1, 'expected letter after .'
        if rest_code[0] not in "0123456789":
            active_char += rest_code[0]
            rest_code = rest_code[1:]
    # Deal with numbers
    if active_char == "0":
        return active_char, rest_code
    if active_char in ".123456789":
        return num_parse(active_char + rest_code)
    # String literals
    if active_char == '"':
        return str_parse(rest_code)
    if active_char == '."':
        string, rest_code = str_parse(rest_code)
        return "%s(%s)" % (c_to_f['."'][0], string), rest_code
    # Python code literals
    if active_char == '$':
        if safe_mode:
            raise UnsafeInputError(active_char, rest_code)
        else:
            return python_parse(active_char + rest_code)
    # End paren is magic (early-end current function/statement).
    if active_char == ')':
        return '', rest_code
    if active_char == ';':
        # Inside a lambda, return the innermost lambdas leading variable.
        if lambda_stack or state_maintaining_depth:
            return 'env_lookup({!r})'.format((lambda_stack or ['Q'])[-1]), rest_code
        # Semicolon is more magic (early-end all active functions/statements).
        if rest_code == '':
            return '', ';'
        else:
            return '', ';' + rest_code
    # Designated variables
    if active_char in variables:
        if active_char in prepend:
            preps_used.add(active_char)
        return active_char, rest_code
    # Replace replaements
    if active_char in replacements:
        return replace_parse(active_char, rest_code, spacing)
    # Syntactic sugar handling.
    if rest_code and (active_char in c_to_f or active_char in c_to_i):
        sugar_char = rest_code[0]
        remainder = rest_code[1:]
        if active_char in c_to_f:
            arity = c_to_f[active_char][1]
        else:
            arity = c_to_i[active_char][1]

        # Sugar Chaining
        sugar_chars = 'FMLBRID#VW'
        sugar_active_char = active_char
        while sugar_char in sugar_chars and remainder and remainder[0] in sugar_chars:
            sugar_active_char += sugar_char
            sugar_char = remainder[0]
            remainder = remainder[1:]
        if arity > 0:
            if sugar_char == 'F':
                if arity == 1:
                    # Unary: Repeated application
                    rep_arg1, post1 = parse(remainder)
                    rep_arg2, post2 = parse(post1)
                    if sugar_active_char in c_to_f:
                        func = c_to_f[sugar_active_char][0]
                    else:
                        func = "lambda unary_F: " + c_to_i[sugar_active_char][0].format("unary_F")
                    return "repeat({}, {}, {})".format(func, rep_arg1, rep_arg2), post2
                if arity == 2:
                    # <binary function/infix>F: Fold operator
                    reduce_arg1 = lambda_vars['.U'][0][0]
                    reduce_arg2 = lambda_vars['.U'][0][-1]
                    fold_list, post_fold = next_seg(remainder)
                    full_fold, rest = parse(".U" + sugar_active_char +
                                            reduce_arg1 + reduce_arg2 + fold_list)
                    assert rest == '', "Sugar parse F fold failed"
                    return full_fold, post_fold
                if arity > 2:
                    # Just splat it - it's a common use case.
                    splat_list, post_splat = next_seg(remainder)
                    full_splat, rest = parse(
                        sugar_active_char + '.*' + splat_list)
                    assert rest == '', "Sugar parse F splat failed"
                    return full_splat, post_splat

            # <function>M: Map operator
            if sugar_char == 'M':
                m_arg = lambda_vars['m'][0][0]
                if arity == 1:
                    map_target, post_map = next_seg(remainder)
                    full_map, rest = parse('m' + sugar_active_char + m_arg + map_target)
                    assert rest == '', "Sugar parse M 1 arg failed"
                    return full_map, post_map
                else:
                    map_target, post_map = next_seg(remainder)
                    full_map, rest = parse('m%sF%s%s' % (sugar_active_char, m_arg, map_target))
                    assert rest == '', "Sugar parse M 2+ args failed"
                    return full_map, post_map

            # <binary function>L<any><seq>: Left Map operator
            # >LG[1 2 3 4 -> 'm>Gd[1 2 3 4'.
            if sugar_char == 'L':
                if arity >= 2:
                    m_arg = lambda_vars['m'][0][0]
                    lmap_lambda_args, remainder = next_n_segs(arity - 1, remainder)
                    lmap_target, post_lmap = next_seg(remainder)
                    full_lmap, rest = parse('m' + sugar_active_char + lmap_lambda_args + m_arg + lmap_target)
                    assert rest == '', "Sugar parse L failed"
                    return full_lmap, post_lmap

            # <function>V<seq><seq> Vectorize operator.
            # Equivalent to <func>MC,<seq><seq>.
            if sugar_char == 'V':
                vmap_target, post_vmap = next_n_segs(2, remainder)
                full_vmap, rest = parse(sugar_active_char + 'MC,' + vmap_target)
                assert rest == '', "Sugar parse V failed"
                return full_vmap, post_vmap

            # <function>W<condition><arg><rgs> Condition application operator.
            # Equivalent to ?<condition><function><arg><args><arg>
            if sugar_char == 'W':
                condition, rest_code1 = parse(remainder)
                arg1, rest_code2 = state_maintaining_parse(rest_code1)
                func, rest_code2b = parse(sugar_active_char + rest_code1)
                return ('(%s if %s else %s)' % (func, condition, arg1), rest_code2b)

            # <function>B<arg><args> -> ,<arg><function><arg><args>
            # <unary function>I<any> Invariant operator.
            # Equivalent to q<func><any><any>
            if sugar_char in 'BI':
                dup_dict = {
                    'B': '[{},{}]',
                    'I': '{}=={}',
                }
                dup_format = dup_dict[sugar_char]
                dup_parsed, _ = state_maintaining_parse(remainder)
                non_dup_parsed, post_dup = parse(sugar_active_char + remainder)
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
                rop_args, post_rop = next_n_segs(arity, remainder)
                full_rop, rest = parse(func_char + sugar_active_char + lambda_arg + rop_args)
                assert rest == '', 'Sugar parse %s failed' % sugar_char
                return full_rop, post_rop

    # =<function/infix>, ~<function/infix>: augmented assignment.
    if active_char in ('=', '~'):
        if augment_assignment_test(rest_code):
            return augment_assignment_parse(active_char, rest_code)

    # And for general functions
    if active_char in c_to_f:
        if active_char in lambda_f:
            return lambda_function_parse(active_char, rest_code)
        else:
            return function_parse(active_char, rest_code)
    # General format functions/operators
    if active_char in c_to_i:
        return infix_parse(active_char, rest_code)
    # Statements:
    if active_char in c_to_s:
        return statement_parse(active_char, rest_code, spacing)
    # If we get here, the character has not been implemented.
    # There is no non-ASCII support.
    raise PythParseError(active_char, rest_code)


def next_seg(code):
    parsed, rest = state_maintaining_parse(code)
    pyth_seg = code[:len(code) - len(rest)]
    return pyth_seg, rest


def next_n_segs(n, code):
    if not isinstance(n, int):
        assert n == float('inf'), "arities must be either ints or infinity"
        raise RuntimeError # Can't use unbounded arity function in this context.
    remainder = code
    segs = ''
    for _ in range(n):
        seg, remainder = next_seg(remainder)
        segs += seg
    return segs, remainder


def state_maintaining_parse(code):
    global c_to_i
    global state_maintaining_depth
    saved_c_to_i = c.deepcopy(c_to_i)
    state_maintaining_depth += 1
    py_code, rest_code = parse(code)
    state_maintaining_depth -= 1
    c_to_i = saved_c_to_i
    return py_code, rest_code


def augment_assignment_test(rest_code):
    if rest_code[0] == ".":
        func_char = rest_code[:2]
        following_code = rest_code[2:]
    else:
        func_char = rest_code[0]
        following_code = rest_code[1:]
    return func_char not in variables and func_char not in next_c_to_i and func_char != ','


def augment_assignment_parse(active_char, rest_code):
    if rest_code[0] == ".":
        func_char = rest_code[:2]
        following_code = rest_code[2:]
    else:
        func_char = rest_code[0]
        following_code = rest_code[1:]
    following_vars = [
        char for char in following_code if char in variables or char in next_c_to_i]
    assert following_vars, 'Assignment needs a variable'
    var_char = following_vars[0]
    return parse(active_char +
                 var_char +
                 rest_code)


def lambda_function_parse(active_char, rest_code):
    # Function will definitely be in next_c_to_f
    global c_to_f
    global next_c_to_f
    func_name, arity = c_to_f[active_char]
    var = lambda_vars[active_char][0]
    # Swap what variables are used in lambda functions.
    saved_lambda_vars = lambda_vars[active_char]
    lambda_vars[active_char] = lambda_vars[active_char][1:] + [var]
    lambda_stack.append(var[0])
    # Take one argument, the lambda.
    parsed, rest_code = parse(rest_code)
    args_list = [parsed]
    # Rotate back.
    lambda_vars[active_char] = saved_lambda_vars
    lambda_stack.pop()
    while (len(args_list) != arity and parsed != ''
            and not (rest_code == ''
                     and active_char in optional_final_arg
                     and len(args_list) == arity - 1)):
        parsed, rest_code = parse(rest_code)
        args_list.append(parsed)
    if len(args_list) > 0 and args_list[-1] == '':
        args_list = args_list[:-1]
    py_code = '%s(lambda %s:%s)' % (func_name, var, ','.join(args_list))
    return py_code, rest_code


def function_parse(active_char, rest_code):
    func_name, arity = c_to_f[active_char]
    # Recurse until terminated by end paren or EOF
    # or received enough arguments
    args_list = []
    parsed = 'Not empty'
    while (len(args_list) != arity and parsed != ''
            and not (arity == float('inf') and rest_code == '')
            and not (rest_code == ''
                     and active_char in optional_final_arg
                     and len(args_list) == arity - 1)):
        parsed, rest_code = parse(rest_code)
        args_list.append(parsed)
    # Build the output string.
    if len(args_list) > 0 and args_list[-1] == '':
        args_list = args_list[:-1]
    py_code = '%s(%s)' % (func_name, ','.join(args_list))
    return py_code, rest_code


def infix_parse(active_char, rest_code):
    global c_to_i
    infixes, arity = c_to_i[active_char]
    # Advance infixes.
    if active_char in next_c_to_i:
        c_to_i[active_char] = next_c_to_i[active_char]
    args_list = []
    parsed = 'Not empty'
    # Lambda infix(es)
    if active_char == '.W':
        lambda_stack.extend(['Z', 'H'])
    while len(args_list) != arity and parsed != '':
        if (rest_code == ''
                and active_char in optional_final_arg
                and len(args_list) == arity - 1):
            args_list.append('')
            break
        parsed, rest_code = parse(rest_code)
        args_list.append(parsed)
        if active_char == '.W' and len(args_list) <= 2:
            lambda_stack.pop()
    # Statements that cannot have anything after them
    if active_char in end_statement:
        rest_code = ")" + rest_code
    py_code = infixes.format(*args_list)
    return py_code, rest_code


def statement_parse(active_char, rest_code, spacing):
    # Handle the initial portion (head)
    # addl_spaces denotes the amount of extra spacing needed.
    if len(c_to_s[active_char]) == 2:
        infixes, arity = c_to_s[active_char]
        addl_spaces = ''
    else:
        infixes, arity, num_spaces = c_to_s[active_char]
        addl_spaces = ' ' * num_spaces
    # Handle newlines in infix segments
    infixes = infixes.replace("\n", spacing[:-1])
    args_list = []
    parsed = 'Not empty'
    while len(args_list) != arity and parsed != '':
        parsed, rest_code = parse(rest_code)
        args_list.append(parsed)
    # Handle the body - ends object as well.
    body_lines = []
    parsed = 'Not empty'
    while parsed != '' and rest_code != '':
        to_print = add_print(rest_code)
        parsed, rest_code = parse(rest_code, spacing + addl_spaces + ' ')
        if to_print:
            parsed = 'imp_print(%s)' % parsed
        body_lines.append(parsed)
    # Trim the '' away and combine.
    if body_lines and body_lines[-1] == '':
        body_lines = body_lines[:-1]
    if body_lines == []:
        body_lines = ['pass']
    # Combine pieces - intro, statement, conclusion.
    total_spacing = spacing + addl_spaces
    body = total_spacing + total_spacing.join(body_lines)
    args_list.append(body)
    return infixes.format(*args_list), rest_code


def replace_parse(active_char, rest_code, spacing):
    global replacements
    # Special case for \\
    if active_char == "\\" and rest_code[0] in "\"\\":
        return parse('"\\' + rest_code[0] + '"' + rest_code[1:], spacing)
    # Rotate replacements.
    repl_str = replacements[active_char][0]
    saved_replacements = replacements[active_char]
    replacements[active_char] = replacements[active_char][1:] + [repl_str]
    # Parse
    if isinstance(repl_str, tuple):
        repl_str, num_args = repl_str
        format_chars = tuple(rest_code[:num_args])
        new_code = repl_str.format(*format_chars) + rest_code[num_args:]
        parsed, remainder = parse(new_code, spacing)
    else:
        parsed, remainder = parse(repl_str + rest_code, spacing)
    # Rotate back in some cases.
    if active_char in rotate_back_replacements:
        replacements[active_char] = saved_replacements
    return parsed, remainder


# Prependers are magic. Automatically prepend to program if present.
def add_preps(preps):
    return [parse(prepend[var])[0] for var in sorted(preps)]


# Prepend print to any line starting with a function, var or
# safe infix.
def add_print(code):
    if len(code) > 0:
        # Handle alternate table commands before confusion with numerals.
        if code[0] == ".":
            assert len(code) >= 2, 'expected letter after .'
            if code[:2] in c_to_f and not code[:2] == '.q':
                return True
            if code[:2] in variables:
                return True
            if code[:2] in ('.x', '.W', '.(', '.)',):
                return True
            if code[1] not in '0123456789':
                return False

        if (code[0] not in 'p \n'
                and code[0] in c_to_f) or \
            code[0] in variables or \
            code[0] in "@&|]}?,\\\".0123456789," or \
            ((code[0] in 'JK' or code[0] in prepend) and
                c_to_i[code[0]] == next_c_to_i[code[0]]):
            return True
    return False


# Pyth eval
def pyth_eval(a):
    if not isinstance(a, str):
        raise BadTypeCombinationError(".v", a)
    return eval(parse(a)[0], environment)
environment['pyth_eval'] = pyth_eval


# Preprocessor for multi-line mode.
def preprocess_multiline(code_lines):
    # Reading a file keeps trailing newlines, remove them.
    code_lines = [line.rstrip("\n") for line in code_lines]

    # Deal with comments starting with ; and metacommands.
    indent = 2
    i = 0
    end_found = False
    while i < len(code_lines):
        code_line = code_lines[i].lstrip()
        if code_line.startswith(";"):
            meta_line = code_line[1:].strip()
            code_lines.pop(i)

            if meta_line.startswith("indent"):
                try:
                    indent = int(meta_line.split()[1])
                except:
                    print("Error: expected number after indent meta-command")
                    sys.exit(1)

            elif meta_line.startswith("end"):
                code_lines = code_lines[:i]
                end_found = True

        elif end_found:
            code_lines.pop(i)

        else:
            i += 1

    indent_level = 0
    for linenr, line in enumerate(code_lines):
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
            c = line[i]
            if in_string:
                if c == "\"":
                    in_string = False
                elif c == "\\":
                    i += 1  # Nothing after a backslash can close the string.

            elif c == " ":
                consecutive_spaces += 1
            elif c == "\"":
                consecutive_spaces = 0
                in_string = True
            elif c == "\\":
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

        code_lines[linenr] = stripped_line

    return "".join(code_lines)


def run_code(code, inp):
    global safe_mode
    global environment
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
        safe_mode = False
        exec(general_parse(code), environment)
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

    def default(self, code):
        self.output, error = run_code(code, self.output)
        print(self.output, end="")

    def do_EOF(self, line):
        return True

    @property
    @memoized
    def docs(self): #Cache the docs so don't read multiple times
        with open("rev-doc.txt") as doc_file:
            return {i.split(" ")[0] if not i.startswith(" ") else "space":i for
                i in doc_file.read().split("Tokens:\n")[1].split("\n")[:-1]}

    def do_help(self, line):
        if line:
            print(self.docs.get(line, "%s is not a valid token" % line) if not
                all(i in "123456789." for i in line) else self.docs["0123456789."])
        else:
            print("""This is the REPL for Pyth, an extremely concise language.
Use "help [token]" to get information about that token, or read rev-doc.txt""")

    def postloop(self):
        print()

if __name__ == '__main__':
    global safe_mode, c_to_f

    # Check for command line flags.
    # If debug is on, print code, python code, separator.
    # If help is on, print help message.
    if len(sys.argv) > 1 and \
            "-r" in sys.argv[1:] \
            or "--repl" in sys.argv[1:] \
            or len(sys.argv) == 1:

        #setting to None not working, so temp fix setting to key doesn't exist
        #wating for answer on http://stackoverflow.com/questions/37981271
        Repl("skjlksdjfjdsf").cmdloop()

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

See opening comment in pyth.py for more info.""")
    else:
        file_or_string = sys.argv[-1]
        flags = sys.argv[1:-1]
        verbose_flags = [flag for flag in flags if flag[:2] == '--']
        short_flags = [flag for flag in flags if flag[:2] != '--']

        def flag_on(short_form, long_form):
            return any(short_form in flag for flag in short_flags) or \
                long_form in verbose_flags
        debug_on = flag_on('d', '--debug')
        code_on = flag_on('c', '--code')
        safe_mode = flag_on('s', '--safe')
        line_on = flag_on('l', '--line')
        multiline_on = flag_on('m', '--multiline')
        memo_off = flag_on('M', '--no-memoization')
        if safe_mode:
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
                code_lines = list(open(file_or_string, encoding='iso-8859-1'))
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
                    if len(pyth_code) > 0 and pyth_code[-1] == '\n':
                        pyth_code = pyth_code[:-1]

            # Debug message
            if debug_on:
                print('{:=^50}'.format(' ' + str(len(pyth_code)) + ' chars '),
                      file=sys.stderr)
                print(pyth_code, file=sys.stderr)
                print('=' * 50, file=sys.stderr)

            py_code_line = general_parse(pyth_code)

            if debug_on:
                print(py_code_line, file=sys.stderr)
                print('=' * 50, file=sys.stderr)

            if safe_mode:
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

            else:
                safe_mode = False
                exec(py_code_line, environment)
