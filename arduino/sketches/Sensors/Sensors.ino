#include <openag_ds18b20.h>
#include <openag_atlas_do.h>
#include <openag_atlas_ec.h>
#include <openag_atlas_ph.h>
//#include <openag_dht11.h>
#include <openag_am2315.h>
#include <openag_soilmoisture.h>

// Sensor Instances (input argument is the pin number)
Ds18b20 ds18b20_1(2);    // Digital input #2
//AtlasDo atlas_do_1(8);   // i2c address corresponding to channel 0 (JU: see table in user guide)
AtlasEc atlas_ec_1(11);  // i2c address corresponding to channel 1 (JU: see table in user guide)
AtlasPh atlas_ph_1(13);  // i2c address corresponding to channel 2 (JU: see table in user guide)
//Dht11 dht11_1(3);
Am2315 am2315_1; // does not require pins, because it uses predefined pins (see Adafruit example)
SMoist smoist_1(A0); // Analog Input #0

// JU 03/01/2021 Actuator Instances (pumps)
// To make some actions, lets define the MESSAGES they can receive:
// PP_0 = "Peristaltic Pump OFF"
// PP_1 = "Peristaltic Pump ON"
// WP_0 = "Water Pump ON"
// WP_1 = "Water Pump ON"
const int WPUMP_RELAY_PIN = 4; // Peristalic watering pump Digital input #4
// (Next pin free (# is DHT11 if present))
const int SPUMP_RELAY_PIN = 7; // Water stirring pump Digital input #7
const long SPUMP_TIMER = 600000; // Timer in milliseconds for the stirring pump
const long WPUMP_TIMER =  30000; // Timer in milliseconds for the peristaltic
//  pump
long WATERING_START_TIME = 0;  // Counter time for peristaltic watering pump
long STIRRING_START_TIME = 0; // Counter time for water stirring pump
// bool WPUMP_ON = true;
// bool PPUMP_ON = Fatruelse;
unsigned long currentMillis = 0;


#define RELAY_ON LOW // Just to avoid the aparent inconsistency that the relay uses LOW to trigger
#define RELAY_OFF !RELAY_ON
// JU 03/01/2021 END Actuator Instances (pump)

// JU 23/01/2021 Includes a button to action the pump:
int RELAY_STATE = RELAY_ON;
int CurrBtnState = 0;
int LastBtnState = 0;
const int ONOFFBTN = 6;
// JU 23/01/2021 END button action pumps initialization

// Message string
String message = "";
bool stringComplete = false;
const unsigned int MESSAGE_LENGTH = 500;
float SAMPLING_PERIOD = 5000; // in milliseconds

// Main logic
void sensorLoop();
void updateLoop();

// Utility functions
void send_invalid_message_length_error(String msg);
void resetMessage();
void sendModuleStatus(Module &module, String name);
bool beginModule(Module &module, String name);
bool checkModule(Module &module, String name);
bool str2bool(String str);

// These functions are defined in the Arduino.h and are the framework.
void setup() {
  Serial.begin(9600);
// JU 03/01/2021: Initialise the RELAY (pumps)
  beginPump(WPUMP_RELAY_PIN, RELAY_OFF); // Ensure the RELAY is OFF at the start
  beginPump(SPUMP_RELAY_PIN, RELAY_OFF);  // Ensure the RELAY is OFF at the start
// JU 03/01/2021: END Initialise the RELAY (pump)
// JU 23/01/2021: Setup On/Off button (pump)
  pinMode(ONOFFBTN, INPUT);
// JU 23/01/2021 END button setup

  while(!Serial){
    // wait for serial port to connect, needed for USB
  }
  message.reserve(MESSAGE_LENGTH);

  // Begin sensors
 beginModule(ds18b20_1, "DS18B20 #1");
//  beginModule(atlas_do_1, "Atlas D.O. #1");
  beginModule(atlas_ec_1, "Atlas EC #1");
  beginModule(atlas_ph_1, "Atlas pH #1");
//  beginModule(dht11_1, "DHT11 #1");
  beginModule(am2315_1, "AM2315 #1");

  beginModule(smoist_1, "SMOIST #1");
}

void loop() {

//JU 03/01/2021  Tests the relay (use this to start testing how to send the instruction from python)
//  digitalWrite(WPUMP_RELAY_PIN, RELAY_ON); // turn on pump 1 seconds
//  delay(1000);
//  digitalWrite(WPUMP_RELAY_PIN, RELAY_OFF);  // turn off pump
//JU 03/01/2021 END Tests the relay

// JU 23/01/2021 Allows actioning the pump during normal operation of the code
  LastBtnState = pumpControl(WPUMP_RELAY_PIN, ONOFFBTN, LastBtnState);
//   CurrBtnState = digitalRead(ONOFFBTN);
//   RELAY_STATE = digitalRead(WPUMP_RELAY_PIN);

  // This makes the pump works WHILE pressing the button
//   if(LastBtnState != CurrBtnState) {
  // This makes the pump works during consecutive buttons press:
//   if (CurrBtnState == LOW && LastBtnState == HIGH) {
//     delay(10); // to solve debouncing
//     RELAY_STATE = !RELAY_STATE;
//   }
//   digitalWrite(WPUMP_RELAY_PIN, RELAY_STATE); // ledPin, !RELAY_STATE);
//   LastBtnState = CurrBtnState;
// JU 23/01/2021 END pump operation

  updateLoop();

  // JU 28/03/2021 Automate pumps (water and peristaltic pumps). I'm using
  // the previously defined messages blocks to get instructions from the RPi
//   the ideas here are:
//      - The RPi sends WP_0/WP_1 depending on the time of the date
//          hence the water pump works and stirs the water in the tank
//      - The RPi sends PP_0/PP_1 depending on the value of the humidity sensor
// This last one idea requires to enable the sensor, so for the time been,
// just switch it on at certains times, for e.g. 5 mins every day
//

  // If we have not received a message, then do nothing.  This lets our ROS
  // node control the message traffic.  For every message sent to this arduino
  // code, one is sent back.
  currentMillis = millis();
  if(! stringComplete){
    return;
  } else {
    if (message == "SPUMP\n") {
        STIRRING_START_TIME = currentMillis;
        action_pump(SPUMP_RELAY_PIN, RELAY_ON);
    } else if (message == "WPUMP\n") {
        WATERING_START_TIME = currentMillis;
        action_pump(WPUMP_RELAY_PIN, RELAY_ON);
        }
  }
  // JU Persitaltic Watering pump action:
  if (currentMillis - WATERING_START_TIME > WPUMP_TIMER) {
    action_pump(WPUMP_RELAY_PIN, RELAY_OFF);
  }
  // JU Water Stirring pump action:
  if (currentMillis - STIRRING_START_TIME > SPUMP_TIMER) {
    action_pump(SPUMP_RELAY_PIN, RELAY_OFF);
  }

  bool allSensorSuccess = checkSensorLoop();
  if(allSensorSuccess){
    sensorLoop();
  }

//  JU 03/01/2021: Here, it should go any instruction to the pump, based on the readings. 
//  These instructions are going to be sent from the raspberry
//....
}

// JU 02/04/2021: Create auxiliar functions to control the pumps. They should
//  be controllable automatically AND through the buttons (momentary buttons)
int pumpControl(int relayPin, int buttonPin, int prevState) {
  int currState = digitalRead(buttonPin);
  int relayState = digitalRead(relayPin);
  // This makes the pump works WHILE pressing the button
  // if(prevState != currState) {
  //    delay(10); // to solve debouncing
  //    relayState = !relayState;
  //  }
  // This makes the pump works during consecutive buttons press:
  if (currState == LOW && prevState == HIGH) {
    delay(10); // to solve debouncing
    relayState = !relayState;
  }
  digitalWrite(relayPin, relayState);
  return currState;
}

void action_pump(int relayPin, int relState){
    digitalWrite(relayPin, relState);
    }

void beginPump (int relayPin, int relayState){
    pinMode(relayPin, OUTPUT);
    digitalWrite(relayPin, relayState);
    return;
    }

// Runs inbetween loop()s, just takes any input serial to a string buffer.
// Runs as realtime as possible since loop has no delay() calls. (It shouldn't!)
// Note: the internal buffer in the Serial class is only 64 bytes!
void serialEvent() {
  if(stringComplete){
    resetMessage();
  }
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString but first check for potential overflow:
    // (this can happen if a few partial lines are received sequentially without newlines)
    if (message.length() == (MESSAGE_LENGTH - 2)) {
      message += '\n'; // 1 byte add + null terminator makes the full message length
      stringComplete = true;
      return;
    }
    message += inChar;
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n') {
      stringComplete = true;
      return;
    }
  }
}

// Run the update loop
void updateLoop(){
  ds18b20_1.update();

// JU 20190207: Add Temperature Compensation
// JU 20190214: After realising the firmware issue between v2.12 and v2.13, to keep compatibility
//              between both, I have to do the temperature compensation in a sequential way together
//              with the measurements. However, it appear to be not straightforward, as the basis of
//              this sketch is to stack all the messages and then flush the serial with them. Under
//              Under this, even the SUCCESS byte output by the command "T,<n>" will cause a problem:

//  dht11_1.update();
   am2315_1.update();

   smoist_1.update();

//   float curr_temp = am2315_1.get_air_temperature();
  float curr_temp = ds18b20_1.get_temperature();

//  atlas_do_1.set_temp_comp(curr_temp);
//  atlas_do_1.update();

  atlas_ec_1.set_temp_comp(curr_temp);
  atlas_ec_1.update();

  atlas_ph_1.set_temp_comp(curr_temp);
  atlas_ph_1.update();
}

bool checkSensorLoop(){
  bool allSensorSuccess = true;

  // Run Update on all sensors
  allSensorSuccess = checkModule(ds18b20_1, "DS18B20 #1") && allSensorSuccess;
//  allSensorSuccess = checkModule(atlas_do_1, "Atlas D.O. #1") && allSensorSuccess;
  allSensorSuccess = checkModule(atlas_ec_1, "Atlas EC #1") && allSensorSuccess;
  allSensorSuccess = checkModule(atlas_ph_1, "Atlas pH #1") && allSensorSuccess;
//  allSensorSuccess = checkModule(dht11_1, "DHT11 #1") && allSensorSuccess;
  allSensorSuccess = checkModule(am2315_1, "AM2315 #1") && allSensorSuccess;
  allSensorSuccess = checkModule(smoist_1, "SMOIST #1") && allSensorSuccess;
  return allSensorSuccess;
}

void sensorLoop(){
  // Prints the data in CSV format via serial.
  // Columns: status,hum,temp,co2,water_temperature,water_low,water_high,ph,ec
  Serial.print(OK);  Serial.print('{');
//  Serial.print("Status:");  Serial.print(OK);  Serial.print(',');
//  Serial.print("WTEMP:");
   Serial.print(ds18b20_1.get_temperature()); // in Celsius
//     Serial.print(0.0);
    Serial.print(',');
//  Serial.print("WDO:");
//    Serial.print(atlas_do_1.get_water_dissolved_oxygen()); // in mg/L
//    Serial.print(0.0); // in mg/L
//    Serial.print(',');
//  Serial.print("WEC:");
    Serial.print(atlas_ec_1.get_water_electrical_conductivity()); // in mS/cm
//    Serial.print(0.0); // in mS/cm
    Serial.print(',');
    Serial.print(atlas_ec_1.get_total_dissolved_solute()); // in ppm
//    Serial.print(0.0); // in ppm
    Serial.print(',');
    Serial.print(atlas_ec_1.get_salinity()); // in PSU
//    Serial.print(0.0); // in PSU
    Serial.print(',');
//  Serial.print("WPH:");
    Serial.print(atlas_ph_1.get_water_potential_hydrogen()); // in pH
//    Serial.print(0.0); // in pH
    Serial.print(',');
//    Serial.print("ATEMP:");
//    Serial.print(dht11_1.get_air_temperature());
    Serial.print(am2315_1.get_air_temperature());
    Serial.print(',');
//    Serial.print("AHUM:");
//    Serial.print(dht11_1.get_air_humidity());
    Serial.print(am2315_1.get_air_humidity());
    Serial.print(',');
    Serial.print(smoist_1.get_soilmoisture());
//    Serial.print(',');
  Serial.print('}');
  // https://www.arduino.cc/en/serial/flush
  // Wait until done writing.
  Serial.flush();
  delay(SAMPLING_PERIOD);
}

void send_invalid_message_length_error(String msg) {
  String clean_msg = msg;
  clean_msg.replace(',', '_');
  clean_msg.replace("\n", "");
  String warn = "2,Arduino,1,";
  warn += "Invalid message";
  warn += " ";
  warn += msg.length();
  warn += " bytes: |";
  warn += clean_msg;
  warn += "|\n";
  Serial.print(warn);
  Serial.flush();
}

// Resets our global string and flag.
void resetMessage() {
  for(unsigned i=0; i < MESSAGE_LENGTH; i++){
    message.setCharAt(i, '\0');
  }
  message = "";
  stringComplete = false;
}

void sendModuleStatus(Module &module, String name){
  Serial.print(module.status_level); Serial.print(',');
  Serial.print(name);  Serial.print(',');
  Serial.print(module.status_code);  Serial.print(',');
  Serial.print(module.status_msg);   Serial.print('\n');
  Serial.flush();
}

bool beginModule(Module &module, String name){
  bool status = module.begin() == OK;
  if(!status){
    sendModuleStatus(module, name);
  }
  return status;
}

bool checkModule(Module &module, String name){
  bool status = module.status_code == OK;
  if(!status){
    sendModuleStatus(module, name);
  }
  return status;
}

bool str2bool(String str){
  str.toLowerCase();
  return str.startsWith("true");
}
