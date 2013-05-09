import string, cgi, time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import threading
from SocketServer import ThreadingMixIn

class ThreadedHttpServer(ThreadingMixIn, HTTPServer):
	pass

class HTTPHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		try:
			if self.path.endswith(".html"):
				f = open(curdir + sep + self.path)
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
				return
			if self.path.endswith(".png"):
				f = open(curdir + sep + self.path)
				self.send_response(200)
				self.send_header('Content-type', 'image/png')
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
				return
			if self.path.endswith(".jpg"):
				f = open(curdir + sep + self.path)
				self.send_response(200)
				self.send_header('Content-type', 'image/jpg')
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
				return
			if self.path.endswith(".js"):
				f = open(curdir + sep + self.path)
				self.send_response(200)
				self.send_header('Content-type', 'text/javascript')
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
				return

		except IOError:
			self.send_error(404, "File Not Found: %s" % self.path)

	def do_POST(self):
		global rootnode
		try:
			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			if ctype == 'multipart/form-data':
				query = cgi.parse_multipart(self.rfile, pdict)
			self.send_response(301)

			self.end_headers()
			upfilecontent = query.get('upfile')
			print "filecontent", upfilecontent[0]
			self.wfile.write("<HTML>POST OK.<BR><BR>")
			self.wfile.write(upfilecontent[0])

		except:
			pass

def main():
	try:
		server = ThreadedHttpServer(('', 80), HTTPHandler)
#		server = HTTPServer(('', 80), HTTPHandler)
		print 'started httpserver...'
		server.serve_forever()
	except KeyboardInterrupt:
		print "Ctrl+C received, shutting down server"
		server.socket.close()

if __name__ == '__main__':
	main()

