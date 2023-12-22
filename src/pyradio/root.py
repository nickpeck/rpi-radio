import cherrypy

class Root:
    @cherrypy.expose
    def index(self):
        return open("/usr/src/app/pyradio/static/index.html")

    @cherrypy.expose
    def health(self):
        pass

    def static(self):
        pass

    static._cp_config = {
        "tools.staticdir.on": True,
        "tools.staticdir.dir": "/usr/src/app/pyradio/static",
        "tools.staticdir.index": "index.html"
    }
