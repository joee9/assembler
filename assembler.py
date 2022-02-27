#%%
import pandas as pd

codes = pd.read_csv("./opcodes.vals", skipinitialspace=True)

file = "stringtest.txt"

# different kinds of encodings

# ========== ENCODINGS

def make_binary(num):
    sum = 0
    for i in range(32):
        val = num % 10
        sum += 2**i * val
        num = num // 10
    
    return sum

def make_hex(num):
    sum = 0
    for i in range(12):
        val = num % 10
        sum += 16**i * val
        num = num // 10
    
    return sum

def to_decimal(num):
    base = 10
    if "0x" in num:
        base = 16
    elif "0b" in num:
        base = 2
    
    return int(num, base)

def hex_print(num):
    """
    pretty hex printing; puts spaces between the bytes
    """

    s1 = (num >> 24) & 0xFF
    s2 = (num >> 16) & 0xFF
    s3 = (num >> 8)  & 0xFF
    s4 = (num >> 0)  & 0xFF

    s = f"{s1:02x} {s2:02x} {s3:02x} {s4:02x}"

    return s

def regsiter_encoding(s, t, d, a, f):
    """
    values encoding as: oooo ooss ssst tttt dddd daaa aaff ffff
    opcode o is always assumed to be 0b000000
    s is the first register, $s
    t is the first register, $t
    d is the first register, $d
    a is the "shamt"
    f is the "function code"
    """

    o = 0b0 << 26
    s = s << 21
    t = t << 16
    d = d << 11
    a = a << 6
    
    num = o | s | t | d | a | f
    
    return hex_print(num)


def immediate_encoding(o, s, t, i):
    """
    values encoded as: oooo ooss ssst tttt iiii iiii iiii iiii
    o is the opcode
    s is the first register, $s
    t is the first register, $t
    i is the immediate value
    """

    o = o << 26
    s = s << 21
    t = t << 16

    num = o | s | t | i

    return hex_print(num)

def jump_encoding(o, i):
    """
    values encoded as: oooo ooii iiii iiii iiii iiii iiii iiii
    o is the opcode
    i is the immediate value
    """

    # compute the shifted jump value
    i = i >> 2
    i = i & 0x00FFFFFF

    o = o << 26
    
    num = o | i

    return hex_print(num)


# ========== SYNTAXES

ops = codes.iloc[:,0]

input = open(f"./input/{file}", "r")
output = open(f"./output/encoded-{file}", "w")
output.write("v3.0 hex words addressed\n")

string = input.readline()
ct = 0

while (string != ""):
        
    str = string.split(" // ")[0] # split off comments
    ins = str.split(", ")
    op = ins[0]

    if "#" in op:
        op = op.split("# ")[1]
        ct = to_decimal(op)
        string = input.readline()
        continue
        

    # print(s, ins, op)

    if op == "li":
        ins = "addiu, " + ins[1] + ", " + "$0" + ", " + ins[2]
        ins = ins.split(", ")
        op = ins[0]


    idx = ops[ops == op].index[0] # get index of row containing desired operation

    key = codes.iloc[idx]
    op, opcode, syntax, des = key

    opcode = make_binary(opcode)

    # register encodings
    if syntax == "ArithLog":
        f = opcode
        d = int(ins[1][1])
        s = int(ins[2][1])
        t = int(ins[3][1])
        a = 0

        encoding = regsiter_encoding(s,t,d,a,f)

    elif syntax == "Shift":
        f = opcode
        d = int(ins[1][1])
        s = 0
        t = int(ins[2][1])
        a = to_decimal(ins[3])

        encoding = regsiter_encoding(s,t,d,a,f)

    # elif syntax == "DivMult":V
    #     f = opcode
    #     s = int(ins[1][1])
    #     t = int(ins[2][1])
    #     a = int(ins[3])

    #     encoding = regsiter_encoding(s,t,d,a,f)

    elif syntax == "ArithLogI":
        o = opcode
        t = int(ins[1][1])
        s = int(ins[2][1])
        i = to_decimal(ins[3])

        encoding = immediate_encoding(o,s,t,i)

    elif syntax == "Branch":
        o = opcode
        s = int(ins[1][1])
        t = int(ins[2][1])
        label = to_decimal(ins[3])
        # i = 4 + label << 2
        i = label

        encoding = immediate_encoding(o,s,t,i)

    elif syntax == "BranchZ":
        o = opcode
        s = int(ins[1][1])
        # t = int(ins[2][1])
        t = 0
        label = to_decimal(ins[2])
        # i = 4 + label << 2
        i = label

        encoding = immediate_encoding(o,s,t,i)

    elif syntax == "Jump":
        o = opcode
        i = to_decimal(ins[1])

        encoding = jump_encoding(o,i)

    elif syntax == "LoadStore":
        o = opcode
        t = int(ins[1][1])

        i, s = ins[2].split(" ")
        i = to_decimal(i)
        s = int(s[2])

        encoding = immediate_encoding(o,s,t,i)
    
    
    else:
        print(f"{syntax} has not been implemented yet.")
        exit()

    output.write(f"{ct:03x}: {encoding}  # {string}")

    string = input.readline()
    ct += 4

input.close()
output.close()







