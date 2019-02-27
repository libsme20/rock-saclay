package rock;

import javacard.framework.APDU;
import javacard.framework.Applet;
import javacard.framework.ISO7816;
import javacard.framework.ISOException;
import javacard.framework.Util;
 
public class RockSaclay extends Applet {
        public static final byte CLA_MONAPPLET = (byte) 0xB0;
        
        public static final byte INS_GET_NAME = 0x00;
        public static final byte INS_SET_NAME = 0x01;
        
        /* Attributs */
        private byte[] name = {0x6e,0x61,0x7a,0x69,0x6d,0x65};
        private byte[] hello = {0x00,0x01,0x02,0x03,0x04,0x05};
        /* Constructeur */
        private RockSaclay() {
               
        }
 
        public static void install(byte bArray[], short bOffset, byte bLength) throws ISOException {
               new RockSaclay().register();
        }


public void process(APDU apdu) throws ISOException {
    byte[] buffer = apdu.getBuffer();
    
    if (this.selectingApplet()) return;
    
    if (buffer[ISO7816.OFFSET_CLA] != CLA_MONAPPLET) {
            ISOException.throwIt(ISO7816.SW_CLA_NOT_SUPPORTED);
    }

    switch (buffer[ISO7816.OFFSET_INS]) {
            case INS_GET_NAME:
                    Util.arrayCopy(name, (byte)0, buffer, (byte)0, (byte)name.length);
                    apdu.setOutgoingAndSend((short) 0, (short) name.length);
                    break;
                    
            case INS_SET_NAME:
                    apdu.setIncomingAndReceive();
                    Util.arrayCopy(buffer, ISO7816.OFFSET_CDATA, name, (byte)0, ISO7816.OFFSET_LC);
                    break;
                    
            default:
                    ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
    }
}
}
