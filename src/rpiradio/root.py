import os
import sys

import cherrypy

current_module = sys.modules[__name__]
MOD_PATH = os.path.dirname(current_module.__file__)

class Root:

    def __init__(self, app_config):
        self.app_config = app_config

    @cherrypy.expose
    def index(self):
        return open(os.path.join(MOD_PATH, "static/index.html"))

    @cherrypy.expose
    def health(self):
        pass

    def _get_logfile_contents(self, log_path):
        if not os.path.isfile(log_path):
            return "log file does not exist at {}".format(log_path)
        with open(log_path, "r") as f:
            contents = f.readlines()
            return contents

    @cherrypy.expose
    def stdout(self):
        contents = self._get_logfile_contents(
            self.app_config["server"]["out_log_path"])
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        return contents

    @cherrypy.expose
    def stderr(self):
        contents = self._get_logfile_contents(
            self.app_config["server"]["err_log_path"])
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        return contents

    def static(self):
        pass

    static._cp_config = {
        "tools.staticdir.on": True,
        "tools.staticdir.dir": os.path.join(MOD_PATH, "static"),
        "tools.staticdir.index": "index.html"
    }
