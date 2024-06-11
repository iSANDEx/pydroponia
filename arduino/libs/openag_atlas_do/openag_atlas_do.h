/**
 *  \file openag_atlas_do.h
 *  \brief Dissolved oxygen sensor.
 *
 * Modified by Jose Ulloa, 01/08/2018
 *  - Works in the same way as the pH and EC sensors openag code
 *  - Remove dependence on std_msgs/Float32.h and Empty.h
 *
 */
#ifndef OPENAG_ATLAS_DO_H
#define OPENAG_ATLAS_DO_H

#include "Arduino.h"
#include "openag_module.h"
#include <Wire.h>
// #include <std_msgs/Float32.h>
// #include <std_msgs/Empty.h>

/**
 * \brief Dissolved oxygen sensor.
 */
class AtlasDo : public Module {
  public:
    // Constructor
    AtlasDo(int i2c_address); // Default is 97

    // Public functions
    uint8_t begin();
    uint8_t update();

    // JU 20190206: Include temperature compensation, using the syntax RT<float Tcomp> (EZO circuits' v2.13) in
    //  the send_query function, via the update function
    void set_temp_comp(float currTemp);

    float get_water_dissolved_oxygen();
    uint8_t set_atmospheric_calibration();
    uint8_t set_zero_calibration();

  private:
    // Private variables
    float _water_dissolved_oxygen;
    uint32_t _time_of_last_query;
    bool _waiting_for_response;
    const static uint32_t _min_update_interval = 3000;
    int _i2c_address;

    // Additional variable to store answer from begin():
    int _did_send;
    // Temp compensation:
    String _Tcomp;
    String Trequest;

    // Private functions
    void send_query();
    void read_response();

    // Status codes
    static const uint8_t CODE_NO_RESPONSE = 1;
    static const uint8_t CODE_REQUEST_FAILED = 2;
    static const uint8_t CODE_UNKNOWN_ERROR = 3;
};

 #endif
