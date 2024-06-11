/**
 *  \file sensor_dht11.h
 *  \brief Sensor module for air temperature and humidity.
 */

// Library based off: DHT 22/21 library from Seeed Studio and DHT library from Adafruit
// Libraries found at: https://github.com/adafruit/DHT-sensor-library/ and https://github.com/Seeed-Studio/Grove_Temperature_And_Humidity_Sensor
// Component found at: https://www.adafruit.com/product/386
// Modified by: Pablo Aguado, based on Jack Rye's library for DHT22  

#ifndef OPENAG_DHT11_H
#define OPENAG_DHT11_H

#if ARDUINO >= 100
 #include "Arduino.h"
#else
 #include "WProgram.h"
#endif

// 8 MHz(ish) AVR ---------------------------------------------------------
#if (F_CPU >= 7400000UL) && (F_CPU <= 9500000UL)
#define COUNT 3
// 16 MHz(ish) AVR --------------------------------------------------------
#elif (F_CPU >= 15400000UL) && (F_CPU <= 19000000L)
#define COUNT 6
#else
#error "CPU SPEED NOT SUPPORTED"
#endif

// how many timing transitions we need to keep track of. 2 * number bits + extra
#define MAXTIMINGS 85

#include <openag_module.h>
#include <dht.h>
//#include <std_msgs/Float32.h>

/**
 *  \brief Sensor module for air temperature and humidity.
 */
class Dht11 : public Module {
  public:
    // Public Functions
    Dht11(int pin);
//    JU 01/12/2018: Added from openag_ds18b20.h
    uint8_t begin();
    uint8_t update();
    float get_air_temperature();
    float get_air_humidity();
//    JU 01/12/2018: End Added from openag_ds18b20.h

//    void begin();
//    void update();
//    bool get_air_temperature(std_msgs::Float32 &msg);
//    bool get_air_humidity(std_msgs::Float32 &msg);

  private:
    // Private Functions
    void getData();
    bool readSensor();

//    JU 01/12/2018: Added from openag_atlas_ec.h
//    void send_query();
//    void read_response();
//    JU 01/12/2018: End Added from openag_atlas_ec.h

    // Private Variables
    int _pin;
    dht _Dht11;
    int8_t chk;
    float _air_temperature;
//    bool _send_air_temperature;
    float _air_humidity;
//    bool _send_air_humidity;
    uint32_t _time_of_last_reading;
//    const uint32_t _min_update_interval = 2000;
//    JU 01/12/2018: Copied the types from openag_atlas_ec.h
    const static uint32_t _min_update_interval = 2000;
    bool _waiting_for_response;
//    JU 01/12/2018: End Copied the types from openag_atlas_ec.h

//    JU 01/12/2018: Added from openag_atlas_ec.h
    // Status codes
    static const uint8_t CODE_NO_RESPONSE = 1;
    static const uint8_t CODE_REQUEST_FAILED = 2;
    static const uint8_t CODE_UNKNOWN_ERROR = 3;
//    JU 01/12/2018: End Added from openag_atlas_ec.h

//    JU 01/12/2018: Extra const from openag_ds18b20.h
    static const uint8_t CODE_COULDNT_FIND_ADDRESS = 1;
//    JU 01/12/2018: End Extra const from openag_ds18b20.h

    uint8_t _data[6];
    uint8_t _count;
    uint32_t _last_read_time;
    bool _first_reading;
};

#endif // OPENAG_DHT11_H

