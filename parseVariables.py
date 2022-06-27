#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PARSE SLEEP DATABASE

Parse variables from [shhs1-dataset-0.90.0.csv, shhs2-dataset-0.90.0.csv]
Variables can be seen in: https://sleepdata.org/datasets/shhs/variables
Varibales:
    * ahi_a0h3a
    * SlpPrdP
"""

import logging

import numpy as np
import pandas as pd

CSV_SEP = ','
DEFAUL_VARIABLES = ['ahi_a0h3a', 'ahi_a0h3', 'SlpPrdP']


def parseVariables(csv_file, signalID, out_dict, variables=None):

    # get file ID (index in csv)
    id = int(signalID.split('-')[1])

    # read file
    df = pd.read_csv(csv_file, sep=CSV_SEP, index_col=0)
    if variables is None:
        variables = DEFAUL_VARIABLES

    # parse variables
    for v in variables:
        out_dict[v] = df.loc[id, v]

    return out_dict


if __name__ == "__main__":
    ROOT_PATH = './data'
    VARIABLES_FILE = f'{ROOT_PATH}/shhs1-dataset-0.9.0.csv'
    signalID = 'shhs1-200001'
    VARIABLES = ['ahi_a0h3a', 'SlpPrdP']
    out_dict = parseVariables(VARIABLES_FILE,
                              signalID=signalID,
                              out_dict={
                                  'fileID': signalID,
                                  'error': False
                              },
                              variables=VARIABLES)
    pass
