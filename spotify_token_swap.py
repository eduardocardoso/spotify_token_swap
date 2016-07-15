import cherrypy
from cherrypy import tools
import simplejson as json
import requests
import os
import base64

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
CALLBACK_URL = os.environ.get('CALLBACK_URL')

SPOTIFY_TOKEN_URL = os.environ.get('SPOTIFY_TOKEN_URL', 'https://accounts.spotify.com/api/token')

AUTH_HEADER = 'Basic %s' % base64.b64encode('%s:%s' % (CLIENT_ID, CLIENT_SECRET))

class SpotifyTokenSwap(object):
    @cherrypy.expose
    @tools.json_out()
    def swap(self, code=None):
        headers = {
            'Authorization': AUTH_HEADER
        }
        params = {
            'grant_type': 'authorization_code',
            'redirect_uri': CALLBACK_URL,
            'code' : code
        }
        r = requests.post(SPOTIFY_TOKEN_URL, params, headers=headers)
        cherrypy.response.status = r.status_code

        return r.json()

    @cherrypy.expose
    @tools.json_out
    def refresh(self, refresh_token=None):
        headers = {
            'Authorization': AUTH_HEADER
        }
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        r = requests.post(SPOTIFY_TOKEN_URL, params, headers=headers)
        cherrypy.response.status = r.status_code

        return r.json()

def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*" 


if __name__ == '__main__':
    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)
    root = SpotifyTokenSwap()

    config = {
        'global' : {
            'server.socket_host' : '0.0.0.0',
            'server.socket_port' : 9020,
            'server.thread_pool' : 10,
            'environment' : ENVIRONMENT,
        },
        '/' : {
            'tools.CORS.on' : True,
        }
    }
    cherrypy.quickstart(root, '/', config=config)
