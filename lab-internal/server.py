from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


INTERNAL_FLAG = "FLAG{internal_only_via_pivot_proxy}"


class Handler(BaseHTTPRequestHandler):
    server_version = "RandoriInternal/0.1"

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/":
            self.respond(
                200,
                "text/html; charset=utf-8",
                """<!doctype html>
<html>
  <head><title>Internal Accounts Console</title></head>
  <body>
    <h1>Internal Accounts Console</h1>
    <p>This service is bound to the private lab segment.</p>
  </body>
</html>
""",
            )
            return

        if path == "/robots.txt":
            self.respond(
                200,
                "text/plain; charset=utf-8",
                "User-agent: *\nDisallow: /admin/\n",
            )
            return

        if path in ("/admin", "/admin/"):
            self.respond(
                200,
                "text/html; charset=utf-8",
                """<!doctype html>
<html>
  <head><title>Index of /admin/</title></head>
  <body>
    <h1>Index of /admin/</h1>
    <a href="/admin/flag.txt">flag.txt</a>
  </body>
</html>
""",
            )
            return

        if path == "/admin/flag.txt":
            self.respond(200, "text/plain; charset=utf-8", f"{INTERNAL_FLAG}\n")
            return

        if path == "/healthz":
            self.respond(200, "text/plain; charset=utf-8", "ok\n")
            return

        self.respond(404, "text/plain; charset=utf-8", "not found\n")

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)

    def respond(self, status, content_type, body):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Randori-Internal", "true")
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8081), Handler).serve_forever()
