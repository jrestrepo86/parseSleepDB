#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SLEEP DATABASE PARSE
"""
import glob
import os
from datetime import datetime

import scipy.io as spio
from matplotlib.pyplot import plot

from parseRespEvents import parseRespEvents
from parseSignalsEdf import parseSignalsEdf
from parseSleepStages import parseSleepStages

ROOT_PATH = './data'
EDF_PATH = f'{ROOT_PATH}/edfs/shhs1'
SLEEP_STAGING_PATH = f'{ROOT_PATH}/annotations-staging/shhs1'
NSRR_EVENTS_PATH = f'{ROOT_PATH}/annotations-events-nsrr/shhs1'
MAT_OUT_PATH = f'{ROOT_PATH}/matlab/shhs1'
# ------
SIGNALS_MAP = {'SaO2': 0, 'HR': 1, 'OXstat': 13}
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
        '0': [0],
        '1': [1],
        '2': [2],
        '3': [3, 4, 5],
    }
}
# ------
RESP_EVENTS_MAP_T1 = {
    'targetName': 'targetAH',
    'map': {
        '1': ['Hypopnea'],
        '2': ['Obstructive apnea']
    },
}

RESP_EVENTS_MAP_T2 = {
    'targetName': 'targetA',
    'map': {
        '1': ['Hypopnea', 'Obstructive apnea']
    },
}
# ------


def write2mat(fname, out_data):

    # crear folder de salida
    if not os.path.isdir(MAT_OUT_PATH):
        os.makedirs(MAT_OUT_PATH)
        print(f'Archivos creados en: {MAT_OUT_PATH}')

    now = datetime.now()
    current_time = now.strftime("%d/%m/%Y %H:%M:%S")
    infoText = [f'Data generated at {current_time}.']
    out_data['info'] = infoText

    fname = f'{MAT_OUT_PATH}/{fname}.mat'
    spio.savemat(fname, out_data)


def parseFile(fname):

    out_dict, sl = parseSignalsEdf(EDF_PATH,
                                   fname,
                                   out_dict={},
                                   signalsMap=SIGNALS_MAP)
    out_dict, _ = parseSleepStages(
        SLEEP_STAGING_PATH,
        fname,
        signal_length=sl,
        out_dict=out_dict,
        sleepStagesMaps=[SLEEP_STAGES_MAP_T1, SLEEP_STAGES_MAP_T2])

    out_dict = parseRespEvents(
        NSRR_EVENTS_PATH,
        fname,
        signal_length=sl,
        out_dict=out_dict,
        respEventsMap=[RESP_EVENTS_MAP_T1, RESP_EVENTS_MAP_T2])

    write2mat(fname, out_dict)


def parseDataBase(nfiles=None):

    # read files name in folder
    files = glob.glob(f'{EDF_PATH}/*.edf')
    fnames = [fn.split('/')[-1] for fn in files]
    fnames = [fn.split('.')[0] for fn in fnames]
    # parse data
    if nfiles is not None:
        fnames = fnames[:nfiles]

    for fn in fnames:
        parseFile(fn)


if __name__ == "__main__":
    parseDataBase()
