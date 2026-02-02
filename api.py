from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        prompt = qs.get("prompt", [""])[0].strip()

        if not prompt:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"prompt is required")
            return

        image_url = (
            "https://image.pollinations.ai/prompt/"
            + quote(prompt)
            + "?nologo=true&quality=high"
        )

        # 🔥 Direct redirect to image
        self.send_response(302)
        self.send_header("Location", image_url)
        self.end_headers()
