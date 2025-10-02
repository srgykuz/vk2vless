import os
import http.server


LISTEN_HOST = os.getenv("LISTEN_HOST", "127.0.0.1")
LISTEN_PORT = int(os.getenv("LISTEN_PORT", 8000))

DIR = os.getenv("DIR", "./var/run")
PATH = os.getenv("PATH", "/test")


class Handler(http.server.SimpleHTTPRequestHandler):
    not_found_path = "/_not_found"
    allowed_paths = [
        "/wss.txt",
        "/vless.txt",
        "/vmess.txt",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, directory=DIR)

    def send_head(self):
        if self.path.startswith(PATH):
            self.path = self.path.removeprefix(PATH)
        else:
            self.path = self.not_found_path

        if self.path not in self.allowed_paths:
            self.path = self.not_found_path

        return super().send_head()


def main():
    addr = (LISTEN_HOST, LISTEN_PORT)
    httpd = http.server.HTTPServer(addr, Handler)

    print(f"Listening at http://{addr[0]}:{addr[1]}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
