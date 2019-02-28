package rock;

import javacard.framework.APDU;
import javacard.framework.Applet;
import javacard.framework.ISO7816;
import javacard.framework.ISOException;
import javacard.framework.Util;
import javacard.framework.OwnerPIN;

public class RockSaclay extends Applet {
    
    public static final byte CLA_MONAPPLET = (byte) 0xB0;
    
    // Instructions
    public static final byte INS_DEBUG = 0x00;
    public static final byte INS_CHECK_PIN = 0x01;
    public static final byte INS_DEBIT_CREDITS = 0x02;
    public static final byte INS_GET_NAME = 0x03;
    public static final byte INS_GET_ID = 0x04;
    public static final byte INS_GET_CREDITS = 0x05;
    public static final byte INS_GET_TRIES_REMAINING = 0x06;
    public static final byte INS_GET_SIGNATURE = 0x07;
    
    /* Exceptions */
    static final short SW_INSUFFICIENT_CREDITS = 0x7201;
    static final short SW_NOT_A_SHORT_VALUE = 0x7202;
        
    
    public static final byte PIN_TRY_LIMIT =3;
    public static final byte PIN_LENGTH =2;
    public static final byte SIGNATURE_LENGTH =96;
    public static final byte NAME_LENGTH = 15;
    /* Attributs */
    private byte[] name = new byte[NAME_LENGTH];
    private byte name_length = 0;
    private OwnerPIN pin;
    private short credits;
    private short id;
    private byte[] signature = new byte[SIGNATURE_LENGTH];
    
    /* Constructeur */
    private RockSaclay(byte array[], short offset, byte length) {
        
	    this.credits = 500;
        // calculer les offset/length 
        byte aid_length = array[offset];
        byte control_length = array[(short)(offset+(short)aid_length+(short)1)];
        byte oparam_length = array[(short)(offset+1+(short)aid_length+1+(short)control_length)];
        short offset_param = (short)(offset+1+(short)aid_length+1+(short)control_length+1);
        
        
        // 2 bytes id
        this.id = Util.makeShort(array[offset_param], array[(short)(offset_param+1)]);
        offset_param += 2;
        
        // 2 bytes pin
        this.pin = new OwnerPIN(PIN_TRY_LIMIT, PIN_LENGTH);
        this.pin.update(array, offset_param, PIN_LENGTH);
        offset_param += PIN_LENGTH;
        
        // 1 byte len name, n bytes name
        this.name_length = array[offset_param];
        // TODO: check length
        Util.arrayCopy(array, (short)(offset_param+1), this.name, (short)0, this.name_length);
        offset_param += 1 + name_length;

        // signature
        Util.arrayCopy(array, offset_param, this.signature, (short)0, SIGNATURE_LENGTH);
        offset_param += SIGNATURE_LENGTH;
	
    }
    
    /**
     * Debits account with toDebit value, 
     * @param toDebit
     * @exception ISOException if toDebit value is superior compared to toDebit value.
     */
    public void debit(short toDebit) throws ISOException{
        if (toDebit > this.credits){
            ISOException.throwIt(SW_INSUFFICIENT_CREDITS);
        }
        this.credits -= toDebit;
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
                this.check_pin(buffer, apdu);
                break;
                    
            case INS_DEBIT_CREDITS:
                this.debit_credits(buffer, apdu);
                break;

            case INS_GET_NAME:
                this.get_name(buffer, apdu);
                break;
            
            case INS_GET_ID:
                this.get_id(buffer, apdu);
                break;
            
            case INS_GET_CREDITS:
                this.get_credits(buffer, apdu);
                break;

            case INS_GET_TRIES_REMAINING:
                this.get_tries_remaining(buffer ,apdu);
                break;

            case INS_GET_SIGNATURE:
                this.get_signature(buffer, apdu);
                break;
            
            case INS_DEBUG:
                this.debug(buffer, apdu);
                break;

            default:
                ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
        }
    }

    public void debug(byte[] buffer, APDU apdu){
        // TODO not in raw
        // 2 id 2 credits 1 length 15 names
        Util.setShort(buffer, (short)0, this.id);
        Util.setShort(buffer, (short)2, this.credits);
        buffer[4] = this.name_length;
        Util.arrayCopy(this.name, (short)0,buffer,(short)5,(short)NAME_LENGTH );
        apdu.setOutgoingAndSend((short) 0, (short) 20);
    }

    public void check_pin(byte[] buffer, APDU apdu){
        // Return 1(True/False), 1 number of attempt
        apdu.setIncomingAndReceive();
        byte validate = (byte)0;
        if (this.pin.isValidated()){
            validate = (byte)1;
        }else{
            if(pin.check(buffer, (short) ISO7816.OFFSET_CDATA, PIN_LENGTH)){
                validate = (byte)1;
            }else{
                validate = (byte)0;
            }
        }

        buffer[0] = validate;
        buffer[1] = this.pin.getTriesRemaining();

        apdu.setOutgoingAndSend((short) 0, (byte)2);
    }

    public void get_signature(byte[] buffer, APDU apdu){
        Util.arrayCopy(this.signature, (short)0,buffer,(short)0, SIGNATURE_LENGTH );
        apdu.setOutgoingAndSend((short) 0, SIGNATURE_LENGTH);
    }

    public void get_tries_remaining(byte[] buffer, APDU apdu){
        buffer[0] = this.pin.getTriesRemaining();
        apdu.setOutgoingAndSend((short) 0, (byte)1);
    }
    public void get_name(byte[] buffer, APDU apdu){
        Util.arrayCopy(this.name, (short)0,buffer,(short)0,(short)this.name_length );
        apdu.setOutgoingAndSend((short) 0, this.name_length);
    }

    public void get_id(byte[] buffer, APDU apdu){
        Util.setShort(buffer, (short)0, this.id);
        apdu.setOutgoingAndSend((short) 0, (byte)2);
    }

    public void get_credits(byte[] buffer, APDU apdu){
        Util.setShort(buffer, (short)0, this.credits);
        apdu.setOutgoingAndSend((short) 0, (byte)2);
    }

    public void debit_credits(byte[] buffer, APDU apdu){
        apdu.setIncomingAndReceive();
	    // Checks if buffer matches a short length.
	    if(buffer[ISO7816.OFFSET_LC] != Short.BYTES){
		    ISOException.throwIt(SW_NOT_A_SHORT_VALUE);
	    }
        // Gets value from the buffer and store it into toDebitBytes value
        short debiter = Util.getShort(buffer, (short)(ISO7816.OFFSET_LC+1));
        if (debiter > this.credits){
            ISOException.throwIt(SW_INSUFFICIENT_CREDITS);
        }
        this.credits -= debiter;

    }
}
