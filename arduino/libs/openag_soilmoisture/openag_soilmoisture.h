/**
 *  \file openag_soilmoisture.h
 *  \brief Sensor module for soil moisture.
 */
#ifndef SMOIST_H
#define SMOIST_H

#if ARDUINO >= 100
 #include <Arduino.h>
#else
 #include "WProgram.h"
#endif

//#include <OneWire.h>
//#include <DallasTemperature.h>
#include <openag_module.h>

/**
 * \brief Sensor module for soil moisture
 */
class SMoist : public Module {
  public:
    SMoist(int sensor_pin);
    uint8_t begin();
    uint8_t update();
    float get_soilmoisture();

  private:
    bool _send_soilmoisture;
    int _sensor_pin;
//    For each sensor, these values should be found by calibration
    const int _air_value = 830;   //you need to replace this value with Value_1
    const int _water_value = 434;  //you need to replace this value with Value_2
//
    int _soil_moisture_value = 0;
    int _soil_moisture_percent = 0;
    int _soilmoisture = 0;

    uint32_t _time_of_last_query;
//    bool _waiting_for_conversion;
    const static uint32_t _min_update_interval = 2000;

    // Status codes
    static const uint8_t CODE_COULDNT_FIND_ADDRESS = 1;
    static const uint8_t CODE_NO_RESPONSE = 2;
};

#endif
