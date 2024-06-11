/**
 *  \file openag_atlas_ec.cpp
 *  \brief Electrical conductivity sensor.
 */
#include "openag_atlas_ec.h"

AtlasEc::AtlasEc(int i2c_address) {
  status_level = OK;
  status_code = CODE_OK;
  status_msg = "WEC";
  _time_of_last_query = 0;
  _waiting_for_response = false;
  _i2c_address = i2c_address;
}

uint8_t AtlasEc::begin() {
  Wire.begin();
  Wire.setTimeout(40);
//  For some reason, it only 'detects' the first print line (maybe is longer than 32bytes?),
//  so will have to separate it in multiple transmissions:
  Wire.beginTransmission(_i2c_address);
  /** Enable EC reading (this is the minimum parameter to enable): **/
  Wire.print("O,EC,1");  // uS/cm
  _did_send = Wire.endTransmission();

  Wire.beginTransmission(_i2c_address);
  /** Enable(1)/Disable(0) TDS reading : **/
  /** (if disable ==> remember remove the corresponding strtok statement (lines 146-149) **/
  Wire.print("O,TDS,1"); // ppm
  _did_send += Wire.endTransmission();

  Wire.beginTransmission(_i2c_address);
  /** Enable(1)/Disable(0) Salinity reading : **/
  /** (if disable ==> remember remove the corresponding strtok statement (lines 146-149) **/
  Wire.print("O,S,1");   // PSU (Practical Salinity Unit)
  _did_send += Wire.endTransmission();

  Wire.beginTransmission(_i2c_address);
  /** Enable(1)/Disable(0) Specific Gravity reading: **/
  /** (if disable ==> remember remove the corresponding strtok statement (lines 146-149) **/
  Wire.print("O,SG,0");  // Must be 0 (i.e. only relevant for sea water (user guide, page 9))
  _did_send += Wire.endTransmission();

  if (_did_send == 0) {
    status_level = OK;
  } else {
    status_level= ERROR;
  }

  return status_level;
}

void AtlasEc::set_temp_comp(float currTemp) {
/************************************************************************************************/
/** IMPORTANT COMPATIBILITY ISSUE: Firmware version 2.13 and above of the EZO circuits allow to
     compensate the measurements in a single line: "RT,<n>". Previous versions (i.e. <=2.12) will
     have to be done in two steps: "T,<n>" and then "R" **/
    _Tcomp = String(currTemp,2);
}

uint8_t AtlasEc::update() {
  if (_waiting_for_response) {
    if (millis() - _time_of_last_query > 1400) // Processing delays: 600ms to read + 300ms Temp Comp = 900ms + 50%
    {
      read_response();
    }
  }
  else if (millis() - _time_of_last_query > _min_update_interval) {
    send_query();
  }

  return status_level;
}

float AtlasEc::get_water_electrical_conductivity() {
  return _water_electrical_conductivity;
}
float AtlasEc::get_total_dissolved_solute() {
  return _total_dissolved_solute;
}
float AtlasEc::get_salinity() {
  return _salinity;
}

void AtlasEc::set_dry_calibration() {
  Wire.beginTransmission(_i2c_address);
  Wire.print("Cal,dry");
  Wire.endTransmission();
}

void AtlasEc::set_single_calibration(double msg) {
// JU 17/02/2019: It won't work, because the syntax '%.xf' doesn't work in Arduino.
  char buf[17];
  sprintf(buf, "Cal,one,%.2f", msg);
  Wire.beginTransmission(_i2c_address);
  Wire.print(buf);
  Wire.endTransmission();
}

void AtlasEc::set_lowpoint_calibration(double msg) {
// JU 17/02/2019: It won't work, because the syntax '%.xf' doesn't work in Arduino.
  char buf[17];
  sprintf(buf, "Cal,low,%.2f", msg);
  Wire.beginTransmission(_i2c_address);
  Wire.print(buf);
  Wire.endTransmission();
}

void AtlasEc::set_highpoint_calibration(double msg) {
// JU 17/02/2019: It won't work, because the syntax '%.xf' doesn't work in Arduino.
  char buf[17];
  sprintf(buf, "Cal,high,%.2f", msg);
  Wire.beginTransmission(_i2c_address);
  Wire.print(buf);
  Wire.endTransmission();
}

void AtlasEc::send_query() {
  _time_of_last_query = millis();
/**************************************************************************************************************
** IMPORTANT COMPATIBILITY ISSUE: Firmware version 2.13 and above of the EZO circuits allow to compensate
** the measurements in a single line: "RT,<n>". Previous versions (i.e. <=2.12) has to be done on two steps:
** "T,<n>" and then "R". However, there is no easy way to set up the temperature compensation, without passing
** by the Serial interface. The software will require a more in deep modification to allow this.
***************************************************************************************************************
***   Version >= 2.13  ***
***********************/
    if(EZOversion >= 2.13){
        char buf[20];
        Trequest = "RT," + _Tcomp;
        Trequest.toCharArray(buf, 19);
        Wire.beginTransmission(_i2c_address); // read message response state
        Wire.write(buf);
        Wire.endTransmission();
/*************************************************************************************************************/
    } else {
/**************************************************************************************************************
***  Version <=2.12 (no temp compensation) ***
**********************************************/
        char buf[8];
        Trequest = "T," + _Tcomp;
        Trequest.toCharArray(buf, 7);
        Wire.beginTransmission(_i2c_address); // read message response state
        Wire.write(buf);
        Wire.endTransmission();
        delay(300);

        Wire.beginTransmission(_i2c_address); // read message response state
        Wire.write("R");
        Wire.endTransmission();
    }
/************************************************************************************************************/
  _waiting_for_response = true;
}

void AtlasEc::read_response() {
  Wire.requestFrom(_i2c_address, 20, 1);
  byte response;
  String string = "1000";
  // Ju: Added it from arduino_mega_EC_sample_code.ino to deal with all the measurements from the sensor, not only EC
  char sensor_string_array[30];
  char *EC;                                           //char pointer used in string parsing
  char *TDS;                                          //char pointer used in string parsing
  char *SAL;                                          //char pointer used in string parsing

  if (Wire.available()){
    response = Wire.read();
  }

  // Check for failure
  if (response == 255) {
    status_level = ERROR;
    status_code = CODE_NO_RESPONSE;
    status_msg = "No response";
    _waiting_for_response = false;
  }
  else if (response == 254) {
    // Request hasn't been processed yet
    return;
  }
  else if (response == 2) {
    status_level = ERROR;
    status_code = CODE_REQUEST_FAILED;
    status_msg = "Request failed";
    _waiting_for_response = false;
  }
  else if (response == 1) {
    string = Wire.readStringUntil(13);  // JU: Modified the ref character from 0 to 13 ('Carriage return')

    // JU: Taken from arduino_mega_EC_sample_code.ino:
    string.toCharArray(sensor_string_array, 30);   //convert the string to a char array
    EC = strtok(sensor_string_array, ",");               //let's pars the array at each comma
    TDS = strtok(NULL, ",");                            //let's pars the array at each comma
    SAL = strtok(NULL, ",");                            //let's pars the array at each comma
    // JU: End of extra code

    status_level = OK;
    status_code = CODE_OK;
    status_msg = "";
    _water_electrical_conductivity = atof(EC); // micro-Siemens/cm (uS/cm)
    _total_dissolved_solute = atof(TDS); //ppm
    _salinity = atof(SAL); // PSU
    _waiting_for_response = false;
  }
  else {
    status_level = ERROR;
    status_code = CODE_UNKNOWN_ERROR;
    status_msg = "Unknown error";
  }
}
