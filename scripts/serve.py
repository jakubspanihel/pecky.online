#!/usr/bin/env python3
"""Lokální dev server, který napodobuje GitHub Pages subcestu (/pecky.online/),
aby při testu fungovaly stejné kořenově-absolutní odkazy jako po nasazení
(viz SITE_BASE_PATH ve scripts/build.py). Bez tohohle by lokální test na
http://localhost:PORT/ ukazoval nestylovanou stránku s 404 na assety, i
když je build v pořádku - subcesta lokálně jinak neexistuje.

Použití:
    python3 scripts/serve.py [port]   # výchozí port 8000
Pak otevřít http://localhost:PORT/pecky.online/
"""
import functools
import http.server
import os
import sys
from pathlib import Path

BASE_PATH = '/pecky.online'
# Absolute, resolved from __file__ rather than the process's cwd — a
# relative path (or the default no-`directory` behavior of
# SimpleHTTPRequestHandler) needs a working os.getcwd() at request time,
# which can fail with "Operation not permitted" if the process was spawned
# with a cwd the sandbox can't stat (seen with the launch.json dev-server
# runner). Resolving via __file__ sidesteps that entirely.
SITE_ROOT = Path(__file__).resolve().parent.parent


class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = path.split('?', 1)[0].split('#', 1)[0]
        if path == BASE_PATH or path.startswith(BASE_PATH + '/'):
            path = path[len(BASE_PATH):] or '/'
        return super().translate_path(path)


if __name__ == '__main__':
    # port: CLI arg takes priority, then $PORT (set by the dev-server
    # launcher when invoked without a shell to expand "$PORT" itself), then
    # the 8000 default.
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    elif os.environ.get('PORT'):
        port = int(os.environ['PORT'])
    else:
        port = 8000
    handler = functools.partial(Handler, directory=str(SITE_ROOT))
    http.server.test(HandlerClass=handler, port=port)
