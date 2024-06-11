/**
 *  \file openag_soilmoisture.cpp
 *  \brief Sensor module for soil moisture.
 */
#include "openag_soilmoisture.h"

SMoist::SMoist(int sensor_pin) {
  _sensor_pin = sensor_pin;
}

uint8_t SMoist::begin() {
  status_level = OK;
  status_code = CODE_OK;
  status_msg = "";
  _time_of_last_query = 0;
  get_soilmoisture();
  return status_level;
}

uint8_t SMoist::update() {
  if (millis() - _time_of_last_query > _min_update_interval) {
      get_soilmoisture();
      _time_of_last_query = millis();
  }
  return status_code;
}

float SMoist::get_soilmoisture() {

    _soil_moisture_value = analogRead(_sensor_pin);  //put Sensor insert into soil
    _soil_moisture_percent = map(_soil_moisture_value, _air_value, _water_value, 0, 100);

    if(_soil_moisture_percent >= 100) {
      _soilmoisture = 100;
    } else if(_soil_moisture_percent <=0) {
      _soilmoisture = 100;
    } else if(_soil_moisture_percent >0 && _soil_moisture_percent < 100) {
      _soilmoisture = _soil_moisture_percent;
    }

  return _soilmoisture;
}
