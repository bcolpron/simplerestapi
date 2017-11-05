#!/usr/bin/env python
from simplerestapi import SimpleRestApi

def get_builds(matchedUrl, data):
    return {"builds": [1,2,3]}

def set_build(matchedUrl, data):
    print "build: " + str(data)

api = SimpleRestApi(8000)
api.add("get", "/builds", get_builds)
api.add("put", "/builds", set_build)
api.run_forever()
