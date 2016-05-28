# To be included in pyth.py


class PythParseError(Exception):

    def __init__(self, active_char, rest_code):
        self.active_char = active_char
        self.rest_code = rest_code

    def __str__(self):
        return "%s is not implemented, %d from the end." % \
            (self.active_char, len(self.rest_code) + 1)


class UnsafeInputError(Exception):

    def __init__(self, active_char, rest_code):
        self.active_char = active_char
        self.rest_code = rest_code

    def __str__(self):
        return "%s is unsafe, %d from the end." % \
            (self.active_char, len(self.rest_code) + 1)


def num_parse(code):
    output = ''
    rest_code = code
    while len(rest_code) > 0 \
            and rest_code[0] in ".0123456789" \
            and (output + rest_code[0]).count(".") <= 1:
        output += rest_code[0]
        rest_code = rest_code[1:]
    if output[-1] == "." and len(rest_code) > 0 and rest_code[0] not in ' \n':
        output = output[:-1]
        rest_code = "." + rest_code
    return output, rest_code


def str_parse(rest_code):
    """Input: Everything after the leading double quote.
    Output: Resultant string, remaining code."""
    output = '"'
    found_end = False
    while len(rest_code) > 0 and not found_end:
        if rest_code[0] == '\\' and len(rest_code) == 1:
            output += rest_code + '\\'
            rest_code = ''
            break
        if rest_code[0] == '\\' and rest_code[1] in ('"', '\\'):
            output += rest_code[:2]
            rest_code = rest_code[2:]
        elif rest_code[0] == '\\' and rest_code[1] == '\n':
            rest_code = rest_code[2:]
        elif rest_code[0] == '\n':
            output += '\\n'
            rest_code = rest_code[1:]
        elif rest_code[0] == '\0':
            output += '\\000'
            rest_code = rest_code[1:]
        else:
            output += rest_code[0]
            rest_code = rest_code[1:]
            if output[-1] == '"':
                found_end = True
    if not found_end:
        output += '"'
    return output, rest_code


def python_parse(code):
    assert code[0] == '$'
    output = ''
    rest_code = code[1:]
    while (len(rest_code) > 0
           and rest_code[0] != '$'):
        output += rest_code[0]
        rest_code = rest_code[1:]
    return output, rest_code[1:]
