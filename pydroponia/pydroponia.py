#!/usr/bin/env python3
"""
pydroponia.py

This is the main module to read data from the Arduino and store them in a CSV file


Created by Jose L. Ulloa <jose.ulloa@isandex.com>
20/July/2018
"""

""" Load modules"""

import os
import sys
import serial
import numpy as np
import time
import subprocess
import datetime
import csv
import logging

""" To allow loading modules in parallel locations """
PYDROPATH = os.getenv('PYDROPATH')
sys.path.insert(0, PYDROPATH)

from conf import pydro_config
from conf import config_db as db
from comm import *

# JU 09/11/2018: For now, I hard-coded the option to run without the Arduino attached (i.e. for debugging purposes)
#  but on the next release, it must be included as a configurable parameter
# JU 06/03/2019: Sorted 'attached_arduino' parameter -> now is part of the config file
# attached_arduino = True

""" User-defined functions """


def write_data(new_row, path2csv):
    """

    :param new_row:
    :param path2csv:
    :return:
    """
    # JU 06/03/2019: Added time and date fields at the moment of read from Arduino, rather than when writing in the
    # CSV and dB. So the following two lines are now redundant.
    # data_rec_at = datetime.datetime.now()
    # today_date = data_rec_at.strftime('%Y/%m/%d,%H:%M:%S')
    with open(path2csv, 'a') as fid:
        writer = csv.writer(fid, delimiter=',')
        # writer.writerow(today_date.split(',') + new_row)
        # JU 06/03/2019: End
        writer.writerow(new_row)


def reading_loop(always_true, serial_port, system_id, r_time_out, w_time_out,
                 attached_arduino, srow, erow, path2csv, path2db, table_db,
                 logger, dbg_mode=0):
    """
    :param system_id:
    :param srow:
    :param erow:
    :param path2csv:
    :param path2db:
    :param table_db:
    :param dbg_mode:
    :param serial_port:
    :param always_true:
    :return:
    """

    row_counter = 1
    row_avg = 0
    if attached_arduino:
        ndummy = 5 # Number of 'dummy' acquisitions before record them
    else:
        ndummy = 0 # When not recording real data, there is no need to skip samples
        #JU 10/11/18:  Creates here a base list to be updated with random values of a similar order of magnitude of
        # that from each sensor. Order of the sensors was taken from 'pydro_config.py':
        # 'Date,Time,wTemp,wDO,wEC,wTDS,wSAL,wpH'
        # wTEMP: 22-26deg --> 24 + 2.0*2.0*(rand()-0.5)
        # wDO: 8.00-10.00 --> 9 + 1.0*2.0*(rand()-0.5)
        # wEC: 22-26deg --> 24 + 2.0*(rand()-0.5)
        # wTD: 22-26deg --> 24 + 2.0*(rand()-0.5)
        # wSAL: 22-26deg --> 24 + 2.0*(rand()-0.5)
        # wpH: 4-10 --> 7 + 3.0*2.0*(rand()-0.5)
        # atemp: 22-26deg --> 24 + 2.0*2.0*(rand()-0.5)
        # ahum: 10-90 --> 50 + 40.0*2.0*(rand()-0.5)
        base_expected_value = {'wtemp':[24.0, 2.0],
                               'wdo':  [9.0,  1.0],
                               'wec':  [10.0, 2.0],
                               'wtds': [10.0, 2.0],
                               'wsal': [10.0, 2.0],
                               'wph':  [7.0,  2.0],
                               'atemp': [24.0, 2.0],
                               'ahum': [50.0, 40.0],
                               'smoist': [10.0, 70.0]}

    readingSince = datetime.datetime.now()
    lastRead     = readingSince
    logger.info('Writing interval is {}[sec]'.format(w_time_out))
    logger.info('Reading sensors since {}'.format(datetime.datetime.strftime(readingSince,
                                                                             '%Y-%m-%d at %H:%M:%S')))
    # JU 04/04/2021:  In order to control the pump via the soil moisture
    # sensor, I have to initialise the row_4db variable
    row_4_db = None
    # JU 03/04/2021: To control water stirring pump - to stir the water
    # every 2 hours (7.200secs)
    stirring_period = 7200 #seconds
    spump_msg = 'SPUMP\n'
    stir_elp_time = 0
    start_stirring_time = time.time()
    
    # JU 03/04/2021: To control peristaltic watering pump - to water the
    # plants every day (86.400secs)
    watering_period = 86400 #seconds
    wpump_msg = 'WPUMP\n'
    water_elp_time = 0
    start_watering_time = time.time()
    watering_gap = 60 # seconds --> Only every <watering_gap>seconds will
    # check whether to water or not, based on the moisture value
    wpumpON = False # To initialise the watering in the first cycle after a
    # reboot
    soil_moisture_lb = 80 # minimum value when to start watering

    while always_true:
        """ Requests data to Arduino """
        if attached_arduino:
            bytes_written = serial_port.write('\n'.encode())
        else:
            bytes_written = 1
        if dbg_mode:
            logger.debug(''.join(['*'] * 100))
            logger.debug('{} Bytes written OK. Waiting for data...'.format(bytes_written))
        start_time = time.time()
        elp_time = 0
        # JU 09/11/2018: Branch to allow operation without Arduino attached:
        # JU 01/12/2018: Amended bug used a fixed variable (in_waiting) instead the updated serial_port.in_waiting output
        if attached_arduino:
            in_waiting = serial_port.in_waiting
        else:
            in_waiting = 1
        # ------

        # JU 01/12/2018: Amended bug used a fixed variable (in_waiting) instead the updated serial_port.in_waiting output
        #   This is still a bug, I need to device a better solution to allow simpler switch when simulating without an
        #   Arduino attached
        while (serial_port.in_waiting == 0) & (elp_time < r_time_out):
            elp_time = time.time() - start_time
        if serial_port.in_waiting == 0:
            logger.error('ERROR: have not received anything for {0:.1f}s'.format(elp_time))
            break
        else:
            if dbg_mode:
                logger.debug('{} bytes awaiting...'.format(serial_port.in_waiting))
            """ Only now starts reading data... 
            Read the first byte which says whether the sensors are ok or not:
            """
            # JU 09/11/2018: Branch to allow operation without Arduino attached:
            if attached_arduino:
                read_status = serial_port.read(1).decode()
                logger.debug('Status is: {}'.format(read_status))
                all_sensors_status = int(read_status)
            else:
                all_sensors_status = 0

            if dbg_mode:
                logger.debug('First Byte: {}'.format(all_sensors_status))
            if all_sensors_status:  # (0 ==> OK, 1 | 2 ==> ERROR)
                """ Something is wrong. Read until the LF to have the whole error message """
                err_msg = '{0:d}{1:s}'.format(all_sensors_status, serial_port.read_until(b'\n').decode())
                logger.error('ERROR: Code {}'.format(err_msg))
                break
            else:
                """ Good to go! """
                # JU 09/11/2018: Branch to allow operation without Arduino attached:
                if attached_arduino:
                    str_rec = ''
                else:
                    str_rec = srow

                while not str_rec == srow:
                    str_rec = serial_port.read().decode()
                    if dbg_mode:
                        logger.debug('Stream of bytes: {}'.format(str_rec))
                new_row = str_rec
                # JU 09/11/2018: Branch to allow operation without Arduino attached:
                if attached_arduino:
                    new_row += serial_port.read_until(erow.encode()).decode()
                    serial_port.reset_input_buffer()
                    # JU 03/04/2021: Sends a message to switch on the
                    # stirring water pump:
                    if stir_elp_time < stirring_period:
                        stir_elp_time = time.time() - start_stirring_time
                    else:
                        spumpON = serial_port.write(spump_msg.encode())
                        if spumpON:
                            logger.info('{})Switching on the stirring water '
                                        'pump'.format(datetime.datetime.now().strftime('%Y-%m-%d '
                                                                                       '%H:%M:%S')))
                            start_stirring_time = time.time()
                            stir_elp_time = 0
                    # JU 03/04/2021: Sends a message to switch on the
                    # peristaltic watering pump:
                    # if water_elp_time < watering_period:
                    #     water_elp_time = time.time() - start_watering_time
                    # else:
                    #     wpumpON = serial_port.write(wpump_msg.encode())
                    #     if wpumpON:
                    #         logger.info('{} switching on the water pump'.format(
                    #             datetime.datetime.now().strftime(
                    #                 '%Y-%m-%d %H:%M:%S')))
                    #         start_watering_time = time.time()
                    #         water_elp_time = 0
                    # JU : But, after implementing the soil moisture sensor,
                    # replace this block by the actual (accumulated) reading of
                    # the moisture sensor:
                    if row_4_db is not None:
                        if (water_elp_time < watering_gap) and wpumpON:
                            water_elp_time = time.time() - start_watering_time
                        elif row_4_db[-2] <= soil_moisture_lb:
                            logger.info('Warning! soil is getting dry...')
                            logger.info('Soil moisture is {}'.format(row_4_db[-2]))
                            wpumpON = serial_port.write(wpump_msg.encode())
                            if wpumpON:
                                logger.info('{} switching on the water pump'.format(
                                    datetime.datetime.now().strftime(
                                        '%Y-%m-%d %H:%M:%S')))
                                start_watering_time = time.time()
                                water_elp_time = 0
                        else:
                            pass
                else:
                    # JU 8/11/18: Mimic the actual sensor reads by creating random values for each sensor
                    #            Just to make it more 'realistic', use similar orders of magnitudes for each
                    #            sensor. Order taken from 'pydro_config.py':
                    #            'Date,Time,wTemp,wDO,wEC,wTDS,wSAL,wpH'
                    #           wTEMP: 22-26deg --> 24 + 2.0*2.0*(rand()-0.5)
                    #           xDO: 8.00-10.00 --> 9 + 1.0*2.0*(rand()-0.5)
                    #           wEC: 22-26deg --> 24 + 2.0*(rand()-0.5)
                    #           wTD: 22-26deg --> 24 + 2.0*(rand()-0.5)
                    #           wSAL: 22-26deg --> 24 + 2.0*(rand()-0.5)
                    #           wpH: 4-10 --> 7 + 3.0*2.0*(rand()-0.5)
                    for ind_sensor, val_range in base_expected_value.items():
                        new_row += '{0:.3f},'.format(val_range[0] + val_range[1]*2.0*(np.random.random()-0.5))
                    new_row = new_row[:-1] + '}' # Replaces the last ',' by a closing brace '}'
                if dbg_mode:
                    logger.debug('{} bytes in the buffer'.format(serial_port.in_waiting))
                    if np.mod(row_counter, 1) == 0:
                        logger.debug('Row#{0:d}:\t{1:s}'.format(row_counter, new_row))
                row_as_list = new_row.strip('{}').split(',')
                # row_4_db = ['"{}"'.format(system_id)] + [float(xi) for xi in row_as_list]
                # JU 17/10/2018: To be consistent with both databases, re-order the string to populate the table in the
                # same order as defined by the external database:
                #  [fecha,Hora,wtemp,wdo,wec,wtds,wsal,wph,id_sensor]
                # Note that 'fecha' and 'hora' are not defined here, but are the times when the data is written to the
                # database. Which may need to change in future versions
                # JU 06/03/2019: Refactoring this bit of code to record the time and date more accurately (but still not
                #  100% correct) as when the reading happens here, rather than when is written into the database.
                #  Although strictly speaking, it should be sent from the Arduino itself when the actual reading
                #  happened. However, that'll require to add a clock into the Arduino, something that is not yet worth
                #  the effort. For now, do it in here:
                this_time = datetime.datetime.now()
                deltaTime = (this_time - lastRead).total_seconds() # time (in secs) between writes into the dB
                fecha = this_time.strftime('%Y/%m/%d')
                hora = this_time.strftime('%H:%M:%S')
                # JU 06/03/2019: End

                # row_4_db = [float(xi) for xi in row_as_list] + ['"{}"'.format(system_id)]
                # JU 17/10/2018: system_id must be numeric, to be consistent with HydroponicDB.sql
                # JU 06/03/2018: Added Fecha and Hora to ROW_4_DB:
                row_4_db = [fecha, hora] + [float(xi) for xi in row_as_list] + [system_id]
                if row_counter == 1:
                    stacked_rows = row_4_db.copy()
                    stacked_rows[2:-1] = [0.0 for xij in stacked_rows[2:-1]]
                # JU 06/03/2019: End
                # JU 17/10/2018: End
                if row_counter > ndummy:
                    """ Skips the first <ndummy> samples, so it gives time to stabilise everything, 
                    specially the sensors."""
                    # JU 06/03/2019: Together with the 'dummy' acquisitions, we now check whether the interval time to
                    # writing into the dB is less than or equal to the time since the last writing. This time is
                    # different to the sampling time used by the Arduino, as this is the minimum required (to keep
                    # consistency with the temperature compensation)
                    if deltaTime >= w_time_out: # Only writes if time since last write was more than w_time_out
                        # JU 07/03/2019: Modify the lists wrote into the CSV and dB to use the average over the
                        # accumulated period without writing data (given by w_time_out)
                        # JU 07/03/2019: Remember to add the last sample taken (row_4_db), because the main source of
                        # data at this stage is stacked_rows, the last measurement is only an additional read. Also,
                        # remember to consider that last sample into the N (to divide the accumulated measurements and
                        # take the average. Actually, in the future the stats can easily be changed by the median, mode,
                        # min, max or even something more complex.
                        row_4_db[2:-1] = [(row_4_db[ij + 2] + xij)/(row_avg + 1) for ij, xij in enumerate(stacked_rows[2:-1])]
                        write_data(row_4_db[:-1], path2csv)
                        db.pop_table_db(path2db, table_db, row_4_db)
                        if dbg_mode:
                            logger.debug('Data writen:\t[{}]'.format(row_4_db[2:-1]))
                        # JU 07/03/2019: Restart the time of last read and the accumulator stacked_rows:
                        lastRead = datetime.datetime.now()
                        stacked_rows[2:-1] = [0.0 for xij in stacked_rows[2:-1]]
                        row_avg = 0
                        # JU 07/03/2019: End
                        if dbg_mode:
                            logger.debug('Average from the last {}[sec] written into the dB. Wait for next cycle'.format(np.round(w_time_out)))
                    else:
                        # JU 06/03/2019: Time since last writing was less than the write sampling interval
                        if dbg_mode:
                            logger.debug('Time since last write was {} secs. Adding this sample to the accumulator'.format(deltaTime))
                        stacked_rows[2:-1] = [stacked_rows[ij + 2] + xij for ij, xij in enumerate(row_4_db[2:-1])]
                        row_avg += 1
                else:
                    # JU 09/11/2018: The number of samples to skip is now a variable that can be easily changed
                    #  (ideal for debugging)
                    if dbg_mode:
                        logger.debug('Skipping the first {0:d} samples ({1:d} out of {0:d})'.format(ndummy, row_counter))
                        logger.debug(''.join(['*'] * 100))
                # JU 09/11/2018: Remember Arduino samples every 5sec, so I have to add the same pause when simulating
                #               an acquisition
                if not attached_arduino:
                    time.sleep(5)
                row_counter += 1
    print('Bye!')


def start_data_acq():
    run_main()


def run_main():

    """ Load configuration file to define relevant parameters """
    config_pars = pydro_config.config()

    port_id = config_pars['Arduino']['PortID']
    baud_rate = config_pars['Arduino']['BaudRate']
    start_row = config_pars['Arduino']['StartRow']
    end_row = config_pars['Arduino']['EndRow']
    path_to_sketches = config_pars['Arduino']['inoLocation']
    path_to_avrdude_bin = config_pars['Arduino']['path2bin']

    write_time_out = float(config_pars['Communication']['WriteTimeOut'])  # seconds
    read_time_out = float(config_pars['Communication']['ReadTimeOut'])  # seconds
    # JU 06/03/2019: attached_arduino is now a configurable parameter
    attached_arduino = bool(config_pars['Communication']['attached_arduino']) # Whether or not an arduino controller is attached

    db_loc = config_pars['Locations']['dbLocation']
    csv_loc = config_pars['Locations']['csvLocation']

    db_name = config_pars['System']['dbName']
    db_table = config_pars['System']['dbTable']
    db_fields = config_pars['System']['dbFields']
    db_types = config_pars['System']['dbTypes']

    csv_cols_name = config_pars['System']['csvHdr'].split(',')

    sys_id = config_pars['System']['systemID']

    debug_mode = int(config_pars['Misc']['debug'])

    """ Constant parameters """
    today_date = datetime.datetime.now()
    csv_filename = 'Data_System_{}_Created_{}'.format(sys_id, today_date.strftime('%Y%m%d_%H%M%S'))
    path_to_csv = os.path.join(csv_loc, '{}.csv'.format(csv_filename))

    path_to_db = os.path.join(db_loc, db_name)

    """ Logging info to keep track of the 'print' statements previously used """
    path_to_logfile = os.path.join(os.getenv('HOME'),'.pydroponia','pydro.log')
    if debug_mode:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    # create a file handler
    handler = logging.FileHandler(path_to_logfile)
    handler.setLevel(logging.INFO)
    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(handler)

    """ Runs the handshake to ensure there is communication between the the Arduino and the Raspberry Pi"""
    logger.info('Runs the handshake to ensure there is comm btwn Arduino and RPi. Please wait ...')
    # JU 09/11/2018: Have to add flag for when not attaching an Arduino microcontroller:
    if attached_arduino:
        ready_to_go = handshake()
    else:
        ready_to_go = True

    if ready_to_go:
        """ Ok to proceed"""
        if debug_mode:
            logger.debug('Run the subprocess to flash the Arduino with the sensor read sketch...')
        # JU 09/11/2018: Have to add flag for when attaching an Arduino microcontroller:
        if attached_arduino:
            subprocess.run([path_to_avrdude_bin, '--upload', os.path.join(path_to_sketches, 'Sensors', 'Sensors.ino')])

        logger.info('Arduino is now taking data forever...')

        """ Creates data file """
        with open(path_to_csv, 'w') as fid:
            writer = csv.writer(fid)
            writer.writerow(csv_cols_name)

        """ Opens the serial communication """
        try:
            # JU 09/11/2018: Have to add flag for when not attaching an Arduino microcontroller:
            if attached_arduino:
                serial_port = serial.Serial(port_id, baud_rate, timeout=read_time_out)
            else:
                serial_port = True
        except serial.serialutil.SerialException:
            sys.exit('ERROR: Cannot open communication through port {}'.format(port_id))
        else:
            time.sleep(1)
            # JU 09/11/2018: Have to add flag for when not attaching an Arduino microcontroller:
            if attached_arduino:
                reset_arduino(serial_port)

            reading_loop(ready_to_go, serial_port, sys_id, read_time_out, write_time_out,
                         attached_arduino, start_row, end_row, path_to_csv, path_to_db,
                         db_table, logger, dbg_mode=debug_mode)
    else:
        if debug_mode:
            logger.debug('The system is not yet ready. Bye!!')


if __name__ == '__main__':
    """
    Doesn't require any input argument. But still can be run as a part of another function, stand-alone module
    or from the command line
    """

    run_main()
