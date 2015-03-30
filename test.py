#!/usr/bin/python3
import subprocess

# The idea here is to test each type as input to each function.
# num, float, str, list, tuple, set, dict

test_cases = [
    # Test \n
    ('1\n1', b'1\n1\n'),
    # Test ' '
    ('1 1', b'1\n'),
    # Test !
    ('!0', b'True\n'),
    ('!0.', b'True\n'),
    ('!"', b'True\n'),
    ('![', b'True\n'),
    ('!(', b'True\n'),
    ('!{', b'True\n'),
    ('!.d[', b'True\n'),
    # Test "
    ('"a', b'a\n'),
    ('"a"', b'a\n'),
    ('"\\', b'\\\n'),
    ('"\\"', b'"\n'),
    ('"\\""', b'"\n'),
    ('"\\\\', b'\\\n'),
    ('''"
''', b'\n\n'),
    # Test #
    ('#1B1)1', b'1\n1\n'),
    ('#1/1 0 2)2', b'1\n2\n'),
    ('#/2-2Z~Z1', b'1\n2\n'),
    # Test $
    ('$Z="Hello."$Z', b'Hello.\n'),
    ]


def test(pyth_code, expected_output, input_message=''):
    pyth_process = \
        subprocess.Popen(['/usr/bin/env',
                          'python3',
                          'pyth.py',
                          '-c',
                          pyth_code],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)

    output, errors = \
        pyth_process.communicate(input=bytearray(input_message, 'utf-8'))

    if errors:
        raise NameError("Error thrown by %s on input %s:\n%s" %\
            (pyth_code, input_message, errors))
    if output != expected_output:
        raise NameError("Bad output by %s on input %s."
                        "\nExpected: %r.\nReceived: %r" %\
            (pyth_code, input_message, expected_output, output))

if __name__ == '__main__':
    for test_case in test_cases:
        test(*test_case)
    print("All tests succeeded.")
