package rock;

import javacard.framework.APDU;
import javacard.framework.Applet;
import javacard.framework.ISO7816;
import javacard.framework.ISOException;
import javacard.framework.Util;
import javacard.framework.OwnerPIN;
import javacard.security.KeyPair;
import javacard.security.KeyBuilder;
import javacard.security.Signature;
import javacard.security.RSAPrivateKey;
import javacard.security.RSAPublicKey;
import javacard.security.CryptoException;

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
    public static final byte INS_GET_PUBLIC_KEY = 0x08;
    public static final byte INS_GET_TRANSACTION_ID = 0x09;
    public static final byte INS_INTI_APPLET = 0x0a;
    public static final byte INS_TEST_DEBUG = 0x7f;
    
    /* Exceptions */
    static final short SW_INSUFFICIENT_CREDITS = 0x7201;
    static final short SW_NOT_A_SHORT_VALUE = 0x7202;
    static final short SW_PIN_NOT_CHECKED = 0x7203;
        
    
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
    private Signature signature_transactions=null;
    private RSAPrivateKey privatekey;
    private RSAPublicKey publickey;
    private KeyPair keypair;
    private short transactionId = 0;
    
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

        
        //KeyPair keypair = new KeyPair(KeyPair.ALG_RSA, KeyBuilder.LENGTH_RSA_1024);
        KeyPair keypair = new KeyPair(KeyPair.ALG_RSA_CRT, KeyBuilder.LENGTH_RSA_1024);
        
    }
    

    public byte[] sign_transaction(short idVendeur, short transaction_montant){
        short bufferLength = Short.BYTES*4;
        byte[] buffer = new byte[bufferLength];
        byte[] signatureData = new byte[Signature.ALG_RSA_SHA_PKCS1_PSS];
        Util.setShort(buffer, (short) 0, idVendeur);
        Util.setShort(buffer, (short) Short.BYTES, transaction_montant);
        Util.setShort(buffer, (short) 4, this.id);
	Util.setShort(buffer, (short) 6, this.transactionId);
        this.signature_transactions.sign(buffer, (short) 0, bufferLength, signatureData, (short) 0);
        return signatureData;
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
            
            case INS_GET_TRANSACTION_ID:
                this.get_transaction_id(buffer, apdu);
                break;

            case INS_GET_TRIES_REMAINING:
                this.get_tries_remaining(buffer ,apdu);
                break;

            case INS_GET_SIGNATURE:
                this.get_signature(buffer, apdu);
                break;

            case INS_GET_PUBLIC_KEY:
                this.get_public_key(buffer, apdu);
                break;
            
            case INS_DEBUG:
                this.debug(buffer, apdu);
                break;

            case INS_TEST_DEBUG:
                this.test_debug(buffer, apdu);
                break;

            default:
                ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
        }
    }

    public void init_applet(){
        try {
            if (this.signature_transactions != null){
                return;
            }
            ISOException.throwIt((short)11);
            this.privatekey = (RSAPrivateKey)(keypair.getPrivate());
            
            this.publickey = (RSAPublicKey) keypair.getPublic();
            
            // Maybe false should be change,
            this.signature_transactions = Signature.getInstance(
                Signature.ALG_ECDSA_SHA,
                false
            );
            this.signature_transactions.init(privatekey, Signature.MODE_SIGN);
       } catch (CryptoException e) {
            short reason = e.getReason();
            ISOException.throwIt(reason);
       }
        
    }
    public void debug(byte[] buffer, APDU apdu){
        // TODO not in raw
        // 2 id 2 credits 1 length 15 names
        Util.setShort(buffer, (short)0, this.id);
        Util.setShort(buffer, (short)2, this.credits);
        buffer[4] = this.name_length;
        Util.arrayCopy(this.name, (short)0,buffer,(short)5,(short)NAME_LENGTH);
        apdu.setOutgoingAndSend((short) 0, (short) 20);
    }

    public void test_debug(byte[] buffer, APDU apdu){
        
       
    }

    public void is_authenticated() throws ISOException {
        if (! this.pin.isValidated()){
            ISOException.throwIt(SW_PIN_NOT_CHECKED);
        }
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

    
    public void get_public_key(byte[] buffer, APDU apdu){
        this.publickey.getExponent(buffer, (short) 0);
        this.publickey.getModulus(buffer, (short) 2);
            //Util.arrayCopy(this.publickey, (short)0,buffer,(short)0, KeyBuilder.LENGTH_EC_FP_192 );
        short sizePK =  KeyBuilder.LENGTH_RSA_1024 + 2;
        apdu.setOutgoingAndSend((short) 0, sizePK);
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
        this.is_authenticated();
        Util.setShort(buffer, (short)0, this.credits);
        apdu.setOutgoingAndSend((short) 0, (byte)2);
    }

    public void get_transaction_id(byte[] buffer, APDU apdu){
        this.is_authenticated();
        Util.setShort(buffer, (short)0, this.transactionId);
        apdu.setOutgoingAndSend((short) 0, (byte)2);
    }
    public void debit_credits(byte[] buffer, APDU apdu){
        this.is_authenticated();

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
	    this.transactionId ++;
    }
}
