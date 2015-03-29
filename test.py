#!/usr/bin/python3
import subprocess


test_cases = [
    # Test \n
    ('1\n1', b'1\n1\n'),
    # Test ' '
    ('1 1', b'1\n'),
    # Test !
    ('!Y', b'True\n'),
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
