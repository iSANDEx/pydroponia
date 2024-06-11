#!/usr/bin/env python3
"""
display_sensor_data.py

This is the main module to start and manage the web interface to display the data

THIS SHOULDN'T BE USED AS A PERMANENTE SOLUTION, IT IS ONLY A PoC!!!

The main issue is that requires to be run by 'sudo'

Created by Jose L. Ulloa <jose.ulloa@isandex.com>
20/July/2018
"""

""" Load modules"""

import sys
import io
import os
import copy
import configparser
import logging

""" To allow loading modules in parallel locations """
PYDROPATH = os.getenv('PYDROPATH')
sys.path.insert(0, PYDROPATH)

# import conf.pydro_config as pydro_config

import datetime
import sqlite3
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from flask import Flask, render_template, send_file, make_response, request

""" More details here from the Flask tutorials """
app = Flask(__name__)

""" User-defined functions """
app._static_folder = os.path.join(PYDROPATH, 'web_server', 'static')


def get_last_data():
    """ Retrieve LAST data available from the database """
    last_data = get_nth_data(1)
    return last_data


def get_nth_data(n):
    """ Retrieve N data from the last one (including it) """
    global path_to_db, table_name
    conn = sqlite3.connect(path_to_db)
    curs = conn.cursor()
    query = curs.execute('SELECT * FROM {} ORDER BY timestamp DESC LIMIT {}'.format(table_name, n))
    cols_name = [fieldnames[0] for fieldnames in query.description]
    data = query.fetchall()
    db_data = {key: [] for key in cols_name}
    for row in reversed(data):
        for j, xij in enumerate(row):
            db_data[cols_name[j]].append(xij)
    conn.close()
    return db_data


""" Retrieve HISTORICAL data from database based on two dates """
def get_hist_data(start_date, end_date):
    """ Retrieve historical data from the database, between two dates given by the user """
    global path_to_db, table_name
    conn = sqlite3.connect(path_to_db)
    db_inst = 'SELECT * FROM {0:s} WHERE timestamp  BETWEEN \'{1:s}\' AND \'{2:s}\''.format(table_name,
                                                                                            start_date.replace('/',
                                                                                                               ' '),
                                                                                            end_date.replace('/', ' '))
    curs = conn.cursor()
    curs.execute(db_inst)
    cols_name = [fieldnames[0] for fieldnames in curs.description]
    data = curs.fetchall()
    db_data = {key: [] for key in cols_name}
    for row in data:
        for j, xij in enumerate(row):
            db_data[cols_name[j]].append(xij)
    conn.close()
    return db_data


def sampling():
    """ Get sampling period, in seconds"""
    two_data = get_nth_data(2)
    times = two_data['timestamp']
    fmt = '%Y-%m-%d %H:%M:%S'
    t_stamp_0 = datetime.datetime.strptime(times[0], fmt)
    t_stamp_1 = datetime.datetime.strptime(times[1], fmt)
    sampl_period = t_stamp_1 - t_stamp_0
    sampl_period = (sampl_period.total_seconds())
    return (sampl_period)


def name_dictionary(field_name):
    translation = {'temp': 'Temperature [C]',
                   'atemp': 'Air Temp [C]',
                   'ahum': 'Rel Humidity Air [%]',
                   'smoist': 'Soil Moisture [%]',
                   'ph': 'pH [pH]',
                   'ec': 'Electroconductividad [uS/cm]',
                   'tds': 'Total Dissolved Solutes [ppm]',
                   'sal': 'Salinity [PSU]',
                   'do': 'Dissolved Oxygen [mg/L]'}
    if field_name in translation.keys():
        xlabels = translation[field_name]
    else:
        xlabels = copy.copy(field_name)

    return xlabels


""" Main block """
@app.route("/")
def index():
    global path_to_db, table_name, start_date, end_date
    last_data = get_last_data()
    date_i = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    date_f = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

    template_data = {'startYear': date_i.year,
                     'startMonth': date_i.month,
                     'startDay': date_i.day,
                     'startHour': date_i.hour,
                     'startMin': date_i.minute,
                     'endYear': date_f.year,
                     'endMonth': date_f.month,
                     'endDay': date_f.day,
                     'endHour': date_f.hour,
                     'endMin': date_f.minute
                     }
    for (key, value) in last_data.items():
        template_data[key] = value[0]

    return render_template('index.html', **template_data)


""" Requesting by date range """
@app.route('/', methods=['POST'])
def my_form_post():
    global sample_period, start_date, end_date

    start_yyyy = int(request.form['startYear'])
    start_mm = int(request.form['startMonth'])
    start_dd = int(request.form['startDay'])
    start_hh = int(request.form['startHour'])
    start_min = int(request.form['startMin'])
    day_0 = datetime.datetime(start_yyyy, start_mm, start_dd, start_hh, start_min, 0)
    start_date = datetime.datetime.strftime(day_0, '%Y-%m-%d %H:%M:%S')

    end_yyyy = int(request.form['endYear'])
    end_mm = int(request.form['endMonth'])
    end_dd = int(request.form['endDay'])
    end_hh = int(request.form['endHour'])
    end_min = int(request.form['endMin'])
    day_1 = datetime.datetime(end_yyyy, end_mm, end_dd, end_hh, end_min, 0)
    end_date = datetime.datetime.strftime(day_1, '%Y-%m-%d %H:%M:%S')

    delta_time = day_1 - day_0
    range_time = delta_time.total_seconds()

    if range_time < sample_period:
        day_0 = day_1 - datetime.timedelta(0, 4.0 * sample_period)
        start_date = datetime.datetime.strftime(day_0, '%Y-%m-%d %H:%M:%S')
    last_data = get_last_data()
    template_data = {'startYear': start_yyyy,
                     'startDay': start_dd,
                     'startMonth': start_mm,
                     'startHour': start_hh,
                     'startMin': start_min,
                     'endYear': end_yyyy,
                     'endMonth': end_mm,
                     'endDay': end_dd,
                     'endHour': end_hh,
                     'endMin': end_min
                     }
    for (key, value) in last_data.items():
        template_data[key] = value[0]

    return render_template('index.html', **template_data)


""" This should be generalised to deal with multiple/variable number of sensors 
(see @app.route('plot/hum') below """

@app.route('/plot/parameters')
def plot_parameters():
    global start_date, end_date
    query_data = get_hist_data(start_date, end_date)
    cols_name = list(query_data.keys())
    times = query_data['timestamp']
    sysid = query_data['system_id']
    for els2del in ['timestamp', 'system_id']:
        cols_name.pop(cols_name.index(els2del))

    nfigs = len(cols_name)
    if nfigs <= 3:
        ncols = nfigs
        nrows = 1
    else:
        ncols = np.ceil(np.sqrt(nfigs))
        nrows = np.ceil(nfigs / ncols)
    fig_width = ncols * 5.0
    fig_height = nrows * 5.0
    fig = Figure(figsize=(fig_width, fig_height))
    t_axis = [datetime.datetime.strptime(xj, '%Y-%m-%d %H:%M:%S') for xj in times]

    for indfig, sensor_name in enumerate(cols_name):
        axis = fig.add_subplot(nrows, ncols, indfig+1)
        ys = query_data[sensor_name]
        axis.set_title(name_dictionary(sensor_name))
        axis.set_xlabel("Date")
        axis.grid(True)
        axis.plot(t_axis, ys)
        fig.autofmt_xdate()
        minys = min(ys)
        maxys = max(ys)
        if minys*maxys != 0.0:
            axis.set_ylim([0.5 * min(ys), 1.5 * max(ys)])

    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'

    return response


""" Define and initialise global variables """
global path_to_db, table_name, logger
""" 
This has to run as sudo, so need to re-define the key env variables:
PYDROCONF=${HOME}/.pydroponia
PYDROPATH=${PYDROPATH}
The full command line instructions should be:
pi@raspberrypi:~ $ cd ~/bin/bioagro/pydroponia/web_server
pi@raspberrypi:~/bin/bioagro/pydroponia/web_server $ sudo PYDROCONF=${HOME}/.pydroponia PYDROPATH=${PYDROPATH} ./displ_sensor_data.py
"""
""" Load configuration file to define relevant parameters """
# config_pars = pydro_config.config()
path_to_config_file = os.path.join(os.getenv('PYDROCONF'), 'conf.info')
config_pars = configparser.ConfigParser()
config_pars.read(path_to_config_file)

path_to_db = os.path.join(config_pars['Locations']['dbLocation'], config_pars['System']['dbName'])
table_name = config_pars['System']['dbTable']

nth_data = get_last_data()
end_date = nth_data['timestamp'][0]
now = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
today = now - datetime.timedelta(0, 3600, 0)  # default shows 1 hr of data collection
start_date = today.strftime('%Y-%m-%d %H:%M:%S')
sample_period = sampling()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)