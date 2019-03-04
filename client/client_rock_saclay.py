import sys
import struct 
import time

from ecdsa import VerifyingKey, BadSignatureError
from smartcard.Exceptions import NoCardException
from smartcard.System import readers

from util import debug, h2a, a2h, a2s, s2a, input_int

MAX_SHORT = 2**16-1

public_key_pem =b'-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAE38NjBNRn/Pci2yVRa3CLnLUuI2JC/beh\n1y9TKV5YGp1v1QfBnZDSNHu5rQfy6hmaTer+DyoelapySUnPDjfjU2bWt/6z/yZD\n6uPKUr/AgDxz7oVqvF+OH6IM6CJ4d92F\n-----END PUBLIC KEY-----\n'
public_key = VerifyingKey.from_pem(public_key_pem)

class RockSaclayException(Exception):
    pass

class SW_INSUFFICIENT_CREDITS(RockSaclayException):
    pass

 

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
    INS_GET_PUBLIC_KEY = 0x08
    INS_GET_TRANSACTION_ID = 0x09
    INS_TEST_DEBUG = 0x7f

    # Exceptions
    exceptions = {
        0x7201:SW_INSUFFICIENT_CREDITS,
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
                raise ClientRockSaclay.exceptions[error_code](error_msg)
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
    
    def test_debug(self):
        self.instruction(ClientRockSaclay.INS_TEST_DEBUG)

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

    def vendre(self):
        # Vérifier si la carte est vérouillé
        if not self.get_tries_remaning():
            print("0 Essay restant, carte vérouillé")
            sys.exit(1)
        
        # Insertion PIN
        while True:
            pin = input_int("Insérez votre code PIN: ", 0, 9999)
            checked, attempt = self.check_pin(pin)
            if checked:
                print("code PIN bon")
                break
            # bad pin
            if attempt:
                print("code PIN faux, essaye restant", attempt)
                continue
            # no more pin
            else:
                print("0 Essay restant, carte vérouillé")
                break
        print()

        # user information
        print("---- information utilisateur ----")
        print("id:", self.get_id())
        print("nom:", self.get_name())
        print("credits:", self.get_credits())
        print()

        # Debiter
        print("---- debiter montant ----")
        debit = input_int("Choisir montant à débiter: ", min=0, max=MAX_SHORT)
        try:
            self.debit_credits(debit)
            print("Crédit restant", self.get_credits())
        except SW_INSUFFICIENT_CREDITS:
            print("Solde insufisant", self.get_credits())
        print()


    
class RoRockSaclayVente():
    def vendre(self):
        pass

if __name__ == "__main__":
    print("---- Rock Saclay Vente ----")
    print("Insérez votre carte")
    vente = RoRockSaclayVente()
    while True:
        print("Choisir une action")
        print("1) Vendre à un client")
        print("2) Quitter")
        choix = input_int("> ", min=1, max=2)
        if choix == 1:
            client = ClientRockSaclay()
            client.wait_carte()
            client.select()
            client.verify()
            client.vendre()
        elif choix == 2:
            break
        print()

    

    



    

