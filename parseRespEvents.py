#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SLEEP DATABASE PARSE
parse respiratory events
"""

import numpy as np
import pandas_read_xml as pdx
from matplotlib.pyplot import plot

# structure in xml file
XML_STRUC = ['PSGAnnotation', 'ScoredEvents', 'ScoredEvent']
RESP_EVENTS_MAP_DEFAULT = {
    'targetName': 'respEventsDefaultTarget',
    'map': {
        '1': ['Hypopnea'],
        '2': ['Obstructive apnea'],
        '3': ['Central Apnea'],
        '4': ['Mixed Apnea'],
    },
}
DESATURATION_MARK_OFFSET = 30


def getDesaturation(xml_data, signal_length, desat_item):

    eventType = desat_item['event']
    threshold = desat_item['th']

    # get SpO2 desaturaion events in xml
    desaturation = np.zeros(signal_length)
    event = np.zeros(signal_length)
    for i in range(xml_data.size):
        b = xml_data.iloc[i]
        if 'SpO2 desaturation' in b['EventConcept']:
            SpO2Nadir = float(b['SpO2Nadir'])
            SpO2Baseline = float(b['SpO2Baseline'])
            if np.abs(SpO2Baseline - SpO2Nadir) >= threshold:
                start = int(np.round(float(b['Start'])))
                stop = int(np.round(float(b['Start']) + float(b['Duration'])))
                desaturation[start:stop] = 1
        if eventType in b['EventConcept']:
            start = int(np.round(float(b['Start'])))
            stop = int(np.round(float(b['Start']) + float(b['Duration'])))
            event[start:stop] = 1

    # match desaturation
    desaturation = np.roll(desaturation, -DESATURATION_MARK_OFFSET)
    desaturation[-DESATURATION_MARK_OFFSET:] = 0

    return desaturation * event


def getEvents(xml_data, signal_length, out_dict, respEventsMap):

    desat_filt = {}
    if 'SpO2 desaturation' in respEventsMap:
        for desat_item in respEventsMap['SpO2 desaturation']:
            dfilt = getDesaturation(xml_data, signal_length, desat_item)
            desat_filt.update({desat_item['event']: dfilt})

    # read all events in xml
    xml_events = []
    for i in range(xml_data.size):
        b = xml_data.iloc[i]
        xml_events.append(
            (b['EventConcept'], float(b['Start']), float(b['Duration'])))

    # map respiratory events
    target = np.zeros(signal_length)
    if respEventsMap is None:
        respEventsMap = RESP_EVENTS_MAP_DEFAULT

    targetName = respEventsMap['targetName']
    for map, vals in respEventsMap['map'].items():
        for (ev_type, ev_start, ev_duration) in xml_events:
            if any(s in ev_type for s in vals):
                start = int(np.round(ev_start))
                stop = int(np.round(ev_start + ev_duration))
                target[start:stop] = int(map)
    # filtrar según desaturación, (se podría optimizar en el gfor de arriba, pero lo
    # dejo para debugeo fácil)
    filter = np.zeros_like(target)
    for filt in desat_filt.values():
        filter = filter + filt
    filter = filter > 0
    out_dict[targetName] = target * filter
    return out_dict


def parseRespEvents(xml_path,
                    fname,
                    signal_length,
                    out_dict,
                    respEventsMaps=None):

    out_dict['respEventTargetMaps'] = [str(map) for map in respEventsMaps]
    # read xml
    fname = f'{xml_path}/{fname}-nsrr.xml'
    xml_data = pdx.read_xml(fname, XML_STRUC).iloc[0]
    # parse all target maps
    for map in respEventsMaps:
        out_dict = getEvents(xml_data, signal_length, out_dict, map)
    return out_dict


if __name__ == "__main__":
    ROOT_PATH = './data'
    NSRR_EVENTS_PATH = f'{ROOT_PATH}/annotations-events-nsrr/shhs1'
    RESP_EVENTS_MAP_T1 = {
        'targetName':
        'targetAH',
        'map': {
            '1': ['Hypopnea'],
            '2': ['Obstructive apnea', 'Central Apnea', 'Mixed Apnea'],
        },
        'SpO2 desaturation': [
            {
                'event': 'Hypopnea',
                'th': 4.0
            },
            {
                'event': 'Obstructive apnea',
                'th': 0.0
            },
            {
                'event': 'Central apnea',
                'th': 0.0
            },
            {
                'event': 'Mixed apnea',
                'th': 0.0
            },
        ],
    }

    # RESP_EVENTS_MAP_T2 = {
    #     'targetName': 'targetA',
    #     'map': {
    #         '1':
    #         ['Hypopnea', 'Obstructive apnea', 'Central Apnea', 'Mixed Apnea'],
    #     },
    #     'SpO2 desaturation':{'calculate':True, 'threshold':3.0},
    # }
    fname = 'shhs1-203535'
    out_dict = parseRespEvents(NSRR_EVENTS_PATH,
                               fname=fname,
                               signal_length=32520,
                               out_dict={
                                   'fileID': fname,
                                   'error': False
                               },
                               respEventsMaps=[RESP_EVENTS_MAP_T1])
