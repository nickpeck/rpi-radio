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

class Station:

    def __init__(self, db):
        self.db = db

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        all_stations = self.db.search(Query().name.exists())
        return all_stations

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def create(self):
        payload = cherrypy.request.json
        for key in ["name", "url"]:
            if key not in payload:
                cherrypy.response.status = 400
                return {"error": f"missing required attribute {key}"}
            if not payload[key]:
                cherrypy.response.status = 400
                return {"error": f"{key} cannot be empty"}
        if len(str(payload['name'])) > 50:
            cherrypy.response.status = 400
            return {"error": f"name should be < 50 characters"}
        if not validators.url(payload['url']):
            cherrypy.response.status = 400
            return {"error": f"url invalid"}
        station = {
            "uid": str(uuid.uuid4()),
            "name": str(payload['name']),
            "url": str(payload['url'])}
        with transaction(self.db) as tr:
            self.db.insert(station)
            cherrypy.response.status = 201

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def delete(self):
        payload = cherrypy.request.json
        uid = payload['uid']
        with transaction(self.db) as tr:
            self.db.remove(where('uid') == uid)
