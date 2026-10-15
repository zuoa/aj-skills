"""Loopback-only confirmation UI; no document generation or model access."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import secrets
from urllib.parse import urlsplit
import webbrowser

from report_workflow import load, save, session_path, update_session

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "supplement"


def make_server(workdir, period, port=0):
    path = session_path(workdir, period)
    if not path.exists():
        raise ValueError("请先运行 prepare 建立本期会话")
    token = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, status, body, content_type="application/json; charset=utf-8"):
            if not isinstance(body, bytes):
                body = json.dumps(body, ensure_ascii=False, allow_nan=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(body)

        def allowed_host(self):
            return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

        def authorized(self):
            return self.allowed_host() and secrets.compare_digest(self.headers.get("X-Session-Token", ""), token)

        def do_GET(self):
            if not self.allowed_host():
                return self.send(403, {"error": "无效访问地址"})
            route = urlsplit(self.path).path
            if route == "/api/session":
                if not self.authorized():
                    return self.send(403, {"error": "请使用启动时显示的完整链接"})
                return self.send(200, load(path))
            names = {"/": "index.html", "/app.js": "app.js", "/style.css": "style.css"}
            if route not in names:
                return self.send(404, {"error": "页面不存在"})
            mime = {"/": "text/html", "/app.js": "text/javascript", "/style.css": "text/css"}[route]
            self.send(200, (ASSETS / names[route]).read_bytes(), mime + "; charset=utf-8")

        def do_POST(self):
            if not self.authorized():
                return self.send(403, {"error": "会话验证失败，请重新打开完整链接"})
            origin = self.headers.get("Origin")
            if origin and origin != f"http://127.0.0.1:{self.server.server_port}":
                return self.send(403, {"error": "不接受跨站提交"})
            route = urlsplit(self.path).path
            if route not in ("/api/draft", "/api/submit"):
                return self.send(404, {"error": "接口不存在"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 2_000_000:
                    raise ValueError("请求为空或超过 2 MB")
                if self.headers.get_content_type() != "application/json":
                    raise ValueError("请求须为 JSON")
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError("请求须为对象")
                result = update_session(workdir, period, payload, submit=route == "/api/submit")
                self.send(200 if result["ok"] else 422, result)
            except (ValueError, KeyError, TypeError, UnicodeError) as exc:
                self.send(400, {"error": str(exc)})

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    return server, f"http://127.0.0.1:{server.server_port}/#token={token}"


def serve(workdir, period, port=0, open_browser=True):
    server, url = make_server(workdir, period, port)
    runtime = session_path(workdir, period).parent / "runtime.json"
    import os
    save(runtime, {"pid": os.getpid(), "url": url})
    print(json.dumps({"status": "listening", "url": url, "message": "逐项补充后点击提交，当前会话将继续生成报告。"}, ensure_ascii=False), flush=True)
    if open_browser:
        try:
            if not webbrowser.open(url):
                print("未能自动打开浏览器，请打开上述完整链接。", flush=True)
        except webbrowser.Error:
            print("未能自动打开浏览器，请打开上述完整链接。", flush=True)
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        if load(runtime, {}).get("url") == url:
            runtime.unlink(missing_ok=True)
