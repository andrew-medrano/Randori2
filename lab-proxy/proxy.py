import base64
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


USERNAME = "operator"
PASSWORD = "windward"
ALLOWED_DESTINATIONS = {("lab-internal", 8081)}


class ProxyHandler(BaseHTTPRequestHandler):
    server_version = "RandoriPivotProxy/0.1"

    def do_GET(self):
        self.forward()

    def do_HEAD(self):
        self.forward()

    def do_CONNECT(self):
        self.respond_text(405, "CONNECT is disabled for this lab. Use HTTP proxy requests.\n")

    def forward(self):
        if not self.authorized():
            self.send_response(407)
            self.send_header("Proxy-Authenticate", 'Basic realm="Randori Pivot"')
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        parsed = urlsplit(self.path)
        if parsed.scheme != "http" or not parsed.hostname:
            self.respond_text(400, "Use an absolute http:// URL with this proxy.\n")
            return

        port = parsed.port or 80
        destination = (parsed.hostname, port)
        if destination not in ALLOWED_DESTINATIONS:
            self.respond_text(403, "Proxy destination is outside this lab segment.\n")
            return

        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"

        headers = {
            "Host": f"{parsed.hostname}:{port}",
            "User-Agent": self.headers.get("User-Agent", "randori-proxy"),
            "Accept": self.headers.get("Accept", "*/*"),
        }

        try:
            conn = http.client.HTTPConnection(parsed.hostname, port, timeout=5)
            conn.request(self.command, path, headers=headers)
            response = conn.getresponse()
            body = response.read()
        except OSError as exc:
            self.respond_text(502, f"Proxy upstream error: {exc}\n")
            return

        self.send_response(response.status, response.reason)
        blocked_headers = {
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",
            "te",
            "trailer",
            "transfer-encoding",
            "upgrade",
        }
        for name, value in response.getheaders():
            if name.lower() not in blocked_headers:
                self.send_header(name, value)
        self.send_header("Via", "1.1 randori-pivot")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def authorized(self):
        expected = "Basic " + base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
        return self.headers.get("Proxy-Authorization") == expected

    def respond_text(self, status, body):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 3128), ProxyHandler).serve_forever()
