#!/usr/bin/python3
import pyth
import subprocess

# The idea here is to test each type as input to each function.
# num, float, str, list, tuple, set, dict

test_cases = [
    # Test \n
    ('1\n1', '1\n1\n'),
    # Test ' '
    ('1 1', '1\n'),
    ('1  1', '1\n'),
    # Test !
    ('!0', 'True\n'),
    ('!0.', 'True\n'),
    ('!"', 'True\n'),
    ('![', 'True\n'),
    ('!(', 'True\n'),
    ('!{', 'True\n'),
    ('!.d[', 'True\n'),
    ('!q1 0', 'True\n'),
    ('!>2 1', 'False\n'),
    ('!]0', 'False\n'),
    ('!.5', 'False\n'),
    ('!(1', 'False\n'),
    ('!"Hallo', 'False\n'),
    ('!{"Hallo', 'False\n'),
    ('!.d[,1 2', 'False\n'),
    # Test "
    ('"a', 'a\n'),
    ('"a"', 'a\n'),
    ('"\\', '\\\n'),
    ('"\\"', '"\n'),
    ('"\\""', '"\n'),
    ('"\\\\', '\\\n'),
    ('"\\\\\\"', '\\"\n'),
    ('"\n', '\n\n'),
    # Test #
    ('#1B1', '1\n1\n'),
    ('#1/1 0 2)2', '1\n2\n'),
    ('#/2-2Z~Z1', '1\n2\n'),
    # Test $
    ('$Z="Hello."$Z', 'Hello.\n'),
    # Test %
    ('%5 2', '1\n'),
    ('%6 3', '0\n'),
    ('%3U8', '[0, 3, 6]\n'),
    ('%2"YNeos', 'Yes\n'),
    ('%2(1 2 3 4', '(1, 3)\n'),
    ('%"i=%d"1', 'i=1\n'),
    ('%"%s=%d",\i1', 'i=1\n'),
    ('%"%0.2f".12345', '0.12\n'),
    # Test &
    ('&1 0', '0\n'),
    ('&!0!0', 'True\n'),
    ('&!1!0', 'False\n'),
    ('&0/1Z', '0\n'),
    ('&2 3', '3\n'),
    # TODO: Test '
    # Test (
    ('(', '()\n'),
    ('()', '()\n'),
    ('(1', '(1,)\n'),
    ('(1 2', '(1, 2)\n'),
    ('(1"abc"3)', "(1, 'abc', 3)\n"),
    # Test )
    ('(1)2', '(1,)\n2\n'),
    ('V3N)0', '0\n1\n2\n0\n'),
    ('FN"abc"N)0', 'a\nb\nc\n0\n'),
    ('#/1Z)1', '1\n'),
    ('c"a b")1', "['a', 'b']\n1\n"),
    # Test *
    ('*3 2', '6\n'),
    ('*3 .5', '1.5\n'),
    ('.R*.1.2 5', '0.02\n'),
    (r'*\x5', 'xxxxx\n'),
    ('*2"ab', 'abab\n'),
    ('*3]0', '[0, 0, 0]\n'),
    ('*[1 2 3)2', '[1, 2, 3, 1, 2, 3]\n'),
    ('*2,Z1', '(0, 1, 0, 1)\n'),
    ('*U3U2', '[(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]\n'),
    ('*"abc"U2', "[('a', 0), ('a', 1), ('b', 0), ('b', 1), ('c', 0), ('c', 1)]\n"),
    ('*"abc",0 1', "[('a', 0), ('a', 1), ('b', 0), ('b', 1), ('c', 0), ('c', 1)]\n"),
    ('*"ab""cd', "[('a', 'c'), ('a', 'd'), ('b', 'c'), ('b', 'd')]\n"),
    # Test :
    (':"abcde",0 3]"lol"', 'lolbclole\n'),
    (':"####$$$$"%2U8\\x', 'x#x#x$x$\n'),
    (':U10r4 7 8', '[0, 1, 2, 3, 8, 8, 8, 7, 8, 9]\n'),
]



def test(pyth_code, expected_output, input_message=''):
    output, error = pyth.run_code(pyth_code, input_message)

    if error:
        raise NameError("Error thrown by %s on input %s:\n%s" %\
            (pyth_code, input_message, error))
    if output != expected_output:
        raise NameError("Bad output by %s on input %s."
                        "\nExpected: %r.\nReceived: %r" %\
            (pyth_code, input_message, expected_output, output))

if __name__ == '__main__':
    for test_case in test_cases:
        test(*test_case)
    print("All tests succeeded.")
