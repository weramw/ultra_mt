#!/usr/bin/env python3
import sys
import requests
import json

# TODO accept/register cert once
# from OpenSSL.SSL import Context, Connection, SSLv23_METHOD
# from OpenSSL.SSL import VERIFY_PEER, VERIFY_FAIL_IF_NO_PEER_CERT, VERIFY_CLIENT_ONCE
#
# def verify_callback(connection, x509, errnum, errdepth, ok):
#     #if not ok:
#     #    print "Bad Certs"
#     #else:
#     #    print "Certs are fine"
#     return True
#     return ok
#
# ctx = Context(SSLv23_METHOD)
# ctx.set_verify( VERIFY_PEER | VERIFY_FAIL_IF_NO_PEER_CERT | VERIFY_CLIENT_ONCE, verify_callback )

class Light(object):
    def __init__(self, light_id, light_dict, hue):
        self.id = light_id
        for k, v in light_dict.items():
            setattr(self, k, v)
        self.hue = hue

    def update(self):
        light_return = self.hue._get_light_return(self.id)
        for k, v in light_return.items():
            setattr(self, k, v)

    def switch(self, on):
        self.hue._set_light(self.id, on)

    def __str__(self):
        ret = f"{self.name} ({self.id}) "
        ret += "ON" if self.state['on'] else "OFF"
        ret += " "
        ret += f"Brightness = {self.state['bri']}"
        ret += " "

        if 'colormode' not in self.state:
            return ret

        if self.state['colormode'] == 'ct':
            ret += f"Color Temperature = {self.state['ct']}"
        elif self.state['colormode'] == 'xy':
            ret += f"XY = {self.state['xy']}"
        else:
            ret += self.state['colormode']
        return ret

    def __repr__(self):
        return f"{self.name} ({self.id})"

class HueBridge(object):
    def __init__(self, ip, api_key):
        self.ip = ip
        self.api_key = api_key
        self.api_url = f"http://{self.ip}/api/{self.api_key}/"
        self.lights = self.get_lights()

    def get_light_by_name(self, name):
        for light in self.lights:
            if light.name == name:
                return light
        return None

    def get_lights(self):
        r = requests.get(self.api_url + "lights")
        lights_return = json.loads(r.text)
        lights = []
        for li, light_dict in lights_return.items():
            l = Light(li, light_dict, self)
            lights.append(l)
        return lights

    def _get_light_return(self, light_id):
        r = requests.get(f"{self.api_url}lights/{light_id}")
        lights = json.loads(r.text)
        return lights

    def _set_light(self, light_id, on):
        light_url = f"{self.api_url}lights/{light_id}/state"
        data = {"on": on}
        r = requests.put(light_url, json=data)

if __name__=="__main__":
    hue_ip = "192.168.0.87"
    api_key = "tNmBJLQdGdYBta51nzwU2PP8GfzuzFFBlup5h9c2"
    hue = HueBridge(hue_ip, api_key)
    lights = hue.get_lights()
    for l in lights:
        print(l)
    print()

    balkon = hue.get_light_by_name("Balkon")
    assert balkon is not None
    print(balkon)
    if len(sys.argv) > 1:
        on = sys.argv[1] == "1"
        balkon.switch(on)
        balkon.update()
        print(balkon)

