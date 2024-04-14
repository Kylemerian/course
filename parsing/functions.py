def xor_(a, b):
    return a ^ b

def shr_(a, offset):
    return (a >> offset) & 0xffffffffffffffff

# def ashr(a, offset):
#     return (a >> offset) & 0xffffffffffffffff

def shl_(a, offset):
    return (a << offset) & 0xffffffffffffffff

def new_array_(a):
    return [0] * a

def sizeof_(a):
    return a.__sizeof__()

def or_(a, b):
    return (a or b)

def and_(a, b):
    return (a and b)

def getDictForFuncs():
    functions = {}
    functions['xor'] = xor_
    functions['shr'] = shr_
    functions['shl'] = shl_
    functions['new_array'] = new_array_
    functions['sizeof'] = sizeof_
    functions['or'] = or_
    functions['and'] = and_

    return functions



# funciotns[""]