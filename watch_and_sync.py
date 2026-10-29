# Auto YouTube Auth Watcher
import os, sys, time, glob, json, urllib.request, urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess

PORT = 8080
auth_code = None

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if 'code' in query:
            auth_code = query['code'][0]
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'<h1>Success! YouTube Shorts Authorized.</h1><p>You can close this tab now.</p>')
        else:
            self.send_response(400)
            self.end_headers()
    def log_message(self, *args): pass

print('Watcher script ready')
