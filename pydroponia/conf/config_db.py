#!/usr/bin/env python3

"""
This script creates and manages the tables in the database
where to store the data from the sensors
(see tutorial: http://www.instructables.com/id/From-Data-to-Graph-a-Web-Journey-With-Flask-and-SQL/

[JU] This assumes a very simple structure, which is what we want at this stage:
<timestamp>, <system_id>, <sensor1_data>, <sensor2_data>,...

Becuase this should log automatically from the system, we can
pre-define that for each insertion, the timestamp is added
automatically by the system (like in the tutorial)
"""

""" Load modules"""
import sys
import sqlite3 as lite

#JU 16/10/2018: Load MySQL modules:
# Looks like MySQLdb is not longer supported, it is recommended to use either mysqlclient or mysql.connector
# see this thread for more info
# https://stackoverflow.com/questions/43102442/whats-the-difference-between-mysqldb-mysqlclient-and-mysql-connector-python
# To keep compatibility with MySQLdb, let's rename the modules when loaded:
# import mysql.connector as mysql_db
import MySQLdb as mysql_db

import datetime
#JU 16/10/2018: End

""" To allow loading modules in parallel locations """
sys.path.insert(0, '../source_code')

""" User-defined functions """


def create_tabledb(path_to_database, table_name, field_names, field_types):
    """

    :param path_to_database:
    :param table_name:
    :param field_names:
    :param field_types:
    :return:
    """
    con = lite.connect(path_to_database)
    dropTable = 'DROP TABLE IF EXISTS {}'.format(table_name)
    creaTable = 'CREATE TABLE {}('.format(table_name)
    for colname, coltype in zip(field_names, field_types):
        creaTable += colname + ' ' + coltype + ','
    creaTable = creaTable[:-1] + ')'
    with con:
        cur = con.cursor()
        cur.execute(dropTable)
        cur.execute(creaTable)
        con.commit()
    # close the database after use
    # not needed if using 'with'
    # con.close()
    return


def pop_table_db(path_to_database, table_name, data_to_add):
    """
    pop_table_db Populates the database with the readings

    :param path_to_database:
    :param table_name:
    :param data_to_add: It is just a list with the data to add, it must be ordered according to the table
    :return:
    """

    #JU 16/10/2018: Added support for a MySQL database (preliminar test)
    # - Identification of the database and MySQL credentials (must change according to the actual db and
    # placed here just for testing, it is recommended to have this information in a config file instead):
    #JU 10/11/2018: When using it in a real setting use this:
    #config = {'user': <real_user_name>,
    #          'password': <real_password>,
    #          'host': real.ip.address,
    #          'database': 'hydroponicdb'
    #          }
    # JU 17/12/2018: Setup another Raspberry Pi to host the database:
    config = {'user': 'pydroponia',
             'password': 'pydr0p0n1a',
             'host': '192.168.0.23',
             'port': 3306,
             'database': 'hydroponicdb'
             }

    # JU 06/03/2019: Date and time are now defined when reading from Arduino, so is now a unique value for all dB's
    # (external MySQL and internally-defined SQLite) as well as in the CSV file:
    fecha, hora = data_to_add[:2]
    # JU 06/03/2019: End
    try:
        # If it can establish a connection, then add the data into the MySQL database, otherwise it'll write it into the
        # local SQLite3 database (need to match the names though)
        conn = mysql_db.connect(**config)
        hdrrow = 'fecha, hora, wtemp,wec,wtds,wsal,wph,atemp,ahum, ' \
                 'smoist, systemid'
        db_instruction = 'INSERT INTO {}({}) VALUES(\''.format(table_name,
                                                               hdrrow)
        db_instruction += '\',\''.join(['{}'.format(xi) for xi in data_to_add])
        db_instruction += '\')'

        cur = conn.cursor()
        cur.execute(db_instruction)
        conn.commit()
        cur.close()

    except mysql_db.Error as mysql_error:
        print('Error al conectar a la base de datos remota.')
        print(mysql_error)

    #JU 16/10/2018: End
    con = lite.connect(path_to_database)
    # JU 06/03/2019: Reformat the INSERT statement to be compatible with the update that define the time and date at
    # the time of reading from the arduino, rather than when writing into the dB:
    # db_instruction = 'INSERT INTO {} VALUES(datetime(\'now\')'.format(table_name)
    hoydia = datetime.datetime.combine(datetime.datetime.strptime(fecha, "%Y/%m/%d"),
                                        datetime.datetime.strptime(hora, "%H:%M:%S").time())

    db_instruction = 'INSERT INTO {} VALUES(datetime(\'{}\', \'utc\')'.format(table_name, hoydia)
    # JU 06/03/2019: End
    if hasattr(data_to_add, '__len__'):
        for xj in data_to_add[2:]: # JU 06/03/2019: The relevant values for this loop now start from index 2 (skips date and time)
            db_instruction += ', {}'.format(xj)
        db_instruction += ')'
    else:
        db_instruction += ', {})'.format(data_to_add[2:]) # JU 06/03/2019: The relevant values for this loop now start from index 2 (skips date and time)

    with con:
        cur = con.cursor()
        cur.execute(db_instruction)
        con.commit()
    """ Close the database after user 
            but not needed if using 'with'
    """
    # con.close()

    return


def print_db(path2Database, tabledb):
    """
    :param path2Database:
    :param tabledb:
    :return:
    """
    con = lite.connect(path2Database)
    cur = con.cursor()

    print('Entire database contents:')
    for row in cur.execute('SELECT * FROM {}'.format(tabledb)):
        print(row)
