import extra_parse
import data
import sys

# Call with Pyth program on STDIN.


global J_used
global K_used
J_used = False
K_used = False
nums = '0123456789'


def make_tree(code):
    if code == '':
        return [], ''
    char, code = code[0], code[1:]
    if char == '.' and code[0] not in nums:
        char += code[0]
        code = code[1:]
    if char in '.' + nums:
        while code and code[0] in nums:
            char += code[0]
            code = code[1:]
        return [char], code
    if char == '"':
        _, new_code = extra_parse.str_parse(char, code)
        char += code[:len(code) - len(new_code)]
        code = new_code
        return [char], code
    if char == '$':
        _, new_code = extra_parse.python_parse(char, code)
        char += code[:len(code) - len(new_code)]
        code = new_code
        return [char], code
    if char == '\\':
        if code:
            char += '\\' + code[0]
            code = code[1:]
        return [char], code
    if char == ')':
        return [], code
    if char == ';':
        return [], ';' + code
    if char in data.variables:
        return [char], code
    global J_used
    if char == 'J':
        if J_used:
            return [char], code
        else:
            J_used = True
    global K_used
    if char == 'K':
        if K_used:
            return [char], code
        else:
            K_used = True
    if char in data.c_to_s or char in 'V':
        if char in 'V':
            init_arity = 1
        else:
            init_arity = data.c_to_s[char][1]
        args = [char]
        while len(args) < init_arity + 1 and code:
            child, new_code = make_tree(code)
            code = new_code
            args.append(child)
        while args[-1] and args[-1][0] not in data.end_statement and code:
            child, new_code = make_tree(code)
            code = new_code
            args.append(child)
        if not args[-1]:
            args = args[:-1]
        return args, code
    if char in data.c_to_f:
        arity = data.c_to_f[char][1]
    if char in data.c_to_i:
        arity = data.c_to_i[char][1]
    if char in data.replacements:
        # This may change!
        arity = 1
    if char in data.c_to_i or char in data.c_to_f or char in data.replacements:
        if arity == 0:
            return [char], code
        if not code:
            return [char, []], code
        elif code[0] in 'FMI':
            arity = 1
            char += code[0]
            code = code[1:]
        elif code[0] in 'LRV':
            arity = 2
            char += code[0]
            code = code[1:]
        elif code[0] in 'W':
            arity += 1
            char += code[0]
            code = code[1:]
        elif code[0] in 'B':
            char += code[0]
            code = code[1:]
        while code[0] in 'M':
            arity = 1
            char += code[0]
            code = code[1:]
        args = [char]
        while (arity < 0 or len(args) < arity + 1) and code:
            child, new_code = make_tree(code)
            code = new_code
            args.append(child)
        return args, code
    raise NameError("%s unimplemented" % char)


def assemble_trees(code):
    trees = []
    while code:
        tree, code = make_tree(code)
        if code and code[0] == ';':
            code = code[1:]
        trees.append(tree)
    return trees


def disp_tree(trees):
    graph = Digraph()
    count = 0

    def add(tree, count):
        if not tree:
            return count
        root = count
        graph.node(str(root), label=tree[0])
        for subtree in tree[1:]:
            if subtree:
                count += 1
                graph.edge(str(root), str(count))
                count = add(subtree, count)
        return count
    for tree in trees:
        count = add(tree, count) + 1
    graph.render('tree-rep.gv', view=True)


def text_tree(trees):
    def single_tree(tree):
        head, *children = tree
        if not children:
            return head
        start = head + ' '
        rest = (single_tree(children[0]) if len(children) == 1
                else ''.join(
                    '\n' + single_tree(child)
                    for child in children))
        return start + rest.replace('\n', '\n' + ' ' * len(start))
    return '\n'.join(single_tree(tree) for tree in trees)

code = input()
trees = assemble_trees(code)
if len(sys.argv) > 1:
    from graphviz import Digraph
    disp_tree(trees)
else:
    print(text_tree(trees))
