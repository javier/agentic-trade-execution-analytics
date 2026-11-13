"""Tiny local receiver: the console page POSTs a notebook export, this writes it to disk."""
import http.server
import json
import os
import re
import sys

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)


class Handler(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        name = re.sub(r"[^A-Za-z0-9._-]", "_", self.path.strip("/")) or "notebook"
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        data = json.loads(body)
        path = os.path.join(OUT, name + ".json")
        with open(path, "w") as f:
            json.dump(data, f, indent=1, ensure_ascii=False)
        self.send_response(200)
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps({"saved": path, "bytes": len(body)}).encode())

    def log_message(self, *args):
        pass


http.server.HTTPServer(("127.0.0.1", 18765), Handler).serve_forever()
