from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests, urllib.parse, base64, json

# ================= CONFIG =================
import os
API_KEY = os.getenv("IMG_API_KEY") or "MYSECRET123"  # Use Vercel env var or fallback
# Unlimited, so no daily limit

# ================= ENGINES =================

def flux(prompt):
    try:
        url = f"https://fluximg.rydenxgod.workers.dev/?prompt={urllib.parse.quote(prompt)}&size=1024x1024&n=1"
        r = requests.get(url, timeout=60)
        data = r.json()
        if data.get("code") == 0:
            return data["data"]["images"][0]["url"]
    except:
        pass
    return None

def bj(prompt):
    try:
        url = f"https://text-to-img.apis-bj-devs.workers.dev/?prompt={urllib.parse.quote(prompt)}"
        r = requests.get(url, timeout=60)
        data = r.json()
        return data.get("result", [])
    except:
        return []

def pollinations(prompt):
    return f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?nologo=true"

def download(url):
    r = requests.get(url, timeout=60)
    return r.content if r.status_code == 200 else None

# ================= HANDLER =================

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)

        prompt = qs.get("prompt", [None])[0]
        key = qs.get("key", [None])[0]
        engine = qs.get("engine", ["flux"])[0]      # flux | bj | pollinations | all
        fmt = qs.get("format", ["image"])[0]        # image | json | base64

        # ---------- AUTH ----------
        if key != API_KEY:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b"Invalid API key")
            return

        if not prompt or len(prompt) < 3:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Prompt required (min 3 chars)")
            return

        # ---------- GENERATE ----------
        urls = []

        if engine in ("flux", "all"):
            u = flux(prompt)
            if u:
                urls.append(u)

        if engine in ("bj", "all"):
            urls.extend(bj(prompt))

        if engine in ("pollinations", "all"):
            urls.append(pollinations(prompt))

        if not urls:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Image generation failed")
            return

        # ---------- DIRECT IMAGE ----------
        if fmt == "image":
            img = download(urls[0])
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.end_headers()
            self.wfile.write(img)
            return

        # ---------- BASE64 ----------
        if fmt == "base64":
            img = download(urls[0])
            b64 = base64.b64encode(img).decode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b64.encode())
            return

        # ---------- JSON ----------
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "success",
            "prompt": prompt,
            "engine": engine,
            "total_images": len(urls),
            "images": urls
        }).encode())
