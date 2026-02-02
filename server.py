from http.server import HTTPServer
from api import handler

PORT = 7000

httpd = HTTPServer(("0.0.0.0", PORT), handler)
print(f"🚀 Server running on http://127.0.0.1:{PORT}")
httpd.serve_forever()
