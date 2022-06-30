#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PARSE SLEEP DATABASE

Parse variables from [shhs1-dataset-0.90.0.csv, shhs2-dataset-0.90.0.csv]
Variables can be seen in: https://sleepdata.org/datasets/shhs/variables
"""

import numpy as np
import pandas as pd

CSV_SEP = ','
VARIABLES = [
    'HREMBP', 'HROP', 'HNRBP', 'HNROP', 'HREMBP3', 'HROP3', 'HNRBP3', 'HNROP3',
    'HREMBP4', 'HROP4', 'HNRBP4', 'HNROP4', 'CARBP', 'CAROP', 'CANBP', 'CANOP',
    'OARBP', 'OAROP', 'OANBP', 'OANOP', 'ahi_a0h4', 'ahi_a0h3', 'SlpPrdP'
]


def buildVariablesFile(csv_file, signalID, df_in, calc_vars):

    new_row = calc_vars.copy()
    new_row['fileName'] = signalID

    # get file ID (index in csv)
    id = int(signalID.split('-')[1])

    # read file
    df = pd.read_csv(csv_file, sep=CSV_SEP, index_col=0)
    # parse variables
    for v in VARIABLES:
        new_row[v] = df.loc[id, v]

    df_in = pd.concat([df_in, pd.DataFrame([new_row])],
                      axis=0,
                      ignore_index=True)

    return df_in
