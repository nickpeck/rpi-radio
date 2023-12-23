import os
import sys

import cherrypy

current_module = sys.modules[__name__]
MOD_PATH = os.path.dirname(current_module.__file__)

class Root:

    @cherrypy.expose
    def index(self):
        return open(os.path.join(MOD_PATH, "static/index.html"))

    @cherrypy.expose
    def health(self):
        pass

    @cherrypy.expose
    def stdout(self):
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        log_path = "/var/log/radio.out.log"
        if not os.path.isfile(log_path):
            return "log file does not exist at {}".format(log_path)
        with open(log_path, "r") as f:
            contents = f.readlines()
            return contents

    @cherrypy.expose
    def stderr(self):
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        log_path = "/var/log/radio.err.log"
        if not os.path.isfile(log_path):
            return "log file does not exist at {}".format(log_path)
        with open(log_path, "r") as f:
            contents = f.readlines()
            return contents

    def static(self):
        pass

    static._cp_config = {
        "tools.staticdir.on": True,
        "tools.staticdir.dir": os.path.join(MOD_PATH, "static"),
        "tools.staticdir.index": "index.html"
    }
