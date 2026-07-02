from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


EDGE_FLAG = "FLAG{edge_backup_proxy_leak}"
PROXY_URL = "http://operator:windward@lab-proxy:3128"
INTERNAL_URL = "http://lab-internal:8081"


class Handler(BaseHTTPRequestHandler):
    server_version = "RandoriEdge/0.2"

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/":
            self.respond(
                200,
                "text/html; charset=utf-8",
                f"""<!doctype html>
<html>
  <head><title>Randori Edge Target</title></head>
  <body>
    <h1>Randori Edge Target</h1>
    <p>Authorized local edge target for the segmented lab.</p>
    <p>Status: edge services healthy. Internal asset routing is managed separately.</p>
  </body>
</html>
""",
            )
            return

        if path == "/robots.txt":
            self.respond(
                200,
                "text/plain; charset=utf-8",
                "User-agent: *\nDisallow: /backup/\nDisallow: /ops/\n",
            )
            return

        if path in ("/backup", "/backup/"):
            self.respond(
                200,
                "text/html; charset=utf-8",
                """<!doctype html>
<html>
  <head><title>Index of /backup/</title></head>
  <body>
    <h1>Index of /backup/</h1>
    <a href="/backup/config.bak">config.bak</a>
  </body>
</html>
""",
            )
            return

        if path == "/backup/config.bak":
            self.respond(
                200,
                "text/plain; charset=utf-8",
                "\n".join(
                    [
                        "app=randori-edge",
                        "db_host=localhost",
                        "db_user=lab",
                        "db_password=not-real",
                        f"proxy_url={PROXY_URL}",
                        f"internal_asset={INTERNAL_URL}",
                        "note=internal_asset is only reachable through the pivot proxy",
                        f"flag={EDGE_FLAG}",
                        "",
                    ]
                ),
            )
            return

        if path in ("/ops", "/ops/"):
            self.respond(
                200,
                "text/html; charset=utf-8",
                """<!doctype html>
<html>
  <head><title>Index of /ops/</title></head>
  <body>
    <h1>Index of /ops/</h1>
    <a href="/ops/proxy.env">proxy.env</a>
  </body>
</html>
""",
            )
            return

        if path == "/ops/proxy.env":
            self.respond(
                200,
                "text/plain; charset=utf-8",
                f"HTTP_PROXY={PROXY_URL}\nINTERNAL_TARGET={INTERNAL_URL}\n",
            )
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
        self.send_header("X-Randori-Lab", "true")
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
