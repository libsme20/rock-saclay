#!/usr/bin/env python3

from ecdsa import SigningKey, NIST384p

#private_key = SigningKey.generate(curve=NIST384p)
#string = private_key.to_string();

private_key_string = b'-----BEGIN EC PRIVATE KEY-----\nMIGkAgEBBDAfR/wtBhgTA36/CciBuwBZ4JvdbsJfgQoUiktFiApgslqe9JAqE49c\nD3Oxs1HxMdygBwYFK4EEACKhZANiAATfw2ME1Gf89yLbJVFrcIuctS4jYkL9t6HX\nL1MpXlganW/VB8GdkNI0e7mtB/LqGZpN6v4PKh6VqnJJSc8ON+NTZta3/rP/JkPq\n48pSv8CAPHPuhWq8X44fogzoInh33YU=\n-----END EC PRIVATE KEY-----\n'  
private_key= SigningKey.from_pem(private_key_string)
public_key = private_key.get_verifying_key()
print(public_key.to_pem())

signature = private_key.sign("INFO".encode())

assert public_key.verify(signature, "INFO".encode())
