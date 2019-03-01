import sys
import struct 
import time

from ecdsa import VerifyingKey, BadSignatureError
from smartcard.Exceptions import NoCardException
from smartcard.System import readers

from util import debug, h2a, a2h, a2s, s2a


public_key_pem =b'-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAE38NjBNRn/Pci2yVRa3CLnLUuI2JC/beh\n1y9TKV5YGp1v1QfBnZDSNHu5rQfy6hmaTer+DyoelapySUnPDjfjU2bWt/6z/yZD\n6uPKUr/AgDxz7oVqvF+OH6IM6CJ4d92F\n-----END PUBLIC KEY-----\n'
public_key = VerifyingKey.from_pem(public_key_pem)


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
    INS_GET_TRIES_REMAINING = 0x06
    INS_GET_SIGNATURE = 0x07

    # Exceptions
    exceptions = {
        0x7203: "SW_PIN_NOT_CHECKED"
    }

    def __init__(self):
        pass

    def wait_carte(self):
        while True:
            r = readers()
            if len(r):
                break
            time.sleep(0.5)
        self.connection = r[0].createConnection()
        while True:
            try:
                self.connection.connect()
                break
            except NoCardException:
                time.sleep(0.5)
        print("Carte insérée")
    
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
        error_code = struct.unpack("!H", bytes([sw1, sw2]))[0]
        if error_code != 0x9000:
            error_msg = f"Code error not OK code {hex(error_code)}"
            if error_code in ClientRockSaclay.exceptions:
                error_msg += ", "+ClientRockSaclay.exceptions[error_code]
            raise Exception(error_msg)
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

    def get_tries_remaning(self):
        data = self.instruction(ClientRockSaclay.INS_GET_TRIES_REMAINING)
        return struct.unpack("!B", bytes(data))[0]

    def get_signature(self):
        data =  self.instruction(ClientRockSaclay.INS_GET_SIGNATURE)
        return bytes(data)
    
    def debit_credits(self, debit):
        debit = struct.pack("!H",debit)
        self.instruction(ClientRockSaclay.INS_DEBIT_CREDITS, 2, debit)

    def check_pin(self, pin):
        pin = struct.pack("!H", pin)
        data = self.instruction(ClientRockSaclay.INS_CHECK_PIN, 2, pin)
        debug("pin", data[0], data[1])
        return data
    
    def debug(self):
        data =  self.instruction(ClientRockSaclay.INS_DEBUG)
        assert len(data) == 20
        id, credits, name_length, name =  struct.unpack("!HHB15s", bytes(data))

        print("id", id)
        print("credits", credits)
        print("name length", name_length)
        print("name", name)

    def verify(self):
        id = struct.pack('!H', self.get_id())
        name = self.get_name().encode()
        data = id + name
        signature = self.get_signature()
        try:
            public_key.verify(signature, data)
        except BadSignatureError:
            print("[EXIT] Fake Card, wrong signature")
            sys.exit(0)
        print("Carte vérifiée")


    

if __name__ == "__main__":
    print("--- Rock Saclay ----")
    print("Insérez votre carte")

    client = ClientRockSaclay()
    client.wait_carte()
    client.select()
    client.verify()
    sys.exit(0)

    pin = input("Insérez votre code PIN: ")
    debug("test")
    client = ClientRockSaclay()
    client.select()
    print("signature", client.get_signature())
    print("verify", client.verify())
    print(client.check_pin(5555))
    #    print("bad signature: fake card !")
    print(client.get_name())
    print("id", client.get_id())
    print("credits", client.get_credits())
    client.debit_credits(20)
    print("credits", client.get_credits())
    print("tries remanging", client.get_tries_remaning())
    print(client.check_pin(4444))
    print(client.check_pin(5555))
    print(client.check_pin(5555))

    

