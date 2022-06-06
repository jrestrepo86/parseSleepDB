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


def getEvents(xml_data, signal_length, out_dict, respEventsMap):
    # read events all events in xml
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
    out_dict[targetName] = target
    return out_dict


def parseRespEvents(xml_path,
                    fname,
                    signal_length,
                    out_dict,
                    respEventsMap=None):

    # read xml
    fname = f'{xml_path}/{fname}-nsrr.xml'
    xml_data = pdx.read_xml(fname, XML_STRUC).iloc[0]
    # parse all target maps
    for map in respEventsMap:
        out_dict = getEvents(xml_data, signal_length, out_dict, map)
    return out_dict


if __name__ == "__main__":
    ROOT_PATH = './data'
    NSRR_EVENTS_PATH = f'{ROOT_PATH}/annotations-events-nsrr/shhs1'
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
            '1':
            ['Hypopnea', 'Obstructive apnea', 'Central Apnea', 'Mixed Apnea'],
        },
    }

    out_dict = parseRespEvents(
        NSRR_EVENTS_PATH,
        fname='shhs1-200001',
        signal_length=32520,
        out_dict={},
        respEventsMap=[RESP_EVENTS_MAP_T1, RESP_EVENTS_MAP_T2, None])
    pass
