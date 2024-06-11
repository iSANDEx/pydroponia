/**
 *  \file openag_atlas_do.cpp
 *  \brief Dissolved oxygen sensor.
 *
 * Modified by Jose Ulloa, 01/08/2018
 *  - Works in the same way as the pH and EC sensors openag code
 *  - Remove dependence on std_msgs/Float32.h and Empty.h
 *
 */
#include "openag_atlas_do.h"

AtlasDo::AtlasDo(int i2c_address) {
  status_level = OK;
  status_code = CODE_OK;
  status_msg = "WDO";
  _time_of_last_query = 0;
  _waiting_for_response = false;
  _i2c_address = i2c_address;
}

uint8_t AtlasDo::begin() {
  Wire.begin();
  Wire.setTimeout(40);
  return status_level;
}

void AtlasDo::set_temp_comp(float currTemp) {
/************************************************************************************************/
/** IMPORTANT COMPATIBILITY ISSUE: Firmware version 2.13 and above of the EZO circuits allow to
     compensate the measurements in a single line: "RT,<n>". Previous versions (i.e. <=2.12) will
     have to be done in two steps: "T,<n>" and then "R" **/
    _Tcomp = String(currTemp,2);
}

uint8_t AtlasDo::update() {
  if (_waiting_for_response) {
    if (millis() - _time_of_last_query > 1400) { // Processing delays: 600ms to read + 300ms Temp Comp = 900ms + 50%
      read_response();
    }
  }
  else if (millis() - _time_of_last_query > _min_update_interval) {
    send_query();
  }
  return status_level;
}

float AtlasDo::get_water_dissolved_oxygen() {
  return _water_dissolved_oxygen;
}

uint8_t AtlasDo::set_atmospheric_calibration() {
  Wire.beginTransmission(_i2c_address);
  Wire.print("Cal");
  Wire.endTransmission();
  return status_level;
}

uint8_t AtlasDo::set_zero_calibration() {
  Wire.beginTransmission(_i2c_address);
  Wire.print("Cal,0");
  Wire.endTransmission();
  return status_level;
}

void AtlasDo::send_query() {
  _time_of_last_query = millis();
/**************************************************************************************************************
** IMPORTANT COMPATIBILITY ISSUE: Firmware version 2.13 and above of the EZO circuits allow to compensate
** the measurements in a single line: "RT,<n>". Previous versions (i.e. <=2.12) has to be done on two steps:
** "T,<n>" and then "R". However, there is no easy way to set up the temperature compensation, without passing
** by the Serial interface. The software will require a more in deep modification to allow this.
***************************************************************************************************************
***   Version 2.13  ***
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
        Wire.endTransmission(false);
        delay(300);

        Wire.beginTransmission(_i2c_address); // read message response state
        Wire.write("R");
        Wire.endTransmission();
    }
/************************************************************************************************************/
  _waiting_for_response = true;
}

void AtlasDo::read_response() {
  Wire.requestFrom(_i2c_address, 20, 1);
  byte response;
  if(Wire.available()){
    response = Wire.read(); // increment buffer by a byte
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
  }
  else if (response == 2) {
    status_level = ERROR;
    status_code = CODE_REQUEST_FAILED;
    status_msg = "Request failed";
    _waiting_for_response = false;
  }
  else if (response == 1) {
    String string = Wire.readStringUntil(13); // JU: Modified the ref character from 0 to 13 ('Carriage return')
    status_level = OK;
    status_code = CODE_OK;
    status_msg = "";
    _water_dissolved_oxygen = string.toFloat();
    _waiting_for_response = false;
  }
  else {
    status_level = ERROR;
    status_code = CODE_UNKNOWN_ERROR;
    status_msg = "Unknown error";
  }
}
