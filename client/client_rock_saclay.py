from smartcard.System import readers
import sys
import string 
import struct 
import ecdsa import SigningKey

public_key_pem = b'-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAE38NjBN
Rn/Pci2yVRa3CLnLUuI2JC/beh\n1y9TKV5YGp1v1QfBnZDSNHu5rQfy6hmaTer+Dyoe
lapySUnPDjfjU2bWt/6z/yZD\n6uPKUr/AgDxz7oVqvF+OH6IM6CJ4d92F\n-----END
 PUBLIC KEY-----\n'
public_key = SigningKey.from_pem(public_key_pem)



alphabet = string.ascii_letters
DEBUG = 1
def debug(*args):
    if DEBUG:
        print("[DEBUG]", *args)


def h2a(h):
    """Hex to array"""
    if len(h)%2 != 0:
        raise Exception("h must be hex and length multiple of 2")
    return [int(h[i:i+2], 16) for i in range(0,len(h),2)]

def a2h(a):
    return "".join([hex(e)[2:].zfill(2) for e in a])


# INSTALL THE APPLET HELPER
if len(sys.argv) == 2  and sys.argv[1] == "install":
    print("Client Rock Saclay Installation Helper")
    # Get ID
    while True:
        id = input("Donnez l'id: ")
        if not id.isdigit():
            print("Id doit être un numéro")
            continue
        id = int(id)
        if id <0 or id > 65535:
            print("Id doit etre entre 0 et 65535")
            continue
        break
    
    # Get PIN
    while True:
        pin = input("Donnez pin: ")
        if not pin.isdigit():
            print("PIN doit être un numéro")
            continue
        pin = int(pin)
        if pin <0 or pin > 9999:
            print("PIN doit etre entre 0 et 9999")
            continue
        break
    
    # Get Name
    while True:
        # Encoding?
        name = input("Donnez le nom: ")
        if len(name) >= 15:
            print("Le nom doit pas depasser les 15 caractères")
            continue
        good_alpha = True
        for e in name:
            if e not in alphabet:
                print("Le nom peut pas contenir des caractères spécieaux")
                good_alpha = False
                break
        if not good_alpha:
            continue
        break
    print(id, pin, name)
    id = struct.pack("!H", id)
    pin = struct.pack("!H", pin)
    name_length = struct.pack("B", len(name))
    name = name.encode()
    args = id+pin+name_length+name
    debug("param array", args)
    args = a2h(args)
    debug("param hex", args)
    print("gp -v --install RockSaclay221.cap --params", args)
    exit()

def array2str(a):
    return "".join([chr(e) for e in a])

def str2array(string):
    return [ord(e) for e in string]

def get_name():
    data, sw1, sw2 = connection.transmit([CLASS_APPLET, INS_GET_NAME,0x00,0x00,0x01,0x00,0x00])
    # print("[DEBUG]",hex(sw1),sw2)
    return array2str(data)
    

def set_name(name):
    a = [CLASS_APPLET, INS_SET_NAME, 0x00,0x00, len(name)] + str2array(name)+[0x00]
    print(a)
    connection.transmit(a)




class ClientRockSaclay(object):
    # Const
    CLASS_APPLET = 0xB0
    AID = h2a("0102030405060710")
    SELECT = h2a("00A4040008")
    # Instructions
    INS_DEBUG = 0x00
    INS_CHECK_PIN = 0x01
    INS_DEBITER_ARGENT = 0x02
    INS_GET_NAME = 0x03
    INS_GET_ID = 0x04
    INS_GET_CREDITS = 0x05

    
    

    def __init__(self):
        self.connection = readers()[0].createConnection()
        self.connection.connect()
    
    def transmit(self, *args):
        arg = []
        for e in args:
            if isinstance(e, list):
                arg += e
            elif isinstance(e, bytes):
                arg += list(e)
            elif isinstance(e, str):
                arg += h2a(e)
            elif isinstance(e, int):
                if e < 0 or e > 255:
                    raise Exception(f"int must be byte 0-255 {e}")
                arg.append(e)
            else:
                raise Exception(f"can't hadnle type {type(e)} in transmit")
        debug("transmit", arg)
        data, sw1, sw2 = self.connection.transmit(arg)
        if sw1 != 0x90 and sw2 != 0x00:
            raise Exception(f"Code error not OK code {hex(sw1)} {hex(sw2)}")
        debug("returned data", data)
        return data


    def select(self):
        self.transmit(ClientRockSaclay.SELECT, ClientRockSaclay.AID)

    def instruction(self, inst, *args):
        return self.transmit(ClientRockSaclay.CLASS_APPLET, inst, b"\x00\x00",*args )
    # API with javacard
    def get_name(self):
        data = self.instruction(ClientRockSaclay.INS_GET_NAME)
        return array2str(data)
    
    def get_id(self):
        data = self.instruction(ClientRockSaclay.INS_GET_ID)
        return struct.unpack("!H", bytes(data))[0]
    
    def get_credits(self):
        data = self.instruction(ClientRockSaclay.INS_GET_CREDITS)
        return struct.unpack("!H", bytes(data))[0]

    def debug(self):
        data =  self.instruction(ClientRockSaclay.INS_DEBUG)
        assert len(data) == 20
        id, credits, name_length, name =  struct.unpack("!HHB15s", bytes(data))

        print("id", id)
        print("credits", credits)
        print("name length", name_length)
        print("name", name)


if __name__ == "__main__":
    debug("test")
    client = ClientRockSaclay()
    client.select()
    print(client.get_name())
    print("id", client.get_id())
    print("credits", client.get_credits())
    
    
