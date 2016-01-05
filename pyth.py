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
from macros import environment, BadTypeCombinationError
from data import *
import copy as c
import sys
import io
from ast import literal_eval

environment['literal_eval'] = literal_eval

sys.setrecursionlimit(100000)

lambda_stack = []

# Parse it!
def general_parse(code):
    code = prepend_parse(code)
    # Parsing
    args_list = []
    parsed = 'Not empty'
    while parsed != '':
        to_print = add_print(code)
        parsed, code = parse(code)
        if to_print:
            parsed = 'imp_print(' + parsed + ')'
        # Finish semicolon parsing
        if code and code[0] == ';':
            code = code[1:]
        args_list.append(parsed)
    # Build the output string.
    py_code = '\n'.join(args_list[:-1])
    return py_code


def parse(code, spacing="\n "):
    # If we've reached the end of the string, finish up.
    if code == '':
        return '', ''
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
        return num_parse(active_char, rest_code)
    # String literals
    if active_char == '"':
        return str_parse(active_char, rest_code)
    if active_char == '."':
        string, rest_code = str_parse('"', rest_code)
        return "%s(%s)" % (c_to_f['."'][0], string), rest_code
    # Python code literals
    if active_char == '$':
        if safe_mode:
            raise UnsafeInputError(active_char, rest_code)
        else:
            return python_parse(active_char, rest_code)
    # End paren is magic (early-end current function/statement).
    if active_char == ')':
        return '', rest_code
    if active_char == ';':
        # Inside a lambda, return the innermost lambdas leading variable.
        if lambda_stack:
            return 'env_lookup({!r})'.format(lambda_stack[-1]), rest_code
        # Semicolon is more magic (early-end all active functions/statements).
        if rest_code == '':
            return '', ''
        else:
            return '', ';' + rest_code
    # Designated variables
    if active_char in variables:
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

        if arity > 0:
            # <binary function/infix>F: Fold operator
            if sugar_char == 'F':
                if arity == 2:
                    reduce_arg1 = lambda_vars['.U'][0][0]
                    reduce_arg2 = lambda_vars['.U'][0][-1]
                    return parse(".U" +
                                 active_char +
                                 reduce_arg1 +
                                 reduce_arg2 +
                                 remainder)
                else:
                    # Just splat it - it's a common use case.
                    return parse(active_char + ".*" + remainder)

            # <function>M: Map operator
            if sugar_char == 'M':
                m_arg = lambda_vars['m'][0][0]
                if remainder and remainder[0] in 'LMR':
                    while remainder and remainder[0] in 'LMR':
                        if remainder[0] == 'M':
                            active_char += remainder[0]
                            remainder = remainder[1:]
                        if remainder and remainder[0] in 'LR':
                            active_char += remainder[0]
                            remainder = remainder[1:]
                            seg, remainder = next_seg(remainder)
                            active_char += seg
                    return parse('m' + active_char + m_arg + remainder)
                if arity == 1:
                    return parse('m' + active_char + m_arg + remainder)
                else:
                    return parse('m%sF%s%s' % (active_char, m_arg, remainder))
            # <binary function>L<any><seq>: Left Map operator
            # >LG[1 2 3 4 -> 'm>Gd[1 2 3 4'.
            if sugar_char == 'L':
                if arity >= 2:
                    pyth_seg = ''
                    for _ in range(arity - 1):
                        seg, remainder = next_seg(remainder)
                        pyth_seg += seg
                    m_arg = lambda_vars['m'][0][0]
                    return parse('m' + active_char + pyth_seg + m_arg + remainder)

            # <function>V<seq><seq> Vectorize operator.
            # Equivalent to <func>MC,<seq><seq>.
            if sugar_char == 'V':
                return parse("%sMC,%s" % (active_char, remainder))

            # <function>W<condition><arg><rgs> Condition application operator.
            # Equivalent to ?<condition><function><arg><args><arg>
            if sugar_char == 'W':
                condition, rest_code1 = parse(remainder)
                arg1, rest_code2 = state_maintaining_parse(rest_code1)
                func, rest_code2b = parse(active_char + rest_code1)
                return ('(%s if %s else %s)' % (func, condition, arg1), rest_code2b)

            # <function>B<arg><args> -> ,<arg><function><arg><args>
            # <unary function>I<any> Invariant operator.
            # Equivalent to q<func><any><any>
            if sugar_char in 'BI':
                func_dict = {
                    'B': ',',
                    'I': 'q',
                }
                func_char = func_dict[sugar_char]
                parsed, rest = state_maintaining_parse(remainder)
                pyth_seg = remainder[:len(remainder) - len(rest)]
                return parse(func_char + pyth_seg + active_char + remainder)

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
                return parse(func_char + active_char + lambda_arg + remainder)

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


def state_maintaining_parse(code):
    global c_to_i
    saved_c_to_i = c.deepcopy(c_to_i)
    lambda_stack.append("This is a placeholder")
    py_code, rest_code = parse(code)
    c_to_i = saved_c_to_i
    lambda_stack.pop()
    return py_code, rest_code


def augment_assignment_test(rest_code):
    if rest_code[0] == ".":
        func_char = rest_code[:2]
        following_code = rest_code[2:]
    else:
        func_char = rest_code[0]
        following_code = rest_code[1:]
    if (func_char in c_to_f and c_to_f[func_char][1] > 0) or\
       (func_char in c_to_i and c_to_i[func_char][1] > 0
            and not func_char == ','):
        var_char = following_code[0]
        if (var_char in variables or var_char in next_c_to_i):
            return True
    return False


def augment_assignment_parse(active_char, rest_code):
    if rest_code[0] == ".":
        func_char = rest_code[:2]
        following_code = rest_code[2:]
    else:
        func_char = rest_code[0]
        following_code = rest_code[1:]
    var_char = following_code[0]
    return parse(active_char +
                 var_char +
                 func_char +
                 var_char +
                 following_code[1:])


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
    while len(args_list) != arity and parsed != '':
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
    while len(args_list) != arity and parsed != '':
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
    while parsed != '':
        to_print = add_print(rest_code)
        parsed, rest_code = parse(rest_code, spacing + addl_spaces + ' ')
        if to_print:
            parsed = 'imp_print(%s)' % parsed
        body_lines.append(parsed)
    # Trim the '' away and combine.
    if body_lines[-1] == '':
        body_lines = body_lines[:-1]
    if body_lines == []:
        body_lines = ['pass']
    # Combine pieces - intro, statement, conclusion.
    total_spacing = spacing + addl_spaces
    body = total_spacing + total_spacing.join(body_lines) + total_spacing
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
def prepend_parse(code):
    def not_escaped(code_part):
        code_part = list(code_part)
        count = 0
        if code_part and code_part[-1] == '.' and quot_marks % 2 == 0:
            count = 1
        while code_part and code_part.pop() == '\\':
            count += 1
        return count % 2 == 0

    out_code = code

    for prep_char in sorted(prepend):
        quot_marks = 0
        for index, char in enumerate(code):
            if char == '"' and (not_escaped(code[:index]) or
                                (index > 0 and code[index - 1] == '.')):
                quot_marks += 1
            elif char == prep_char and quot_marks % 2 == 0 and \
                    not_escaped(code[:index]):
                out_code = prepend[prep_char] + out_code
                break

    return out_code


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

    old_stdout, old_stdin = sys.stdout, sys.stdin

    sys.stdout = io.StringIO()
    sys.stdin = io.StringIO(inp)

    error = None

    saved_env = c.deepcopy(environment)
    saved_c_to_i = c.deepcopy(c_to_i)
    saved_replacements = c.deepcopy(replacements)

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


if __name__ == '__main__':
    global safe_mode, c_to_f

    # Check for command line flags.
    # If debug is on, print code, python code, separator.
    # If help is on, print help message.
    if len(sys.argv) > 1 and \
            "-h" in sys.argv[1:] \
            or "--help" in sys.argv[1:] \
            or len(sys.argv) == 1:
        print("""This is the Pyth -> Python compliler and executor.
Give file containing Pyth code as final command line argument.

Command line flags:
-c or --code:   Give code as final command arg, instead of file name.
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
            c_to_f['v'] = ('literal_eval', 1)
            del c_to_f['.w']
        if line_on:
            line_num = int(sys.argv[-2])
        if memo_off:
            c_to_s['D'] = (('def ', ':'), 1)
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
