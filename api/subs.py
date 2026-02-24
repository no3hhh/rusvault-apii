from http.server import BaseHTTPRequestHandler
import json, urllib.parse

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    LIB_OK = True
    LIB_ERR = ""
except Exception as e:
    LIB_OK = False
    LIB_ERR = str(e)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        if not LIB_OK:
            self.wfile.write(json.dumps({"ok": False, "error": "Import failed: " + LIB_ERR}).encode())
            return

        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        video_id = params.get("v", [None])[0]
        lang = params.get("lang", ["ru"])[0]

        if not video_id or len(video_id) != 11:
            self.wfile.write(json.dumps({"ok": False, "error": "Invalid video ID"}).encode())
            return

        try:
            ytt = YouTubeTranscriptApi()
            transcript = ytt.fetch(video_id, languages=[lang, lang + "-auto"])
            text = " ".join([snippet.text for snippet in transcript.snippets]).strip()
            self.wfile.write(json.dumps({"ok": True, "text": text, "length": len(text)}).encode())
        except Exception as e:
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.end_headers()
