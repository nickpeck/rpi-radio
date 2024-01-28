import os
import json
import signal
import uuid
from subprocess import Popen, PIPE

import cherrypy
from cherrypy.lib import auth_digest
from tinydb import TinyDB, Query, where
from tinydb.operations import delete
from tinyrecord import transaction
import validators

class Player:
    _proc = None

    def __init__(self, db, app_config):
        self.db = db
        self.app_config = app_config
        player = self.db.search(Query().current_station.exists())[0]
        current_station = self.get_current_station()
        if len(current_station) and app_config.getboolean("server", 'play_on_start'):
            self.play(current_station[0]['url'])

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        player = self.db.search(Query().current_station.exists())[0]
        player['state'] = 'stopped'
        if Player._proc is not None:
            player['state'] = "playing"
        player["login"] = cherrypy.request.login
        return player

    def get_current_station(self):
        player = self.db.search(Query().current_station.exists())[0]
        return self.db.search(Query().uid == player['current_station'])

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def update(self):
        payload = cherrypy.request.json
        old_state = self.db.search(Query().current_station.exists())[0]
        new_state = old_state.copy()
        new_state.update(payload)
        with transaction(self.db) as tr:
            self.db.update(
                new_state,
                Query().current_station.exists())
        if new_state["state"] == "playing":
            if old_state["state"] == "playing" and old_state["current_station"] == new_state["current_station"]:
                return new_state
            current_station = self.db.search(
                Query().uid == new_state['current_station'])[0]
            self.stop()
            self.play(current_station["url"])
        elif new_state["state"] == "stopped":
            self.stop()
        return new_state

    def play(self, url):
        Player._proc = Popen(["mplayer", url])

    def stop(self):
        if Player._proc is not None:
            Player._proc.kill()
            Player._proc = None
