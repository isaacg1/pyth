def lex(code):
    remainder = code
    tokens = []
    while remainder:
        split_point = find_split_point(remainder)
        token, remainder = remainder[:split_point], remainder[split_point:]
        tokens.append(token)
    return tokens

def find_split_point(code):
    if len(code) == 1:
        return 1
    if code[0] == ".":
        if code[1] == '"':
            return string_split(code[1:]) + 1
        if code[1] not in "0123456789":
            return 2
    if code[0] == '\\':
        return 2
    if code[0] in ".123456789":
        return num_split(code)
    if code[0] == '"':
        return string_split(code)
    if code[0] == '$':
        return python_lit_split(code)
    return 1

def string_split(code):
    assert code[0] == '"'
    point = 1
    while point < len(code):
        if code[point] == '\\':
            if len(code) == point + 1:
                point += 1
                break 
            elif code[point+1] in ('"', '\\'):
                point += 2
                continue
        if code[point] == '"':
            point += 1
            break
        else:
            point += 1
    return point

def num_split(code):
    point = 0
    seen_a_dot = False
    while point < len(code) \
          and code[point] in ".0123456789" \
          and (not (seen_a_dot and code[point] == '.')):
        seen_a_dot = seen_a_dot or code[point] == '.'
        point += 1
    if point < len(code) and code[point-1] == '.':
        point -= 1
    return point

def python_lit_split(code):
    assert code[0] == '$'
    if '$' not in code[1:]:
        return len(code)
    else:
        return code[1:].index('$') + 2
