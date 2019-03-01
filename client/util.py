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


