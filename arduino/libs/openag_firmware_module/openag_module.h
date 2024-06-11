#ifndef OPENAG_MODULE
#define OPENAG_MODULE

#if (ARDUINO >= 100)
 #include "Arduino.h"
#else
 #include "WProgram.h"
#endif

// JU 15/02/2019: Adding a configuration file to load some useful variables that need to be define for
//                each particular Pydroponia installation
#include <ino_conf.h>

#include <string.h>

static const uint8_t OK = 0;
static const uint8_t WARN = 1;
static const uint8_t ERROR = 2;

static const uint8_t CODE_OK = 0;

//JU 14/02/2019: Trying to branch based on the EZO circuits versions:
// Version >= 2.13 ==> Allow simple temperature compensation (i.e. "RT,<n>")
// Version <= 2.12 ==> Method to compensate for temperature is still work in progress
static const float EZOversion = EZOFMW;

class Module {
  public:
    // Public methods
    virtual ~Module() {}; // destructor
    virtual uint8_t begin() = 0;
    virtual uint8_t update() = 0;

    uint8_t status_level;
    String status_msg;
    uint8_t status_code;
};

#endif
