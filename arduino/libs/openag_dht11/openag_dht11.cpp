/**
 *  \file sensor_dht11.cpp
 *  \brief Sensor module for air temperature and humidity.
 *  \details See sensor_dht11.h for details.
 */
#include "openag_dht11.h"

Dht11::Dht11(int pin) {
  _pin = pin;
//  status_level = OK;
//  status_msg = "";

//  JU 01/12/2018: Added from openag_atlas_ec.cpp
  status_level = OK;
  status_code = CODE_OK;
  status_msg = "ATEMP";
  _time_of_last_reading = 0;
  _waiting_for_response = false;
//  JU 01/12/2018: End Added from openag_atlas_ec.cpp
}

// JU 01/12/2018: Modified output type to match header's definition
uint8_t Dht11::begin(){
//}
//void Dht11::begin() {
// JU 01/12/2018: Modified function body to match openag template (e.g. openag_ds18b20.cpp):
//  _sensors.begin(); JU 01/12/2018 It doesn't go here, because this function is from DallasTemperature.h
  status_level = OK;
  status_code = CODE_OK;
  status_msg = "ATEMP";
//  _waiting_for_conversion = false;
  _time_of_last_reading = 0;
//  if (!_sensors.getAddress(_address, 0)) {
//    status_level = ERROR;
//    status_code = CODE_COULDNT_FIND_ADDRESS;
//    status_msg = "Unable to find address for sensor";
//  }
  return status_level;
//  JU 01/12/2018: End Modified function body...

//  pinMode(_pin, INPUT);
//  digitalWrite(_pin, HIGH);
//  _count = COUNT;
//  _first_reading = true;
//  _time_of_last_reading = 0;
}
// JU 01/12/2018: Modified output type to match header's definition
uint8_t Dht11::update() {
//}
//void Dht11::update() {
// JU 01/12/2018: Modified function body to match openag template (e.g. openag_ds18b20.cpp):
  if (millis() - _time_of_last_reading > _min_update_interval) {
    getData();
    _time_of_last_reading = millis();
  }
}

// JU 01/12/2018: These two functions (get_air_temperature and get_air_humidity are modified to match openag templates
//                  e.g. openag_atlas_ec.cpp
//bool Dht11::get_air_temperature(std_msgs::Float32 &msg) {
//  msg.data = _air_temperature;
//  bool res = _send_air_temperature;
//  _send_air_temperature = false;
//  return res;
//}
float Dht11::get_air_temperature() {
  return _air_temperature;
}

//bool Dht11::get_air_humidity(std_msgs::Float32 &msg) {
//  msg.data = _air_humidity;
//  bool res = _send_air_humidity;
//  _send_air_humidity = false;
//  return res;
//}
float Dht11::get_air_humidity() {
  return _air_humidity;
}

void Dht11::getData(void) {
  if (readSensor()) {
    if (status_level != OK) {
      status_level = OK;
      status_msg = "";
    }

    _air_humidity = _Dht11.humidity; // _data[0];
    _air_temperature = _Dht11.temperature; // _data[2];

//    _send_air_temperature = true;
//    _send_air_humidity = true;
  }
  else {
    status_level = ERROR;
    //status_msg = "Failed to read from sensor";
    // Failed to read from sensor
    status_msg = "32";
  }
}

//Let's try using the 'official' DHT library (https://playground.arduino.cc/Main/DHTLib)
bool Dht11::readSensor() {
    chk = _Dht11.read11(_pin);
    switch (chk)
      {
        case DHTLIB_OK:
//		    Serial.print("OK,\t");
    		return true;
        case DHTLIB_ERROR_CHECKSUM:
//		    Serial.print("Checksum error,\t");
    		return false;
        case DHTLIB_ERROR_TIMEOUT:
//		    Serial.print("Time out error,\t");
    		return false;
        default:
//		    Serial.print("Unknown error,\t");
    		return false;
      }
 }

//bool Dht11::readSensor() {
//  uint8_t last_state = HIGH;
//  uint8_t counter = 0;
//  uint8_t j = 0, i;
//  unsigned long current_time;
//
//  digitalWrite(_pin, HIGH);
//  delay(2); // old delay time was 250 // Why this? Copied from dht22 library...
//
//  current_time = millis();
//  if (current_time < _last_read_time) {
//    // ie there was a rollover
//    _last_read_time = 0;
//  }
//  if (!_first_reading && ((current_time - _last_read_time) < 2000)) {
//    return true; // return last correct measurement
//  }
//  _first_reading = false;
//  _last_read_time = millis();
//
//  _data[0] = _data[1] = _data[2] = _data[3] = _data[4] = 0;
//
//  // now pull it low for ~20 milliseconds
//  pinMode(_pin, OUTPUT);
//  digitalWrite(_pin, LOW);
//  delay(20);
//  digitalWrite(_pin, HIGH);
//  delayMicroseconds(40);
//  pinMode(_pin, INPUT);
//
//  // read in timings
//  for ( i=0; i< MAXTIMINGS; i++) {
//    counter = 0;
//    while (digitalRead(_pin) == last_state) {
//      counter++;
//      delayMicroseconds(1);
//      if (counter == 255) {
//        break;
//      }
//    }
//    last_state = digitalRead(_pin);
//
//    if (counter == 255) break;
//
//    // ignore first 3 transitions
//    if ((i >= 4) && (i%2 == 0)) {
//      // shove each bit into the storage bytes
//      _data[j/8] <<= 1;
//      if (counter > _count)
//        _data[j/8] |= 1;
//      j++;
//    }
//  }
//
//  // check we read 40 bits and that the checksum matches
//  if ((j >= 40) &&
//      (_data[4] == ((_data[0] + _data[1] + _data[2] + _data[3]) & 0xFF)) ) {
//    return true;
//  }
//  return false;
//}
