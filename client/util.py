DEBUG = 0
def debug(*args):
    if DEBUG:
        print("[DEBUG]", *args)


def h2a(h):
    """Hex to array"""
    if len(h)%2 != 0:
        raise Exception("h must be hex and length multiple of 2")
    return [int(h[i:i+2], 16) for i in range(0,len(h),2)]

def a2h(a):
    """Array to hex"""
    return "".join([hex(e)[2:].zfill(2) for e in a])

def a2s(a):
    """Array to string."""
    return "".join([chr(e) for e in a])

def s2a(string):
    """String to array."""
    return [ord(e) for e in string]

def input_int(msg="", min=None, max=None):
    # TODO accept negative number
    while True:
        x = input(msg)
        if not x.isdigit():
            print("Not a number")
            continue
        x = int(x)
        if min and x < min:
            print("Minimum", min)
            continue
        if max and x > max:
            print("Minimum", max)
            continue
        break
    return x

def input_str(msg="", min_length=None, max_length=None, alphabet=None):
    while True:
        x = input(msg)
        if min_length and len(x) < min_length:
            print("Minimum length", min_length)
            continue
        if max_length and len(x) > max_length:
            print("Maximum length", max_length)
            continue
        if alphabet:
            good_alpha = True
            for e in x:
                if e not in alphabet:
                    print("Bad character")
                    good_alpha = False
                    break
            if not good_alpha:
                continue
        break
    return x
