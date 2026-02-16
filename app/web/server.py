#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 80

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Server", "Apache/2.4.49 (Ubuntu)")
        super().end_headers()

Handler = CustomHandler

os.chdir(os.path.join(os.path.dirname(__file__), "www"))

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Serving lab on port {PORT}")
    httpd.serve_forever()
