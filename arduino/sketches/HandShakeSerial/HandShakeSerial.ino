/* Simple Serial sender program to 'handshake' Arduino and RPi.
 *  RPi side of things is going to be controlled by Python
 *  See XXX.py code
 *  I only modified the original code available here:
 *  https://learn.sparkfun.com/tutorials/connecting-arduino-to-processing
 */

char HandShakeToken;
// JU 18/01/2019: Replaced by the default 'LED_BUILTIN', so don't have to worry about which pin is on each board
// int BUILTIN_LED_PIN = 13;
boolean LED_STATE = HIGH; 
boolean NewData = true;

void setup() {
  //initialize serial communications at a 9600 baud rate
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
  while (!Serial) {
    LED_STATE = !LED_STATE; //flip LED_STATE
    digitalWrite(LED_BUILTIN, LED_STATE);
    delay(100);
  }
}

void loop()
{
  recvOneChar();
  sendBackOneChar();
}

void recvOneChar() 
{
  
  if (Serial.available()) {
    HandShakeToken = Serial.read();
    LED_STATE = !LED_STATE; //flip LED_STATE
    digitalWrite(LED_BUILTIN, LED_STATE);
    NewData = true;
    delay(200);
  }
} 

void sendBackOneChar() 
{
  if (NewData == true) {
    Serial.print(HandShakeToken);
    LED_STATE = !LED_STATE; //flip LED_STATE
    digitalWrite(LED_BUILTIN, LED_STATE);
    Serial.flush();
    NewData = false;
  }
}

