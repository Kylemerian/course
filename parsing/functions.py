def xor_(a, b):
    return a ^ b

def shr_(a, offset):
    return (a >> offset) & 0xffffffffffffffff

def ashr_(a, offset):
    return (a >> offset) & 0xffffffffffffffff

def shl_(a, offset):
    return (a << offset) & 0xffffffffffffffff

def new_array_(a):
    return [0 for _ in range(a)]

def sizeof_(a):
    return a.__sizeof__()

def or_(a, b):
    return (a | b)

def and_(a, b):
    return (a & b)

def getDictForFuncs():
    functions = {}
    functions['xor'] = xor_
    functions['shr'] = shr_
    functions['ashr'] = ashr_
    functions['shl'] = shl_
    functions['new_array'] = new_array_
    functions['sizeof'] = sizeof_
    functions['or_'] = or_
    functions['and_'] = and_

    return functions