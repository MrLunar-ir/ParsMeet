import threading
import time
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

class DashboardHandler(BaseHTTPRequestHandler):
    bot = None

    def log_message(self, format, *args):
        return

    def do_GET(self):
        if self.path == "/api/stats":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            bot = self.bot
            data = {
                "status": "online",
                "uptime": int(time.time() - bot._started_at),
                "users": len(bot.db.get_all_chat_ids()),
                "ai_provider": bot.ai.provider_name,
                "plugins": bot.plugins.list_plugins(),
                "paused": bot._paused
            }
            self.wfile.write(json.dumps(data).encode("utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = """<!DOCTYPE html><html><head><title>ParsMeet Dashboard</title>
<style>body{font-family:sans-serif;background:#1e1e2e;color:#cdd6f4;padding:40px}
h1{color:#6c5ce7}.card{background:#2d2d3f;padding:20px;border-radius:10px;margin:15px 0}
.value{font-size:2em;color:#a6e3a1}</style></head><body>
<h1>ParsMeet Dashboard</h1>
<div class="card"><div>Status</div><div class="value" id="status">-</div></div>
<div class="card"><div>Uptime</div><div class="value" id="uptime">-</div></div>
<div class="card"><div>Users</div><div class="value" id="users">-</div></div>
<div class="card"><div>AI</div><div class="value" id="ai">-</div></div>
<div class="card"><div>Plugins</div><div class="value" id="plugins">-</div></div>
<script>
async function u(){const r=await fetch('/api/stats');const d=await r.json();
document.getElementById('status').textContent=d.status;
document.getElementById('uptime').textContent=d.uptime;
document.getElementById('users').textContent=d.users;
document.getElementById('ai').textContent=d.ai_provider;
document.getElementById('plugins').textContent=d.plugins.join(', ')||'none';}
setInterval(u,2000);u();</script></body></html>"""
            self.wfile.write(html.encode("utf-8"))

def start_dashboard(bot, port=8080):
    DashboardHandler.bot = bot
    server = HTTPServer(("0.0.0.0", port), DashboardHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"Dashboard: http://localhost:{port}")
    return server