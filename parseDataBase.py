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
import scipy.io as spio
from matplotlib.pyplot import plot
from tqdm import tqdm

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

# crear folder de salida
if not os.path.isdir(MAT_OUT_PATH):
    os.makedirs(MAT_OUT_PATH)
    print(f'Archivos creados en: {MAT_OUT_PATH}')

# ------
SIGNALS_EDF_NAMES = ['SaO2', 'H.R.', 'OX stat']
# ------
SLEEP_STAGES_MAP_T1 = {
    'targetName': 'sleepTarget1',
    'map': {
        '0': [0, 6],
        '1': [1, 2, 3, 4, 5],
    }
}
SLEEP_STAGES_MAP_T2 = {
    'targetName': 'sleepTarget2',
    'map': {
        '0': [0, 6],
        '1': [1],
        '2': [2],
        '3': [3],
        '4': [4],
        '5': [5],
    }
}
# ------
RESP_EVENTS_MAP_T1 = {
    'targetName': 'targetAH',
    'map': {
        '1': ['Hypopnea'],
        '2': ['Obstructive apnea'],
        '3': ['Central Apnea'],
        '4': ['Mixed Apnea'],
    },
}
RESP_EVENTS_MAP_T2 = {
    'targetName': 'targetA',
    'map': {
        '1': ['Hypopnea', 'Obstructive apnea', 'Central Apnea', 'Mixed Apnea'],
    },
}
RESP_EVENTS_MAP_T3 = {
    'targetName': 'desaturation',
    'map': {
        '1': ['SpO2 desaturation'],
    },
}
# ------
# Variables
VARIABLES = ['ahi_a0h3a', 'SlpPrdP', 'OARBP', 'OAROP', 'OANBP', 'OANOP']
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


def calc_ah_index(fname, signal_length, out_dict):

    # AH_RESP_MAP = {
    #     'targetName': 'resp_ahi',
    #     'map': {
    #         '1':
    #         ['Hypopnea', 'Obstructive apnea', 'Central Apnea', 'Mixed Apnea'],
    #     },
    # }
    AH_SLEEP_MAP = {
        'targetName': 'sleep_ahi',
        'map': {
            '0': [0, 6],
            '1': [1, 2, 3, 4, 5],
        }
    }
    AH_RESP_MAP = {
        'targetName': 'resp_ahi',
        'map': {
            '1': ['Hypopnea'],
            '2': ['Obstructive apnea'],
            '3': ['Central Apnea'],
            '4': ['Mixed Apnea'],
        },
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

    tst = od_['tst']
    sleep_mask = od_['sleep_ahi']
    ah_events = od_['resp_ahi']
    n_ah_events = (np.diff(ah_events * sleep_mask) > 0).sum()
    n_ah_events0 = (np.diff(ah_events) > 0).sum()

    ahi = 60 * n_ah_events / (tst)
    ahi0 = 60 * n_ah_events0 / (tst)
    out_dict['ahi'] = ahi
    out_dict['ahi0'] = ahi0

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


def parseFile(fname):
    # logging.info(f'{fname}')
    out_dict, sl = parseSignalsEdf(EDF_PATH,
                                   fname,
                                   out_dict={
                                       'fileID': fname,
                                       'error': False
                                   },
                                   signalsNames=SIGNALS_EDF_NAMES)
    if not out_dict['error']:
        out_dict, _ = parseSleepStages(
            SLEEP_STAGING_PATH,
            fname,
            signal_length=sl,
            out_dict=out_dict,
            sleepStagesMaps=[SLEEP_STAGES_MAP_T1, SLEEP_STAGES_MAP_T2])

        out_dict = parseRespEvents(NSRR_EVENTS_PATH,
                                   fname,
                                   signal_length=sl,
                                   out_dict=out_dict,
                                   respEventsMaps=[
                                       RESP_EVENTS_MAP_T1, RESP_EVENTS_MAP_T2,
                                       RESP_EVENTS_MAP_T3
                                   ])
        out_dict = parseVariables(VARIABLES_FILE,
                                  signalID=fname,
                                  out_dict=out_dict,
                                  variables=VARIABLES)

        out_dict = calc_ah_index(fname, signal_length=sl, out_dict=out_dict)

        # crop trailing nans
        out_dict = cropNans(out_dict)
        del out_dict['error']
        write2mat(fname, out_dict)


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
    for fn in tqdm(fnames, disable=disableTqdm):
        parseFile(fn)


if __name__ == "__main__":
    logging.warning(f'pid: {os.getpid()}')
    # parseDataBase()
    # registros con problemas 203535
    # fnames = ['shhs1-203535', 'shhs1-203540', 'shhs1-203541']
    fnames = ['shhs1-203535']
    parseDataBase(fnames=fnames, disableTqdm=True)
    # parseDataBase(n_start=0, nfiles=100, disableTqdm=False)
