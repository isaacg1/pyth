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
    # Test !
    ('!0', 'True\n'),
    ('!0.', 'True\n'),
    ('!"', 'True\n'),
    ('![', 'True\n'),
    ('!(', 'True\n'),
    ('!{', 'True\n'),
    ('!.d[', 'True\n'),
    # Test "
    ('"a', 'a\n'),
    ('"a"', 'a\n'),
    ('"\\', '\\\n'),
    ('"\\"', '"\n'),
    ('"\\""', '"\n'),
    ('"\\\\', '\\\n'),
    ('"\n', '\n\n'),
    # Test #
    ('#1B1)1', '1\n1\n'),
    ('#1/1 0 2)2', '1\n2\n'),
    ('#/2-2Z~Z1', '1\n2\n'),
    # Test $
    ('$Z="Hello."$Z', 'Hello.\n'),
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
