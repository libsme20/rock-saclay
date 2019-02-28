#!/usr/bin/env python3
import sys
import string 
import struct

from ecdsa import SigningKey, NIST384p

from util import debug, h2a, a2h

alphabet = string.ascii_letters

#private_key = SigningKey.generate(curve=NIST384p)
private_key_string = b'-----BEGIN EC PRIVATE KEY-----\nMIGkAgEBBDAfR/wtBhgTA36/CciBuwBZ4JvdbsJfgQoUiktFiApgslqe9JAqE49c\nD3Oxs1HxMdygBwYFK4EEACKhZANiAATfw2ME1Gf89yLbJVFrcIuctS4jYkL9t6HX\nL1MpXlganW/VB8GdkNI0e7mtB/LqGZpN6v4PKh6VqnJJSc8ON+NTZta3/rP/JkPq\n48pSv8CAPHPuhWq8X44fogzoInh33YU=\n-----END EC PRIVATE KEY-----\n'  
private_key= SigningKey.from_pem(private_key_string)
public_key = private_key.get_verifying_key()
print(public_key.to_pem())

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
    signature = private_key.sign(id+name)
    args = id+pin+name_length+name+signature
    debug("signature", signature)
    debug("param array", args)
    args = a2h(args)
    debug("param hex", args)

    print("gp -v --install RockSaclay221.cap --params", args)
    exit()
