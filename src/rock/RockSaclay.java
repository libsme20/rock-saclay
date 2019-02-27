package rock;

import javacard.framework.APDU;
import javacard.framework.Applet;
import javacard.framework.ISO7816;
import javacard.framework.ISOException;
import javacard.framework.Util;
import javacard.framework.OwnerPIN;
 
public class RockSaclay extends Applet {
        public static final byte CLA_MONAPPLET = (byte) 0xB0;
        
        public static final byte INS_CHECK_PIN = 0x00;
        public static final byte INS_DEBITER_ARGENT = 0x01;
        
        /* Attributs */
        private byte[] name = new byte[15];
        private byte name_length = 0;
        private OwnerPIN pin;
        private short argent = 500;
        private short id;
        /* Constructeur */
        private RockSaclay(byte[] array, short offset, byte length) {
                // calculer les offset/length 
                byte aid_length = array[offset];
                byte control_length = array[(short)(offset+(short)aid_length+(short)1)];
                byte offset_param_length = array[(short)(offset+1+(short)aid_length+1+(short)control_length)];
                short offset_param = (short)array[(short)(offset+1+(short)aid_length+1+(short)control_length+1)];
                

                // 2 bytes id
                id = Util.makeShort(array[offset_param], array[(short)(offset_param+1)]);
                offset_param += 2;

                // 2 bytes pin
                pin.update(array, offset_param, (byte)2);
                offset_param += 2;

                // 1 byte len name, n bytes name
                name_length = array[offset_param];
                // TODO: check length
                Util.arrayCopy(array, (short)(offset_param+1), name, (short)0, name_length);
                offset_param += 1 + name_length;

        }
 
        public static void install(byte bArray[], short bOffset, byte bLength) throws ISOException {
               new RockSaclay(bArray, bOffset, bLength).register();
        }


public void process(APDU apdu) throws ISOException {
    byte[] buffer = apdu.getBuffer();
    
    if (this.selectingApplet()) return;
    
    if (buffer[ISO7816.OFFSET_CLA] != CLA_MONAPPLET) {
            ISOException.throwIt(ISO7816.SW_CLA_NOT_SUPPORTED);
    }

    switch (buffer[ISO7816.OFFSET_INS]) {
            case INS_CHECK_PIN:
                    Util.arrayCopy(name, (byte)0, buffer, (byte)0, (byte)name.length);
                    apdu.setOutgoingAndSend((short) 0, (short) name.length);
                    break;
                    
            case INS_DEBITER_ARGENT:
                    apdu.setIncomingAndReceive();
                    Util.arrayCopy(buffer, ISO7816.OFFSET_CDATA, name, (byte)0, ISO7816.OFFSET_LC);
                    break;
                    
            default:
                    ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
    }
}
}
