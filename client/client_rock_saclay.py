import sys
import struct 


from smartcard.System import readers
from ecdsa import SigningKey


from util import debug, h2a, a2h, a2s, s2a
b'-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAE38NjBNRn/Pci2yVRa3CLnLUuI2JC/beh\n1y9TKV5YGp1v1QfBnZDSNHu5rQfy6hmaTer+DyoelapySUnPDjfjU2bWt/6z/yZD\n6uPKUr/AgDxz7oVqvF+OH6IM6CJ4d92F\n-----END PUBLIC KEY-----\n'
public_key = SigningKey.from_pem(public_key_pem)


class ClientRockSaclay(object):
    # Const
    CLASS_APPLET = 0xB0
    AID = h2a("0102030405060710")
    SELECT = h2a("00A4040008")
    # Instructions
    INS_DEBUG = 0x00
    INS_CHECK_PIN = 0x01
    INS_DEBIT_CREDITS = 0x02
    INS_GET_NAME = 0x03
    INS_GET_ID = 0x04
    INS_GET_CREDITS = 0x05

    def __init__(self):
        # Constructeur
        self.connection = readers()[0].createConnection()
        self.connection.connect()
    
    def transmit(self, *args):
        # Methode basique pour envoyer n'importe quoi a la javacard
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
        # Select l'application avec son AID
        self.transmit(ClientRockSaclay.SELECT, ClientRockSaclay.AID)

    def instruction(self, inst, *args):
        # Toutes les instructions pass par cette fonctions
        return self.transmit(ClientRockSaclay.CLASS_APPLET, inst, b"\x00\x00",*args )

    # API with javacard
    def get_name(self):
        data = self.instruction(ClientRockSaclay.INS_GET_NAME)
        return a2s(data)
    
    def get_id(self):
        data = self.instruction(ClientRockSaclay.INS_GET_ID)
        return struct.unpack("!H", bytes(data))[0]
    
    def get_credits(self):
        data = self.instruction(ClientRockSaclay.INS_GET_CREDITS)
        return struct.unpack("!H", bytes(data))[0]

    def get_signature(self):
        pass
    
    def debit_credits(self, debit):
        debit = struct.pack("!H",debit)
        self.instruction(ClientRockSaclay.INS_DEBIT_CREDITS, 2, debit)

    def debug(self):
        data =  self.instruction(ClientRockSaclay.INS_DEBUG)
        assert len(data) == 20
        id, credits, name_length, name =  struct.unpack("!HHB15s", bytes(data))

        print("id", id)
        print("credits", credits)
        print("name length", name_length)
        print("name", name)

    def verify(self):
        return public_key.verify(
            self.get_signature, 
            struct.pack('!H', self.get_id) + self.get_name.encode()
            )


if __name__ == "__main__":
    debug("test")
    client = ClientRockSaclay()
    client.select()
    if(not verify()):
        print("bad signature: fake card !")
    print(client.get_name())
    print("id", client.get_id())
    print("credits", client.get_credits())
    client.debit_credits(20)
    print("credits", client.get_credits())


