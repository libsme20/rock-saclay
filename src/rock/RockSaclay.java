package rock;

import javacard.framework.APDU;
import javacard.framework.Applet;
import javacard.framework.ISO7816;
import javacard.framework.ISOException;
import javacard.framework.Util;
import javacard.framework.OwnerPIN;
import java.nio.ByteBuffer;
 
public class RockSaclay extends Applet {
    
    public static final byte CLA_MONAPPLET = (byte) 0xB0;
    public static final byte INS_CHECK_PIN = 0x00;
    public static final byte INS_DEBIT_CREDITS = 0x01;
    
    /* Exceptions */
    static final short SW_INSUFFICIENT_CREDITS = 0x7201;
    static final short SW_NOT_A_SHORT_VALUE = 0x7202;
        
    
    /* Attributs */
    private byte[] name = new byte[15];
    private byte name_length = 0;
    private OwnerPIN pin;
    private short credits;
    private short id;
    /* Constructeur */
    private RockSaclay(byte[] array, short offset, byte length) {
	// calculer les offset/length
	this.credits = 500;
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
    
    /**
     * Debits account with toDebit value, 
     * @param toDebit
     * @exception ISOException if toDebit value is superior compared to toDebit value.
     */
    public void debit(short toDebit) throws ISOException{
	if((short)(this.credits - toDebit) >=0){
	    this.credits = (short)(this.credits - toDebit);
	    return;
	}
	ISOException.throwIt(SW_INSUFFICIENT_CREDITS);
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
            
	case INS_DEBIT_CREDITS:
	    apdu.setIncomingAndReceive();
	    // Checks if buffer matches a short length.
	    if(ISO7816.OFFSET_LC != Short.BYTES){
		ISOException.throwIt(SW_NOT_A_SHORT_VALUE);
	    }
	    // Gets value from the buffer and store it into toDebitBytes value
	    byte[] toDebitBytes = new byte[Short.BYTES];
	    Util.arrayCopy(
			   buffer,
			   buffer[ISO7816.OFFSET_CDATA],
			   toDebitBytes,
			   (short) 0,
			   (short) ISO7816.OFFSET_LC
			   );
	    // Converts in short
	    short toDebit = Util.makeShort(
					   toDebitBytes[0],
					   toDebitBytes[1]
					   );
	    // Apply debit
	    this.debit(toDebit);
	    // Converts credits to bytes and push into buffer.
	    byte[] creditsBytes = toBytes(this.credits);
	    Util.arrayCopy(
			   creditsBytes,
			   (short) 0,
			   buffer,
			   (short) 0,
			   (short) creditsBytes.length
			   );
	    apdu.setOutgoingAndSend((short) 0, (short) Short.BYTES);
	    break;
	    
	default:
	    ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
	}
    }

    public static byte[] toBytes(short shortValue){
	return new byte[]{
	    (byte) (shortValue >> 8),
	    (byte) (shortValue)
	};
    }
}
