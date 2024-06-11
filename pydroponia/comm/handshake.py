#!/usr/bin/env python3
"""
handshake.py

Simple code to acknowledge the 'handshake' character sent by the Raspberry (RPi3) to the Arduino
It requires the Arduino sketch 'HandShakeSerial.ino'

Basically, the code performs the following tasks:
- Flashes the sketch HandShakeSerial.ino into the Arduino (using a subprocess)
- Opens the serial port to communication with the Arduino
- Sends (i.e. writes) a single character to be read by the Arduino
- Waits for the character to be sent back
- Compares the received character is the same as originally sent
    - If True --> Returns True
    - If False --> Issues an error message and returns False

Created by Jose L. Ulloa <jose.ulloa@isandex.com>
20/July/2018
"""

""" 
*****  Load modules  *****

Note that 'serial' is from pySerial module, not the standard that comes with the original python installation
see details at https://pyserial.readthedocs.io/en/latest/pyserial_api.html
To install using pip3 type:
pip3 install pyserial
"""
import sys
import serial
import time
import subprocess
import os

""" To allow loading modules in parallel locations """
PYDROPATH = os.getenv('PYDROPATH')
sys.path.insert(0, PYDROPATH)

import conf.pydro_config as pydro_config

"""
Global variables
"""

""" User-defined functions """


def wait4_arduino():
    """
    Just pause as a mean to wait for things to transfer or communication to start.
    Because 'real-time' is not that critical in this project, this is an adequate solution
     """
    time.sleep(2.0) # JU 27/01/19: For MEGA2560 delay of 1.0 sec is ok, but for UNO, it requires 2.0 (which is also compatible with MEGA2560)
    return


def reset_arduino(port_id):
    port_id.setDTR(0)
    time.sleep(0.5)
    port_id.flushInput()
    port_id.setDTR(0)
    time.sleep(0.5)

    return


def send_token(port_i_d, msg2_send):
    print('The built-in LED should blink and stay on')
    bytes_written = port_i_d.write(msg2_send.encode())
    if bytes_written == 0:
        print('ERROR: Cannot write any bytes')
        sent_flag = False
    else:
        print('{} bytes successfully written'.format(bytes_written))
        sent_flag = True

    return sent_flag


def rec_token(port_i_d, e_token='A'):
    # while(port_i_d.in_waiting <= 0):
    #     pass

    read_flag = True
    while read_flag:
        print(port_i_d.in_waiting)
        msg_rec = port_i_d.read()  # .decode()
        print('Received "{}" from Arduino'.format(msg_rec))
        if msg_rec == e_token:
            print('As expected.')
            rec_flag = True
        else:
            print('Expected "{}"'.format(HandShakeToken))
            print('System not yet ready')
            rec_flag = False

    return rec_flag


def run_main():

    """ Load configuration file to define relevant parameters """
    config_pars = pydro_config.config()

    hand_shake_token = config_pars['Arduino']['HandShakeToken']
    port_id = config_pars['Arduino']['PortID']
    baud_rate = config_pars['Arduino']['BaudRate']
    path_to_sketches = config_pars['Arduino']['inoLocation']
    path_to_avrdude_bin = config_pars['Arduino']['path2bin']
    write_time_out = float(config_pars['Communication']['WriteTimeOut'])  # seconds
    read_time_out = float(config_pars['Communication']['ReadTimeOut'])  # seconds
    debug_mode = int(config_pars['Misc']['debug'])

    """ Flashed the arduino with the sketch 'HandShake.ino' """
    if debug_mode:
        print('Here a subprocess should be run...')
    subprocess.run([path_to_avrdude_bin, '--upload', os.path.join(path_to_sketches, 'HandShakeSerial','HandShakeSerial.ino')])

    """ Opens the Serial communication """
    ready2_go = False
    e_time = 0
    try:
        serial_port = serial.Serial(port_id, baud_rate,
                                    timeout=read_time_out,
                                    write_timeout=write_time_out)
    except serial.serialutil.SerialException:
        bytes_written = None
        if debug_mode:
            print('ERROR: Cannot access the serial port at {}'.format(port_id))
    else:
        """ 
        As suggested at https://playground.arduino.cc/Interfacing/Python
        If the serial device takes some time to start, anything written will be lost
        So to be on the safe side, is worth waiting e.g. 1 sec:
        """
        wait4_arduino()
        bytes_written = serial_port.write(hand_shake_token.encode())
        start_time = time.time()
        if bytes_written:
            while (not ready2_go) and (e_time < read_time_out):
                serial_port.flushInput()
                msg_rec = serial_port.read().decode()
                if debug_mode:
                    print('Char received: {} - '.format(msg_rec))
                ready2_go = (msg_rec == hand_shake_token)
                e_time = time.time() - start_time

    if ready2_go:
        if debug_mode:
            print('Serial connection successfully setup!')
    elif not bytes_written:
        if debug_mode:
            print('ERROR: Could not send anything to Arduino')
    elif e_time >= read_time_out:
        if debug_mode:
            print('ERROR: Have not received anything from Arduino in {0:1f}s'.format(e_time))
    else:
        if debug_mode:
            print('The system should never reach this point')
        sys.exit('ERROR: There is an unknown problem with the execution')

    return ready2_go


def handshake():
    return run_main()


if __name__ == '__main__':
    """
    Doesn't require any input argument. But still can be run as a part of another function, stand-alone module 
    or from the command line
    """

    run_main()
