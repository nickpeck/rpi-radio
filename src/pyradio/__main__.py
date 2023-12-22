import configparser
import os
import json
import logging
import signal
import uuid
import sys
import secrets
from subprocess import Popen, PIPE

import cherrypy
from cherrypy.lib import auth_digest
from tinydb import TinyDB, Query, where
from tinydb.operations import delete
from tinyrecord import transaction
import validators

from . root import Root
from . player import Player
from . station import Station

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root_logger.addHandler(handler)

config = {
    "server": {
        "login": "secret"
    }
}

config = configparser.ConfigParser()
config.read('rpi-radio.ini')
try:
    login = config.sections()['server']['login']
except (TypeError, KeyError):
    login = config['server']['login']

cherrypy.server.socket_host = "0.0.0.0"
cherrypy.server.socket_port = 8080
cp_conf = {
    '/': {
        'tools.auth_digest.on': True,
        'tools.auth_digest.realm': 'localhost',
        'tools.auth_digest.get_ha1': auth_digest.get_ha1_dict_plain({"admin": login}),
        'tools.auth_digest.key': secrets.token_hex(),
        'tools.auth_digest.accept_charset': 'UTF-8',
    }
}
DB_PATH = '/usr/src/app/database/db.json';

def do_exit(*args):
    root_logger.info("Shutdown signal recieved, stopping server")
    cherrypy.engine.exit()

signal.signal(signal.SIGINT, do_exit)
signal.signal(signal.SIGTERM, do_exit)

if not os.path.isfile(DB_PATH):
    db = TinyDB(DB_PATH)
    with transaction(db) as tr:
        db.insert({"state": "stopped", "current_station": None, "play_on_start": True})
else:
    db = TinyDB(DB_PATH)

cherrypy.tree.mount(Root(), "/", cp_conf)
cherrypy.tree.mount(Player(db), "/api/player", cp_conf)
cherrypy.tree.mount(Station(db), "/api/station", cp_conf)
cherrypy.engine.start()
cherrypy.engine.block()
