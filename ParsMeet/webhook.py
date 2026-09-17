import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class WebhookHandler(BaseHTTPRequestHandler):
    bot = None
    secret = None

    def log_message(self, format, *args):
        return

    def do_POST(self):
        if self.secret and self.headers.get("X-Webhook-Secret") != self.secret:
            self.send_response(403)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            update = json.loads(body)
            self.bot._process_update(update)
        except Exception as e:
            print(f"Webhook error: {e}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

class WebhookServer:
    def __init__(self, bot, port=8443, path="/webhook", secret=None):
        self.bot = bot
        self.port = port
        self.path = path
        self.secret = secret
        self._server = None

    def start(self):
        WebhookHandler.bot = self.bot
        WebhookHandler.secret = self.secret
        self._server = HTTPServer(("0.0.0.0", self.port), WebhookHandler)
        thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        thread.start()
        print(f"Webhook listening on port {self.port}{self.path}")

    def stop(self):
        if self._server:
            self._server.shutdown()