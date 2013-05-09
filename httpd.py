import sys
sys.dont_write_bytecode = True

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import os.path


from tornado.options import define, options
define("port", default=80, help="run on givien port", type=int)

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r'/(.*)', tornado.web.StaticFileHandler, {'path': '.'}),
		]
		settings = dict(
		)
		tornado.web.Application.__init__(self, handlers, **settings)


if __name__ =="__main__":
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()

