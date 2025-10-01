import os
import sys
import subprocess
import select
import urllib.parse
import socket
import logging
import json
import base64
import time


PATH_NODE = os.getenv("PATH_NODE", "")
PATH_VK_TUNNEL = os.getenv("PATH_VK_TUNNEL", "")

VK_TUNNEL_HOST = os.getenv("VK_TUNNEL_HOST", "127.0.0.1")
VK_TUNNEL_PORT = os.getenv("VK_TUNNEL_PORT", "2007")
VK_TUNNEL_WS_PROTOCOL = os.getenv("VK_TUNNEL_WS_PROTOCOL", "ws")
VK_TUNNEL_WS_ORIGIN = os.getenv("VK_TUNNEL_WS_ORIGIN", "1")
VK_TUNNEL_INSECURE = os.getenv("VK_TUNNEL_INSECURE", "0")
VK_TUNNEL_TIMEOUT = os.getenv("VK_TUNNEL_TIMEOUT", "5000")

VLESS_TITLE = os.getenv("VLESS_TITLE", "vk-vless")
VLESS_ID = os.getenv("VLESS_ID", "")
VLESS_FP = os.getenv("VLESS_FP", "chrome")

VMESS_TITLE = os.getenv("VMESS_TITLE", "vk-vmess")
VMESS_ID = os.getenv("VMESS_ID", "")
VMESS_FP = os.getenv("VMESS_FP", "chrome")

LOG_LEVEL = int(os.getenv("LOG_LEVEL", logging.INFO))
CAPTURE_TIMEOUT = int(os.getenv("CAPTURE_TIMEOUT", 20))


logging.basicConfig(
    stream=sys.stdout,
    level=LOG_LEVEL,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("main")


class UnathorizedError(Exception):
    pass


def main():
    precondition()

    run = True

    while run:
        proc = spawn()
        logger.info(f"spawned, pid={proc.pid}")

        try:
            handle(proc)
        except KeyboardInterrupt:
            print()
            run = False
        except UnathorizedError:
            logger.error("unathorized")
            run = False
        except Exception as e:
            logger.error(e)
        finally:
            proc.terminate()
            proc.wait()
            logger.info(f"terminated, code={proc.returncode}")

        if run:
            time.sleep(1)


def precondition():
    required = [
        "PATH_NODE",
        "PATH_VK_TUNNEL",
    ]

    for key in required:
        if not os.getenv(key):
            raise Exception(f"{key} env is empty")


def handle(proc: subprocess.Popen):
    output = capture(proc)
    logger.debug(f"captured:\n{output}\n")

    if not output:
        raise Exception("Empty output")
    elif "oauth.vk.ru/code_auth" in output:
        raise UnathorizedError()

    wss = extract_wss(output)
    logger.info(f"wss: {wss}")

    if not wss:
        raise Exception("Empty WSS")

    wss_url = urllib.parse.urlparse(wss)
    wss_host = socket.gethostbyname(wss_url.netloc)

    if VLESS_ID:
        vless = wss_to_vless(wss_url, wss_host)
        logger.info(f"vless: {vless}")

    if VMESS_ID:
        vmess = wss_to_vmess(wss_url, wss_host)
        logger.info(f"vmess: {vmess}")

    proc.wait()


def spawn() -> subprocess.Popen:
    args = [
        PATH_NODE,
        PATH_VK_TUNNEL,
        "--host",
        VK_TUNNEL_HOST,
        "--port",
        VK_TUNNEL_PORT,
        "--ws-protocol",
        VK_TUNNEL_WS_PROTOCOL,
        "--ws-origin",
        VK_TUNNEL_WS_ORIGIN,
        "--insecure",
        VK_TUNNEL_INSECURE,
        "--timeout",
        VK_TUNNEL_TIMEOUT,
    ]
    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,
    )

    return proc


def capture(proc: subprocess.Popen) -> str:
    output = ""
    reached_end = False

    while not reached_end:
        rlist, _, _ = select.select([proc.stdout, proc.stderr], [], [], CAPTURE_TIMEOUT)

        if not rlist:
            break

        for f in rlist:
            b: bytes = f.read(128)
            output += b.decode("utf-8")
            reached_end = (
                ("press ENTER to continue" in output) or
                output.count("tunnel.vk-apps.com/") == 2
            )

    return output


def extract_wss(output: str) -> str:
    start_s = "wss://"
    start = output.find(start_s)

    if start == -1:
        return ""

    end_s = "vk-apps.com/"
    end = output.find(end_s, start)

    if end == -1:
        return ""

    return output[start:end+len(end_s)]


def wss_to_vless(url: urllib.parse.ParseResult, netloc_ip: str) -> str:
    cfg = {
        "encryption": "none",
        "security": "tls",
        "sni": "tunnel.vk-apps.com",
        "alpn": "h2,http/1.1",
        "fp": VLESS_FP,
        "host": url.netloc,
        "path": "/",
        "type": "ws",
    }
    cfg_s = "&".join([f"{k}={v}" for k, v in cfg.items()])
    vless = f"vless://{VLESS_ID}@{netloc_ip}:443?{cfg_s}#{VLESS_TITLE}"
    vless = urllib.parse.quote(vless, safe="~@#$&()*!+=:;,?/\'")

    return vless


def wss_to_vmess(url: urllib.parse.ParseResult, netloc_ip: str) -> str:
    cfg = {
        "add": netloc_ip,
        "aid": "0",
        "alpn": "h2,http/1.1",
        "fp": VMESS_FP,
        "host": url.netloc,
        "id": VMESS_ID,
        "net": "ws",
        "path": "/",
        "port": "443",
        "ps": VMESS_TITLE,
        "scy": "auto",
        "sni": "tunnel.vk-apps.com",
        "tls": "tls",
        "type": "none",
        "v": "2",
    }
    s = json.dumps(cfg)
    b = s.encode("utf-8")
    b64 = base64.b64encode(b).decode("utf-8")
    vmess = f"vmess://{b64}"

    return vmess


if __name__ == "__main__":
    main()
