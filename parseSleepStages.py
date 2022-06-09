#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SLEEP DATABASE PARSE
parse sleep stages

Sleep Heart Health Study staging annotations follow this schema:
    0: Wake
    1: Stage 1 Sleep
    2: Stage 2 Sleep
    3: Stage 3 Sleep
    4: Stage 4 Sleep
    5: REM Sleep
    6: Wake/Movement
    9: Unscored
"""

import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CSV_SEP = ','
EPOCH_DURATION = 30


def correctState9(target):
    '''
    Si el estado es 9, le asigna el estado anterior
    '''
    inds = np.where(target == 9)[0]
    for i in inds:
        target[i] = target[i - 1]
    return target


def parseSleepStages(csv_path,
                     fname,
                     signal_length,
                     out_dict,
                     sleepStagesMaps=None):
    # read file
    fname = f'{csv_path}/{fname}-staging.csv'
    df = pd.read_csv(fname, sep=CSV_SEP, index_col=0)
    data_stages = df['Stage']
    if EPOCH_DURATION * df.size != signal_length:
        text = f'Epoch*{EPOCH_DURATION} not equal to data length.'
        logging.error(text)
        raise ValueError(text)

    # parse all stages in file
    target_xml = np.zeros(signal_length)
    ind = 0
    for stage in data_stages:
        target_xml[ind:ind + EPOCH_DURATION] = stage
        ind += EPOCH_DURATION
    # corregir estado 9
    target_xml = correctState9(target_xml)
    # calcular tiempo total de sueño
    out_dict['tst'] = np.sum(target_xml)
    # map stages
    if sleepStagesMaps is not None:
        target = target_xml.copy()
        for st_map in sleepStagesMaps:
            targetName = st_map['targetName']
            for map, vals in st_map['map'].items():
                inds = np.isin(target, vals)
                target[inds] = int(map)
            out_dict[targetName] = target
    else:
        targetName = 'sleepDefaultTarget'
        out_dict[targetName] = target
    return out_dict, target_xml


if __name__ == "__main__":
    ROOT_PATH = './data'
    SLEEP_STAGING_PATH = f'{ROOT_PATH}/annotations-staging/shhs1'
    fname = 'shhs1-200001'
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
    out_dict, test_target = parseSleepStages(
        SLEEP_STAGING_PATH,
        fname='shhs1-200001',
        signal_length=32520,
        out_dict={},
        sleepStagesMaps=[SLEEP_STAGES_MAP_T1, SLEEP_STAGES_MAP_T2])
    pass
