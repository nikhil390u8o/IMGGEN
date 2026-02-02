from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote
import json

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        prompt = qs.get("prompt", [""])[0].strip()

        if not prompt:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "prompt is required"
            }).encode())
            return

        # Pollinations direct image URL (FAST + UNLIMITED)
        image_url = (
            "https://image.pollinations.ai/prompt/"
            + quote(prompt)
            + "?nologo=true&quality=high"
        )

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        self.wfile.write(json.dumps({
            "status": "success",
            "prompt": prompt,
            "image": image_url
        }).encode())
