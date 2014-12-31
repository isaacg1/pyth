#!/usr/bin/env python3
from http.server import HTTPServer, CGIHTTPRequestHandler
import sys

class Handler(CGIHTTPRequestHandler):
    cgi_directories = ["/"]

PORT = int(sys.argv[1])

httpd = HTTPServer(("", PORT), Handler)
print("serving at port", PORT)
httpd.serve_forever()

