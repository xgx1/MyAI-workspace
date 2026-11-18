#!/usr/bin/env python3
"""网页小工具：GET /hello?name=X 返回「你好, X」。

用法:
    python3 main.py [port] [host]

默认端口 8088，默认只监听 127.0.0.1。
验收:
    python3 main.py 8088
    curl -s 'http://127.0.0.1:8088/hello?name=世界'
"""

from __future__ import annotations

import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

DEFAULT_PORT = 8088
DEFAULT_HOST = "127.0.0.1"
DEFAULT_NAME = "世界"


class HelloHandler(BaseHTTPRequestHandler):
    server_version = "HelloTool/1.0"

    def _target(self) -> str:
        """http.server 按 ISO-8859-1 解析请求行；把裸 UTF-8 字节还原成正常字符。

        curl 直接发 `?name=世界` 时路径里是未百分号编码的 UTF-8 字节，
        不还原的话 parse_qs 会二次编码成乱码。
        """
        path = self.path
        try:
            return path.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return path

    def _send_text(self, status: int, body: str) -> None:
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)

    def do_GET(self) -> None:  # noqa: N802 - stdlib 命名
        parts = urlsplit(self._target())
        path = parts.path.rstrip("/") or "/"

        if path == "/hello":
            query = parse_qs(parts.query, keep_blank_values=True)
            name = query.get("name", [""])[0].strip() or DEFAULT_NAME
            self._send_text(200, f"你好, {name}")
            return

        if path == "/":
            self._send_text(200, "用法: GET /hello?name=X  返回「你好, X」\n")
            return

        self._send_text(404, "404 Not Found\n")

    def do_HEAD(self) -> None:  # noqa: N802 - stdlib 命名
        self.do_GET()

    def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
        sys.stderr.write(
            "[%s] %s %s %s\n"
            % (self.log_date_time_string(), self.command, self._target(), code)
        )

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))


def main(argv: list[str]) -> int:
    port = DEFAULT_PORT
    host = DEFAULT_HOST
    positional = [a for a in argv[1:] if not a.startswith("-")]

    if positional:
        try:
            port = int(positional[0])
        except ValueError:
            sys.stderr.write(f"端口必须是整数: {positional[0]!r}\n")
            return 2
    if len(positional) > 1:
        host = positional[1]

    try:
        httpd = ThreadingHTTPServer((host, port), HelloHandler)
    except OSError as exc:
        sys.stderr.write(f"无法监听 {host}:{port}: {exc}\n")
        return 1

    print(f"监听 http://{host}:{port}  (Ctrl-C 退出)", flush=True)
    print(f"试一下: curl -s 'http://{host}:{port}/hello?name=%E4%B8%96%E7%95%8C'", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止", flush=True)
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
