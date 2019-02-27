from smartcard.System import readers
r=readers()
connection=r[0].createConnection()
connection.connect()

CLASS_APPLET = 0xB1
INS_GET_NAME = 0x00
INS_SET_NAME = 0x01


#Selection AID
data, sw1, sw2 = connection.transmit([0x00,0xA4,0x04,0x00,0x08,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x09])


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

if __name__ == "__main__":
    print("Hello", get_name())
    set_name("nazime")
    print("Hello", get_name())

connection.disconnect()
