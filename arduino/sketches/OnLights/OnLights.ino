/*
  This code is based on Blink, from the source Arduino library
  Turns on the Arduino built-in LED and blink it for three times 
  every 2 second to show the connection is working.
  This is not a 'handshake' protocol to test the serial communication
  because, it doesn't test the serial communication route port.
  
  This example code is in the public domain.

  Modified by Jose Ulloa (jose.ulloa@isandex.com) on 06/07/2018
 */
 
// Pin 13 has an LED connected on most Arduino boards.
// give it a name:
int BUILTIN_LED_PIN = 13;

// the setup routine runs once when you press reset:
void setup() {                
  // initialize the digital pin as an output.
  pinMode(BUILTIN_LED_PIN, OUTPUT);     
}

// the loop routine runs over and over again forever:
void loop() {
  digitalWrite(BUILTIN_LED_PIN, HIGH);  // turn the LED on (HIGH is the voltage level)
  delay(2000);                          // wait for 2s
  for (int flicker = 0; flicker < 3; flicker++) {
    digitalWrite(BUILTIN_LED_PIN, LOW); // turn the LED off by making the voltage LOW
    delay(200);                         // wait for 200ms
    digitalWrite(BUILTIN_LED_PIN, HIGH);  // turn the LED on (HIGH is the voltage level)
    delay(200);                         // wait for 200ms
  }
}
