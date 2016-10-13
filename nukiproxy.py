#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Ben Jones <ben.jones12()gmail.com>'
__copyright__ = 'Copyright 2016 Ben Jones'

# wget http://bottlepy.org/bottle.py
# ... or ... pip install bottle
from bottle import get, post, put, request, run, response, abort
import os
import sys
import ConfigParser
import json
import time
import re
import requests


# Script name (without extension) used for config/logfile names
APPNAME = os.path.splitext(os.path.basename(__file__))[0]
INIFILE = os.getenv('INIFILE', APPNAME + '.ini')

# Read the config file
config = ConfigParser.RawConfigParser()
config.read(INIFILE)

# Use ConfigParser to pick out the settings
DEBUG = config.getboolean("global", "DEBUG")

NUKIPROXY_HOST = config.get("nukiproxy", "NUKIPROXY_HOST")
NUKIPROXY_PORT = config.getint("nukiproxy", "NUKIPROXY_PORT")
NUKIPROXY_ENDPOINT = config.get("nukiproxy", "NUKIPROXY_ENDPOINT")

OPENHAB_HOST = config.get("openhab", "OPENHAB_HOST")
OPENHAB_PORT = config.getint("openhab", "OPENHAB_PORT")
OPENHAB_USER = config.get("openhab", "OPENHAB_USER")
OPENHAB_PASSWORD = config.get("openhab", "OPENHAB_PASSWORD")

OPENHAB_ITEM_LOCKED = config.get("openhab", "OPENHAB_ITEM_LOCKED")
OPENHAB_ITEM_STATE = config.get("openhab", "OPENHAB_ITEM_STATE")
OPENHAB_ITEM_STATENAME = config.get("openhab", "OPENHAB_ITEM_STATENAME")
OPENHAB_ITEM_BATTERYCRITICAL = config.get("openhab", "OPENHAB_ITEM_BATTERYCRITICAL")


def update_openhab(item, value):
    url = 'http://%s:%s@%s:%d/rest/items/%s/state' % (OPENHAB_USER, OPENHAB_PASSWORD, OPENHAB_HOST, OPENHAB_PORT, item)
    headers = { 'Content-Type': 'text/plain' }
    requests.put(url, headers=headers, data=value)

@get('/')
def monitor():
    response.status = 200
    return

@post(NUKIPROXY_ENDPOINT)
def proxy():
    '''Nuki bridge callback - called whenever the Nuki lock changes state
       Sends a JSON POST to the configured callback URL in the form'
         {"nukiId": 11, "state": 1, "stateName": "locked", "batteryCritical": false}
       '''
    try:
        try:
            data = request.json
        except:
            raise ValueError

        if data is None:
            raise ValueError

        nukiId = data['nukiId']
        state = data['state']
        stateName = data['stateName']
        batteryCritical = data['batteryCritical']

        if state == 1:
            update_openhab(OPENHAB_ITEM_LOCKED, 'CLOSED')
        else:
            update_openhab(OPENHAB_ITEM_LOCKED, 'OPEN')

        update_openhab(OPENHAB_ITEM_STATE, str(state))
        update_openhab(OPENHAB_ITEM_STATENAME, stateName)

        if batteryCritical:
            update_openhab(OPENHAB_ITEM_BATTERYCRITICAL, 'ON')
        else:
            update_openhab(OPENHAB_ITEM_BATTERYCRITICAL, 'OFF')

    except ValueError:
        response.status = 400
        return

    response.state = 200
    return


if __name__ == '__main__':

    try:
        run(host=NUKIPROXY_HOST, port=NUKIPROXY_PORT, debug=DEBUG)
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        raise
