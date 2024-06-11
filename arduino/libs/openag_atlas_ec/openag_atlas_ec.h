/**
 *  \file openag_atlas_ec.h
 *  \brief Electrical conductivity sensor.
 */
#ifndef OPENAG_ATLAS_EC_H
#define OPENAG_ATLAS_EC_H

#include "Arduino.h"
#include <openag_module.h>
#include <Wire.h>

/**
 * \brief Electrical conductivity sensor.
 */
class AtlasEc : public Module {
  public:
    // Constructor
    AtlasEc(int i2c_address);

    // Public functions
    uint8_t begin();
    uint8_t update();
    // JU 20190206: Include temperature compensation, using the syntax RT<float Tcomp> (EZO circuits' v2.13) in
    //  the send_query function, via the update function
    void set_temp_comp(float currTemp);

    float  get_water_electrical_conductivity();
    float  get_total_dissolved_solute();
    float  get_salinity();
    void set_dry_calibration();
    void set_single_calibration(double msg);
    void set_lowpoint_calibration(double msg);
    void set_highpoint_calibration(double msg);

  private:
    // Private variables
    float _water_electrical_conductivity;
    float _total_dissolved_solute;
    float _salinity;
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
