import cherrypy
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('app/web/templates'))

class WebApp:
    @cherrypy.expose
    def index(self):
        template = env.get_template('index.html')
        return template.render()

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8080})
    cherrypy.tree.mount(WebApp(), '/')
    cherrypy.engine.start()
    cherrypy.engine.block()
