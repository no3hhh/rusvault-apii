from http.server import BaseHTTPRequestHandler
import json, urllib.parse

from youtube_transcript_api import YouTubeTranscriptApi

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        self._cors()
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        video_id = params.get("v", [None])[0]
        lang = params.get("lang", ["ru"])[0]

        if not video_id or len(video_id) != 11:
            return self._json(400, {"ok": False, "error": "Invalid video ID"})

        try:
            result = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang, lang + "-auto"])
            text = " ".join([entry["text"] for entry in result]).strip()

            if len(text) < 10:
                return self._json(404, {"ok": False, "error": "Too short"})

            self._json(200, {"ok": True, "text": text, "length": len(text)})
        except Exception as e:
            self._json(500, {"ok": False, "error": str(e)})

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
