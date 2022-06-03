#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SLEEP DATABASE PARSE
parse signals in edf file
"""

import re

import numpy as np
import pyedflib
from pyedflib import highlevel
from scipy.interpolate import interp1d

# signal and channel number in edf
OXSTAT_STATES = [1, 2, 3]


def NanInterp(x):
    x = x.copy()
    nans = np.isnan(x)

    def t(z):
        return z.nonzero()[0]

    x[nans] = interp1d(t(~nans),
                       x[~nans],
                       kind='linear',
                       bounds_error=False,
                       copy=True)(t(nans))
    return x


def getSignals(edf_data, out_dict, signalsMap):

    for s, ch in signalsMap.items():
        out_dict.update({s: edf_data[ch][:]})

    return out_dict, edf_data[0].size


def SaO2_correction(out_dict):
    '''Enmascara la señal SaO2 con la información de OxStat e interpola
    linealmente entre las muestras adyacentes a la desconexión.
    OxStat
        0: buen funcionamiento
        2: mal funcionamiento
        3: funcionamiento mediocre
    '''
    Oxstat = out_dict['OXstat']
    SaO2 = out_dict['SaO2']
    # NaN en SaO2 donde OxStat = 2 o 3
    SaO2[np.isin(Oxstat, OXSTAT_STATES)] = np.nan
    # Interpolar NaN
    SaO2_ = NanInterp(SaO2)
    out_dict['SaO2'] = SaO2_
    return out_dict


def HR_correction(out_dict):
    '''Enmascara la señal HR con la información de OxStat y con la misma HR,
    luego interpola linealmente entre las muestras adyacente.
    '''
    LOWER_BOUND, UPPER_BOUND = 40, 110
    Oxstat = out_dict['OXstat']
    HR = out_dict['HR']
    # NaN en HR donde OxStat = 2 o 3
    ind_OXstat = np.isin(Oxstat, OXSTAT_STATES)
    # Nan donde HR supere umbrales
    ind_lb = HR < LOWER_BOUND
    ind_ub = HR > UPPER_BOUND
    # combinar índices
    ind = np.logical_or(ind_OXstat, np.logical_or(ind_lb, ind_ub))
    HR[ind] = np.nan
    # Interpolar NaN
    HR_ = NanInterp(HR)
    out_dict['HR'] = HR_
    return out_dict


def parseSignalsEdf(edf_path, fname, out_dict, signalsMap=None):
    fname = f'{edf_path}/{fname}.edf'
    # read edf file
    signals, signal_headers, header = highlevel.read_edf(fname)
    # obtener todas las señales del edf
    if signalsMap is None:
        signalsMap = {}
        for i, s in enumerate(signal_headers):
            sname = s['label']
            # remover paréntesis del nombre
            sname = re.sub('\(.*?\)', '()', sname)
            # MATLAB no acepta . o espacio en nombre de variable
            for a in ['.', ' ', '(', ')']:
                sname = sname.replace(a, '')
            signalsMap[sname] = i

    # parse data into out_data
    out_dict, signal_lenght = getSignals(signals, out_dict, signalsMap)
    out_dict = SaO2_correction(out_dict)
    out_dict = HR_correction(out_dict)

    return out_dict, signal_lenght


if __name__ == "__main__":
    ROOT_PATH = './data'
    EDF_PATH = f'{ROOT_PATH}/edfs/shhs1'
    SIGNALS_MAP = {'SaO2': 0, 'HR': 1, 'OXstat': 13}
    out_dict, signal_lenght = parseSignalsEdf(EDF_PATH,
                                              fname='shhs1-200002',
                                              out_dict={},
                                              signalsMap=SIGNALS_MAP)
    # out_dict, signal_lenght = parseSignalsEdf(
    #     EDF_PATH,
    #     fname='shhs1-200001',
    #     out_dict={},
    # )
    pass
