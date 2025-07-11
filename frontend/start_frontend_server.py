import http.server
import socketserver
import os

PORT = 8080
WEB_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(WEB_DIR)

Handler = http.server.SimpleHTTPRequestHandler

print(f"Serving frontend at http://localhost:{PORT}")
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.") 