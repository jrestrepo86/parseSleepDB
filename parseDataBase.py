#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SLEEP DATABASE PARSE
"""
import glob
import logging
import os
from datetime import datetime

import numpy as np
import pandas as pd
import scipy.io as spio
from matplotlib.pyplot import figure, plot
from tqdm import tqdm

from makeVariablesFile import buildVariablesFile
from parseRespEvents import parseRespEvents
from parseSignalsEdf import parseSignalsEdf
from parseSleepStages import parseSleepStages
from parseVariables import parseVariables

# ROOT_PATH = '/media/data/shhs'
ROOT_PATH = './data'
EDF_PATH = f'{ROOT_PATH}/edfs/shhs1'
SLEEP_STAGING_PATH = f'{ROOT_PATH}/annotations-staging/shhs1'
NSRR_EVENTS_PATH = f'{ROOT_PATH}/annotations-events-nsrr/shhs1'
VARIABLES_FILE = f'{ROOT_PATH}/shhs1-dataset-0.9.0.csv'
MAT_OUT_PATH = f'{ROOT_PATH}/matlab/shhs1'
VARS_FILE_NAME = f'{ROOT_PATH}/matlab/shhs1/variables.csv'

# crear folder de salida
if not os.path.isdir(MAT_OUT_PATH):
    os.makedirs(MAT_OUT_PATH)
    print(f'Archivos creados en: {MAT_OUT_PATH}')

# ------
SIGNALS_EDF_NAMES = ['SaO2', 'H.R.', 'OX stat']
# ------
SLEEP_STAGES_MAPS = [
    {
        'targetName': 'sleepTarget1',
        'map': {
            '0': [0, 6],
            '1': [1, 2, 3, 4, 5],
        }
    },
    {
        'targetName': 'sleepTarget2',
        'map': {
            '0': [0, 6],
            '1': [1],
            '2': [2],
            '3': [3],
            '4': [4],
            '5': [5],
        }
    },
]
# ------
RESP_EVENTS_MAPS = [
    {
        'targetName':
        'targetA0',
        'maps': [{
            'map':
            1,
            'event':
            ['Hypopnea', 'Obstructive apnea', 'Central Apnea', 'Mixed Apnea'],
            'SpO2 desaturation':
            None
        }]
    },
    {
        'targetName':
        'targetA0H4',
        'maps': [
            {
                'map': 1,
                'event': ['Hypopnea'],
                'SpO2 desaturation': 4.0
            },
            {
                'map': 2,
                'event': ['Obstructive apnea', 'Central Apnea', 'Mixed Apnea'],
                'SpO2 desaturation': None
            },
        ]
    },
    {
        'targetName':
        'targetA0H3',
        'maps': [
            {
                'map': 1,
                'event': ['Hypopnea'],
                'SpO2 desaturation': 3.0
            },
            {
                'map': 2,
                'event': ['Obstructive apnea', 'Central Apnea', 'Mixed Apnea'],
                'SpO2 desaturation': None
            },
        ]
    },
]
# ------
# Variables
VARIABLES = ['ahi_a0h3', 'ahi_a0h4', 'SlpPrdP']
# ------
# log file
LOG_FILE_NAME = f'{MAT_OUT_PATH}/PDBlogfile.log'
logging.basicConfig(
    filename=LOG_FILE_NAME,
    level=logging.INFO,
    filemode='w',
)
# ------


def write2mat(fname, out_data):

    now = datetime.now()
    current_time = now.strftime("%d/%m/%Y %H:%M:%S")
    infoText = [f'Data generated at {current_time}.']
    out_data['info'] = infoText

    fname = f'{MAT_OUT_PATH}/{fname}.mat'
    spio.savemat(fname, out_data)


def calc_ah_index(fname, signal_length, out_dict, th):

    AH_RESP_MAP = {
        'targetName':
        'resp_ahi',
        'maps': [
            {
                'map': 1,
                'event': ['Hypopnea'],
                'SpO2 desaturation': th
            },
            {
                'map': 2,
                'event': ['Obstructive apnea', 'Central Apnea', 'Mixed Apnea'],
                'SpO2 desaturation': None
            },
        ],
    }
    AH_SLEEP_MAP = {
        'targetName': 'sleep_ahi',
        'map': {
            '0': [0, 6],
            '1': [1, 2, 3, 4, 5],
        }
    }

    od_, _ = parseSleepStages(SLEEP_STAGING_PATH,
                              fname,
                              signal_length=signal_length,
                              out_dict={},
                              sleepStagesMaps=[AH_SLEEP_MAP])
    od_ = parseRespEvents(NSRR_EVENTS_PATH,
                          fname,
                          signal_length=signal_length,
                          out_dict=od_,
                          respEventsMaps=[AH_RESP_MAP])

    # tst = od_['tst']
    SlpPrd = out_dict['SlpPrdP']
    sleep_events = od_['sleep_ahi']
    ah_events = od_['resp_ahi']
    temp_ah_events = (ah_events > 0).astype(float)

    # remove awake and partially awake events
    ev_diff = np.diff(temp_ah_events)
    mark_points = np.diff(temp_ah_events *
                          (1 - sleep_events)) * np.abs(ev_diff)
    for i in np.where(mark_points == 1)[0]:
        try:
            j = np.where(ev_diff[i + 1:] < 0)[0][0]
            ah_events[i + 1:i + 2 + j] = 0
        except:
            pass

    out_dict['targetAH_th{th}_masked_sleep'] = ah_events * sleep_events
    n_ah_events = (np.diff(ah_events * sleep_events) > 0).sum()
    ahi = 60 * n_ah_events / (SlpPrd)
    out_dict[f'cal_ahi_a0h{th}'] = ahi

    return out_dict


def cropNans(out_dict):

    iflag = True
    for i, (s, val) in enumerate(out_dict.items()):
        if isinstance(val, (np.ndarray)):
            if iflag:
                nans = np.isnan(val)
                iflag = False
            else:
                nans += np.isnan(val)

    for s, val in out_dict.items():
        # puede haber variables escalares en el diccionario (como tst)
        if isinstance(val, (np.ndarray)):
            if val.size > 1:
                out_dict[s] = val[~nans]
    return out_dict


def parseFile(fname, var_df):
    # logging.info(f'{fname}')
    out_dict, sl = parseSignalsEdf(EDF_PATH,
                                   fname,
                                   out_dict={
                                       'fileID': fname,
                                       'error': False
                                   },
                                   signalsNames=SIGNALS_EDF_NAMES)
    if not out_dict['error']:
        out_dict, _ = parseSleepStages(SLEEP_STAGING_PATH,
                                       fname,
                                       signal_length=sl,
                                       out_dict=out_dict,
                                       sleepStagesMaps=SLEEP_STAGES_MAPS)

        out_dict = parseRespEvents(NSRR_EVENTS_PATH,
                                   fname,
                                   signal_length=sl,
                                   out_dict=out_dict,
                                   respEventsMaps=RESP_EVENTS_MAPS)
        out_dict = parseVariables(VARIABLES_FILE,
                                  signalID=fname,
                                  out_dict=out_dict,
                                  variables=VARIABLES)

        out_dict = calc_ah_index(fname,
                                 signal_length=sl,
                                 out_dict=out_dict,
                                 th=4)
        out_dict = calc_ah_index(fname,
                                 signal_length=sl,
                                 out_dict=out_dict,
                                 th=3)

        # crop trailing nans
        out_dict = cropNans(out_dict)
        del out_dict['error']
        write2mat(fname, out_dict)

        # variables file
        calc_vars = {
            'tst': out_dict['tst'],
            'cal_ahi_a0h3': out_dict['cal_ahi_a0h3'],
            'cal_ahi_a0h4': out_dict['cal_ahi_a0h4'],
        }
        var_df = buildVariablesFile(VARIABLES_FILE,
                                    signalID=fname,
                                    df_in=var_df,
                                    calc_vars=calc_vars)
    return var_df


def parseDataBase(fnames=None, n_start=None, nfiles=None, disableTqdm=False):

    # read files name in folder
    if fnames is None:
        files = glob.glob(f'{EDF_PATH}/*.edf')
        fnames = [fn.split('/')[-1] for fn in files]
        fnames = [fn.split('.')[0] for fn in fnames]

    if n_start is not None:
        fnames = fnames[n_start:]

    if nfiles is not None:
        fnames = fnames[:nfiles]

    # parse data
    var_df = pd.DataFrame()
    for fn in tqdm(fnames, disable=disableTqdm):
        var_df = parseFile(fn, var_df)

    var_df.to_csv(VARS_FILE_NAME)


if __name__ == "__main__":
    logging.warning(f'pid: {os.getpid()}')
    parseDataBase()
    # registros con problemas 203535
    # fnames = ['shhs1-203535', 'shhs1-203540', 'shhs1-203541']
    # fnames = ['shhs1-203535']
    # fnames = ['shhs1-200001']
    # fnames = ['shhs1-200019']
    # fnames = ['shhs1-200829']
    # parseDataBase(fnames=fnames, disableTqdm=True)
    # parseDataBase(n_start=0, nfiles=100, disableTqdm=False)
