#!/usr/bin/env python3
"""
pydro_config.py

This files creates a configuration file for each installation.
The default location for the CONF.INFO file is
${HOME}/.pydroponia/conf.info
The file CONF.INFO is a standard configuration file created by
the module CONFIGPARSER (see https://docs.python.org/3/library/configparser.html)
The user can provide an alternative configuration file living at the same location.
The content of this file will be merged to a default CONF.INFO file, which is the one
used by the whole system
This script performs the following tasks:
Look for ${HOME}/.pydroponia folder
if FALSE ==> Creates the folder '.pydroponia' in ${HOME}
--> if FALSE (i.e. cannot create the folder) ==> Halts the execution and issues an error message
--> if TRUE ==> Creates a default CONF.INFO configuration file within .pydroponia
if TRUE ==> Looks for USER-DEFINED.INFO (if empty, it uses the default 'co
--> if FALSE ==> Looks for a default ${HOME}/.pydroponia/conf.info file
--> --> If FALSE (i.e. CONF.INFO doesn't exist) --> Creates a default CONF.INFO file
--> --> If TRUE ==> Loads it and merge the content with the default configuration parameters (the system will use
CONF.INFO, despite any other configuration files given as an input to this script).

Created by Jose L. Ulloa <jose.ulloa@isandex.com>
20/July/2018
"""
import os
import configparser
import argparse
import sys

""" 
Global variables used by default. They are overwritten if a configuration file is provided
"""
PACKNAME = 'pydroponia'
HOMEPATH = os.getenv('HOME')
PYDROPATH = os.getenv('PYDROPATH')
CONFPATH = os.path.join(HOMEPATH, '.{}'.format(PACKNAME))
CONFIGNAME = 'conf.info'
ARDUINOPATH = os.path.join(os.getenv('BIOAGROLOGPATH'), 'arduino', 'sketches')
ARDUINOBIN = os.path.join(os.getenv('AVRDUDE'))
DEBUG = 0 # JU 12/02/2019: Just to make the development stage simpler, set the (initial) DEBUG mode as TRUE (i.e. 1)
# JU 15/02/2019: Additional variable to branch the use or not of temperature compensation of
# the measurements taken by the Atlas-scientific sensors. If version is == 2.12, the EZO circuits
# are from July 2018 and don't have enabled the command "RT,<n>", instead temperature compensation must
# be done separately from the measurements. For version 2.13 onwards, that command is enabled, so temperature
# compensation is done seamless with the measurement. Default is 2.12, because that is the case of the first
# Pydroponia system installed.
# All the variables created here will go into the Arduino's config file "inoconf.h" in "libs":
ARDUINOCONF = os.path.join(os.getenv('BIOAGROLOGPATH'), 'arduino', 'libs','ino_conf')
INOCONST = {'EZOFMW': '2.12'}

""" To allow loading modules in parallel locations """
sys.path.insert(0, PYDROPATH)
import conf.config_db as db

""" User-defined functions """


def create_subdir(path_to_subdir, subdir_name='', mode=0o644):
    """

    :param path_to_subdir: Absolute path where to create the folder SUBDIR_NAME
    :param subdir_name: Name of the folder to be created within PATH_TO_SUBDIR

    :return: Boolean flag indicating whether the folder was created or not
    """
    full_path = os.path.join(path_to_subdir, subdir_name)
    os.makedirs(full_path, mode=mode, exist_ok=True)
    out_flag = True
    if not os.path.isdir(full_path):
        out_flag = False

    return out_flag


def create_config_file(path_to_dir, config_name, config_struct):
    """

    :param path_to_dir: Absolute path to the configuration folder, default is ${HOME}/.pydroponia
    :param config_name: File name of the configuration file to use. Note that the system will update
    the CONFIG.INFO file (or will create if necessary), as this is the one used by the rest of the scripts and functions.
    :param config_struct: Configparser structure derived from the

    :return:
    """
    exists_dir = create_subdir(path_to_dir)
    if exists_dir:
        path_to_conf = os.path.join(path_to_dir, config_name)
        try:
            with open(path_to_conf, 'w') as configfile:
                config_struct.write(configfile)
        except:
            sys.exit('ERROR: Cannot create file {} in {}'.format(config_name, path_to_dir))
    else:
        sys.exit('ERROR: Cannot create subdir {}'.format(path_to_dir))
    return


def create_inoconf(path_to_libs, dict_with_variables):

    exists_dir = create_subdir(path_to_libs, mode=0o755)
    if exists_dir:
        path_to_inolibs = os.path.join(path_to_libs, 'ino_conf.h')
        try:
            with open(path_to_inolibs, 'w') as libfile:
                for key, val in dict_with_variables.items():
                    str2write = '#define {} {}'.format(key, val)
                    libfile.write(str2write)
        except:
            sys.exit('ERROR: Cannot create file {}'.format(path_to_inolibs))
    else:
        sys.exit('ERROR: Cannot create subdir {}'.format(path_to_libs))

    return


def check_db(db_location, db_name, db_table, db_fields, df_types):
    """

    :param db_location:
    :param db_name:
    :param db_table:
    :param db_fields:
    :param df_types:

    :return:
    """
    full_path = os.path.join(db_location, db_name)
    if not os.path.isfile(full_path):
        db.create_tabledb(full_path, db_table, db_fields.split(','), df_types.split(','))
    return


def default_conf(check_dirs=True):
    """

    :param check_dirs:

    :return:
    """
    global PACKNAME, HOMEPATH, PYDROPATH, CONFPATH, CONFIGNAME, ARDUINOPATH, ARDUINOBIN, DEBUG, ARDUINOCONF, INOCONST

    system_id = 1
    default_token = 'A'
    default_portid = '/dev/ttyACM0'
    default_baudrate = 9600  # baud
    default_wtimeout = 600.0  # seconds it must be longer than 5s
    default_rtimeout = 20.0  # seconds
    # JU 06/03/2019: attached_arduino is now a configurable parameter (default value TRUE)
    default_attarduino = True
    default_dbloc = os.path.join(HOMEPATH, 'Data', PACKNAME)
    # Change the name of the db and the table to match the external MySQL db
    # default_dbname  = 'sensor_data.db'
    # default_dbtable = 'sensors'
    default_dbname  = 'hydroponicdb'
    default_dbtable = 'lectura'
    default_csvloc  = os.path.join(HOMEPATH, 'Data', PACKNAME)
    default_inoloc  = ARDUINOPATH
    default_arduinobin = ARDUINOBIN
    # JU 15/02/2019: Added the parameters to define the Arduino configuration file INOCONF.h
    default_arduinolibs = ARDUINOCONF
    default_arduinoconst = INOCONST
    default_pyloc = PYDROPATH
    default_start_row = '{'
    default_end_row = '}'
    # JU 16/10/2018: Modified the order to reflect the same order as in the external MySQL db
    # JU 04/04/2021: Added the soil moisture measurement, smoist
    # default_dbfields = 'timestamp,system_id,temp,do,ec,tds,sal,ph'
    # default_dbtypes = 'DATETIME,TEXT,NUMERIC,NUMERIC,NUMERIC,NUMERIC,NUMERIC,NUMERIC,NUMERIC'
    default_dbfields = 'timestamp,temp,do,ec,tds,sal,ph,atemp,ahum,smoist,' \
                       'system_id'
    default_dbtypes = 'DATETIME,NUMERIC,NUMERIC,NUMERIC,NUMERIC,NUMERIC,' \
                      'NUMERIC,NUMERIC,NUMERIC,NUMERIC,NUMERIC'
    # Should this come from the Arduino???:
    default_csvhdr = 'Date,Time,wTemp,wDO,wEC,wTDS,wSAL,wpH, aTemp, aHum, ' \
                     'sMoist'

    config = configparser.ConfigParser()
    config['Arduino'] = {'HandShakeToken': default_token,
                         # Single character to be transferred back and forward from/to the Arduino
                         'PortID': default_portid,
                         'BaudRate': default_baudrate,
                         'StartRow': default_start_row,
                         'EndRow': default_end_row,
                         'inoLocation': default_inoloc,
                         'path2bin': default_arduinobin,
                         'path2const': default_arduinolibs,
                         'inoconst': default_arduinoconst}

    # JU 06/03/2019: attached_arduino is now a configurable parameter
    config['Communication'] = {'WriteTimeOut': default_wtimeout,  # in Seconds
                               'ReadTimeOut': default_rtimeout,   # in Seconds
                               'attached_arduino': default_attarduino}

    config['Locations'] = {'dbLocation': default_dbloc,
                           'csvLocation': default_csvloc
                           }
    config['System'] = {'dbName': default_dbname,
                        'dbTable': default_dbtable,
                        'dbFields': default_dbfields,
                        'dbTypes': default_dbtypes,
                        'csvHdr': default_csvhdr,
                        'systemID': system_id,
                        'modulePath': default_pyloc}
    config['Misc'] = {'debug': DEBUG
                      }
    create_config_file(CONFPATH, CONFIGNAME, config)
    if check_dirs:
        create_subdir(default_dbloc)
        create_subdir(default_csvloc)
        check_db(default_dbloc, default_dbname, default_dbtable, default_dbfields, default_dbtypes)

    return config


def load_conf(path_to_config_file):
    """

    :param path_to_config_file:

    :return:
    """
    global DEBUG
    if DEBUG:
        print('Loading configuration data from {}'.format(path_to_config_file))
    local_struct = configparser.ConfigParser()
    local_struct.read(path_to_config_file)
    return local_struct


def merge_conf(local_conf):
    """

    :param local_conf:

    :return:
    """
    global DEBUG
    def_conf = default_conf(check_dirs=False)
    """I'm interested only to keep the default field, so I'll use this as reference to update
    the values in the local_conf structure
    """

    for default_Vals in def_conf:
        if DEBUG:
            print('Fields values for section: {}'.format(default_Vals))
        for default_fields, default_value in def_conf[default_Vals].items():
            if local_conf.has_option(default_Vals, default_fields):
                usr_val = local_conf.get(default_Vals, default_fields)
                if DEBUG:
                    print('User-defined field {} ({})'.format(default_fields, usr_val))
                def_conf.set(default_Vals, default_fields, usr_val)
            else:
                if DEBUG:
                    print('Using default value for parameter {} ()'.format(default_fields,default_value))
    return def_conf


""" Main function """


def run_main(conf_name):
    """

    :param conf_name: Multiple configuration files can live within .pydroponia, so the user can give
    any of them to use. However, the system ALWAYS uses CONFIG.INFO

    :return: Returns a merged configuration structure that will be used to update the CONFIG.INFO
    """
    global HOMEPATH, CONFPATH, CONFIGNAME, DEBUG
    # JU 15/02/2019: Creates a default configuration file for the arduino sketches. It contains the arduino
    # variables that are system-dependent and which are critical for branching some of the Arduino code,
    # e.g. EZOVERSION.
    # Checks for an existing conf.info (or the name given as an input argument) in ${HOME}/.pydroponia
    path2conf = os.path.join(CONFPATH, conf_name)
    path2default = os.path.join(CONFPATH, CONFIGNAME)
    if os.path.isfile(path2conf):
        if DEBUG:
            print('File {} exists in {}'.format(conf_name, HOMEPATH))
        loc_conf = load_conf(path2conf)
        usr_conf = merge_conf(loc_conf)
        """ Check whether need to recreate the folders hosting the database, csv files"""
        create_subdir(usr_conf['Locations']['dbLocation'])
        create_subdir(usr_conf['Locations']['csvLocation'])
        check_db(usr_conf['Locations']['dbLocation'],
                 usr_conf['System']['dbName'],
                 usr_conf['System']['dbTable'],
                 usr_conf['System']['dbFields'],
                 usr_conf['System']['dbTypes'])
    else:
        print(
            'File {} does not exist in {}.\nUsing default conf.info file from {}'.format(conf_name, path2conf,
                                                                                         HOMEPATH))
        usr_conf = default_conf()

    """ Whether the conf.info file exists or not, it is updated with the information from the user-defined 
    configuration file. There may be other more efficients options, but for now it works... """
    with open(path2default, 'w') as configfile:
        usr_conf.write(configfile)

    """Creates the default inoconf.h. This file is created/overwriten everytime Pydroponia (re)starts """
    # create_inoconf(usr_conf['Arduino']['path2const'],
    #                usr_conf['Arduino']['inoconst'])

    return usr_conf


def config(config_file_name='conf.info'):
    """
    So when is called within another function, it returns a configuration structure
    Syntax is:
    import pydro_config
    config_struct = pydro_config.config(config_file_name<='conf.info'>)

    :param config_file_name: Configuration file to be merged with conf.info
    :return: Calls the main function with the input argument
    """
    return run_main(config_file_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creates or loads a configuration file conf.info',
                                     prog='source_code')
    parser.add_argument('-f', '--config',
                        help='Configuration file to be merged with the default conf.info file. '
                             'If no arguments are give, the default conf.info file is used',
                        metavar='FILENAME',
                        default=CONFIGNAME,
                        required=False)
    args = vars(parser.parse_args())
    run_main(args['config'])
