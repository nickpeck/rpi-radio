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
from . monitor import Monitor

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root_logger.addHandler(handler)

app_config_defaults = {
    "login": "secret",
    "out_log_path": "/var/log/radio.out.log",
    "err_log_path": "/var/log/radio.err.log",
    "socket_host": "0.0.0.0",
    "socket_port": 8080,
    "db_path": os.path.join(os.getcwd(), "database/db.json"),
    "play_on_start": True,
    "restart_monitor_on": True,
}

app_config = configparser.ConfigParser()
app_config.read('rpi-radio.ini')
app_config["DEFAULT"] = app_config_defaults

cherrypy.server.socket_host = app_config["server"]["socket_host"]
cherrypy.server.socket_port = app_config.getint("server", "socket_port")
cp_conf = {
    '/': {
        'tools.auth_digest.on': True,
        'tools.auth_digest.realm': 'localhost',
        'tools.auth_digest.get_ha1': auth_digest.get_ha1_dict_plain({
            "admin": app_config["server"]["login"]}),
        'tools.auth_digest.key': secrets.token_hex(),
        'tools.auth_digest.accept_charset': 'UTF-8',
    }
}

db_path = app_config["server"]["db_path"]

def do_exit(*args):
    root_logger.info("Shutdown signal recieved, stopping server")
    cherrypy.engine.exit()

signal.signal(signal.SIGINT, do_exit)
signal.signal(signal.SIGTERM, do_exit)

if not os.path.isfile(db_path):
    db = TinyDB(db_path)
    with transaction(db) as tr:
        db.insert({
            "state": "stopped",
            "current_station": None })
else:
    db = TinyDB(db_path)

player_instance = Player(db, app_config)

cherrypy.tree.mount(Root(app_config), "/", cp_conf)
cherrypy.tree.mount(player_instance, "/api/player", cp_conf)
cherrypy.tree.mount(Station(db), "/api/station", cp_conf)

if app_config.getboolean("server", "restart_monitor_on"):
    monitor = Monitor(player_instance)
    monitor.setDaemon(True)   
    monitor.start()

cherrypy.engine.start()
cherrypy.engine.block()
