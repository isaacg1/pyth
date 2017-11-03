import pyth

def byte_to_k_bits(b, k):
    assert 0 <= b < 2 ** k
    return bin(b)[2:].zfill(k)
    
def bytes_to_packed(bs):
    return ''.join(byte_to_k_bits(b, 7) for b in bs)

def bin_string_to_padded_bytes(b_str):
    end = len(b_str) % 8
    if end:
        pb_str = b_str + '0' * (8 - end)
    else:
        pb_str = b_str
    b_list = []
    for i in range(len(pb_str)//8):
        sub = pb_str[i*8: (i+1)*8]
        b = int(sub, 2)
        b_list.append(b)
    return bytes(b_list)

def bytes_to_bin_string(bs):
    return ''.join(byte_to_k_bits(b, 8) for b in bs)

def bin_string_to_ascii_bytes(b_str):
    b_list = []
    for i in range(len(b_str)//7):
        sub = b_str[i*7: (i+1)*7]
        b = int(sub, 2)
        b_list.append(b)
    return bytes(b_list)

def packed_bytes_to_str(packed_bytes):
    return bin_string_to_ascii_bytes(bytes_to_bin_string(packed_bytes))

def str_to_packed_bytes(str_):
    return bin_string_to_padded_bytes(bytes_to_packed(str_))

import argparse

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("file", help='unpack, run as Pyth program', nargs='?')
group.add_argument('-p', '--pack', help='pack ASCII file SRC into file DST', nargs=2
                   , metavar=('SRC', 'DST'))
group.add_argument('-u', '--unpack', help='unpack packed file SRC into file DST', nargs=2
                   , metavar=('SRC', 'DST'))
parser.add_argument('input', help='Input for Pyth program', nargs='?', default='')
parser.add_argument('-d', '--debug', help='Show Pyth program that was run'
                    , action='store_true')
args = parser.parse_args()

if args.file:
    with open(args.file, 'rb') as f:
        data = f.read()
    pyth_code_bytes = packed_bytes_to_str(data)
    pyth_code = pyth_code_bytes.decode('ascii')
    if args.debug:
        print(pyth_code)
    result, error = pyth.run_code(pyth_code, args.input)
    if error:
        print(error)
    else:
        print(result, end='')
elif args.pack:
    src = args.pack[0]
    dst = args.pack[1]
    with open(src, 'rb') as f:
        data = f.read()
    packed_bytes = str_to_packed_bytes(data)
    str_ = packed_bytes_to_str(packed_bytes)
    assert data == str_, "Inverse works"

    with open(dst, 'wb') as f:
        writen = f.write(packed_bytes)
elif args.unpack:
    src = args.unpack[0]
    dst = args.unpack[1]
    with open(src, 'rb') as f:
        data = f.read()
    str_ = packed_bytes_to_str(data)
    packed_bytes = str_to_packed_bytes(str_)
    assert data == packed_bytes, "Inverse works"
    with open(dst, 'wb') as f:
        writen = f.write(str_)
else:
    assert False, "Argument parsing failed"
    
"""
with open(args.file, 'rb') as f:
    data = f.read()

print(data)
packed_bytes = str_to_packed_bytes(data)
print(packed_bytes)
str_ = packed_bytes_to_str(packed_bytes)
print(str_)

with open('out', 'wb') as f:
    writen = f.write(packed_bytes)
"""
