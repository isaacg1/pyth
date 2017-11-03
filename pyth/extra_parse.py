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

def str_parse_next(active_token):
    point = 0
    out = []
    while point < len(active_token):
        if active_token[point] == '\\':
            if len(active_token) == point + 1:
                out.append('\\\\')
                break
            elif active_token[point + 1] in ('\\', '"'):
                out.append(active_token[point:point+2])
                point += 2
                continue
            elif active_token[point + 1] == '\n':
                point += 2
                continue
        if active_token[point] == '\n':
            out.append('\\n')
        elif active_token[point] == '\r':
            out.append('\\r')
        elif active_token[point] == '\0':
            out.append('\\000')
        else:
            out.append(active_token[point])
        point += 1
    if out.count('"') == 1:
        out.append('"')
        assert out.count('"') == 2                
    return ''.join(out)
