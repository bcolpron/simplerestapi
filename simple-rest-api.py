#!/usr/bin/env python
import sqlite3
import json
import re
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class Registry:
    class NotFound(Exception):
        pass

    def __init__(self):
        self.handlers = [];

    def add(self, method, urlRegex, func):
        self.handlers.append((method, re.compile("^" + urlRegex + "$"), func))

    def get(self, method, url):
        for entry in self.handlers:
            if method == entry[0]:
                m = entry[1].match(url)
                if m:
                    return (m, entry[2])
        else:
            raise Registry.NotFound("no match for {} of {}".format(method, url))

def get_builds(matchedUrl, data):
    return {"builds": [1,2,3]}

def set_build(matchedUrl, data):
    print "data: " + str(data)

class Handler(BaseHTTPRequestHandler):
    def __init__(self, registry, *args):
        self.registry = registry
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_send_response(self, code, body):
        self.send_response(code)
        if body:
            self.send_header("Content-type", "application/json")
        self.end_headers()
        if body:
            self.wfile.write(json.dumps(body))

    def get_request_body(self):
        data = self.rfile.read(int(self.headers.getheader('content-length') or 0))
        return json.loads(data) if data else None

    def do_GET(self):
        try:
            (matchResult, handler) = self.registry.get("get", self.path)
            self.do_send_response(200, json.dumps(handler(matchResult, self.get_request_body())))
        except Registry.NotFound as e:
            self.do_send_response(404, e.message)
        except Exception as e:
            self.do_send_response(500, e.message)

    def do_PUT(self):
        try:
            (matchResult, handler) = self.registry.get("put", self.path)
            handler(matchResult, self.get_request_body())
            self.do_send_response(204, None)
        except Registry.NotFound as e:
            self.do_send_response(404, e.message)
        except Exception as e:
            self.do_send_response(500, e.message)


class SimpleRestApi:
    def __init__(self, port):
        self.registry = Registry()
        Handler.registry = self.registry
        server_address = ('', port)

        def handler(*args):
            Handler(self.registry, *args)

        self.httpd = HTTPServer(server_address, handler)
    
    def run_forever(self):
        self.httpd.serve_forever()

    def add(self, *args):
        self.registry.add(*args)

def run():
    api = SimpleRestApi(8000)
    api.add("get", "/builds", get_builds)
    api.add("put", "/builds", set_build)
    api.run_forever()


if __name__ == "__main__":
    run()