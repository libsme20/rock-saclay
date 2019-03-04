#!/usr/bin/env python3
import sys
import string 
import struct
import os


from ecdsa import SigningKey, NIST384p

from util import debug, h2a, a2h, input_int, input_str

alphabet = string.ascii_letters

#private_key = SigningKey.generate(curve=NIST384p)
private_key_string = b'-----BEGIN EC PRIVATE KEY-----\nMIGkAgEBBDAfR/wtBhgTA36/CciBuwBZ4JvdbsJfgQoUiktFiApgslqe9JAqE49c\nD3Oxs1HxMdygBwYFK4EEACKhZANiAATfw2ME1Gf89yLbJVFrcIuctS4jYkL9t6HX\nL1MpXlganW/VB8GdkNI0e7mtB/LqGZpN6v4PKh6VqnJJSc8ON+NTZta3/rP/JkPq\n48pSv8CAPHPuhWq8X44fogzoInh33YU=\n-----END EC PRIVATE KEY-----\n'  
private_key= SigningKey.from_pem(private_key_string)








class RockSaclayInstall():
    def __init__(self):
        self.load_users()
    
    def load_users(self):
        if os.path.isfile("users.txt"):
            data = open("users.txt").read()
            data = data.strip()
            if data:
                data = data.split("\n")
                for i in range(len(data)):
                    data[i] = data[i].split(";")
            else:
                data = []
            self.users = data
        else:
            open("users.txt","w")
            self.users = [] 
    
    def add_user(self, id, name):
        self.users.append([id, name])
        self.save_users()
    
    def install(self):
        # Get ID
        id = input_int("Donnez l'id: ", 1, 65535)
        pin = input_int("Donnez le code PIN: ", 0, 9999)
        name = input_str("Donnez le nom: ", max_length=15, alphabet=alphabet)

        # Get Name
        print("id",id, "- PIN",pin,"- nom", name)
        self.add_user(id, name)
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
        
        

    def save_users(self):
        f = open("users.txt", "w")
        for user in self.users:
            f.write(";".join(map(str,user))+"\n")

    def reset_users(self):
        self.users = []
        open("users.txt", "w")
    
    def show_users(self):
        if not self.users:
            print("Aucune utilisateurs")
            return
        
        print("-"*29)
        print(f"| {'id':<8}| {'nom':<16}|")
        print("-"*29)
        for user in self.users:
            print(f"| {user[0]:<8}| {user[1]:<16}|")
        print("-"*29)


if __name__ == "__main__":
    # actions: install carte, consulter cartes, reset all, supprimer carte
    print("---- Rock Saclay Installation ----")
    client = RockSaclayInstall()
    while True:
        print("*"*50)
        print("Choisir une action")
        print("*"*50)
        print("1) Ajouter un utilisateur")
        print("2) Consulter les utilisateurs")
        print("3) Supprimer un utilisateur")
        print("4) Supprimer les utilisateurs")
        print("5) Quitter")
        choix = input_int("> ", min=1, max=5)
        if choix == 1:
            print("Ajouter un utilisateur")
            client.install()
        elif choix ==2:
            print("Consulter les utilisateurs")
            client.show_users()
        elif choix == 4:
            print("Supprimer les utilisateurs")
            client.reset_users()
        elif choix == 5:
            print("Quitter")
            break
        print()