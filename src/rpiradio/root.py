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

    def static(self):
        pass

    static._cp_config = {
        "tools.staticdir.on": True,
        "tools.staticdir.dir": os.path.join(MOD_PATH, "static"),
        "tools.staticdir.index": "index.html"
    }
