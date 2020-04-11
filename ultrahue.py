#!/usr/bin/env python3
import requests
import json
from OpenSSL.SSL import Context, Connection, SSLv23_METHOD
from OpenSSL.SSL import VERIFY_PEER, VERIFY_FAIL_IF_NO_PEER_CERT, VERIFY_CLIENT_ONCE

def verify_callback(connection, x509, errnum, errdepth, ok):
    #if not ok:
    #    print "Bad Certs"
    #else:
    #    print "Certs are fine"
    return True
    return ok

ctx = Context(SSLv23_METHOD)
ctx.set_verify( VERIFY_PEER | VERIFY_FAIL_IF_NO_PEER_CERT | VERIFY_CLIENT_ONCE, verify_callback )

class HueBridge(object):
    def __init__(self, ip, api_key):
        self.ip = ip
        self.api_key = api_key
        self.api_url = f"http://{self.ip}/api/{self.api_key}/"

    def get_lights(self):
        r = requests.get(self.api_url + "lights")
        lights = json.loads(r.text)
        return lights

if __name__=="__main__":
    hue_ip = "192.168.0.87"
    api_key = ""
    hue = HueBridge(hue_ip, api_key)
    lights = hue.get_lights()
    print(lights)



