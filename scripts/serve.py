#!/usr/bin/env python3
"""Lokální dev server pro pecky.online.

Web běží na vlastní doméně dopecek.cz na kořeni (SITE_BASE_PATH = ''
ve scripts/build.py), takže kořenově-absolutní odkazy (/assets/...)
fungují na http://localhost:PORT/ beze změny - žádná subcesta se
lokálně nesimuluje. (BASE_PATH tu zůstává jen jako přepínač pro
starší stav bez vlastní domény, kdy web běžel na GitHub Pages
subcestě /pecky.online/ - viz historie tohoto souboru.)

Použití:
    python3 scripts/serve.py [port]   # výchozí port 8000
Pak otevřít http://localhost:PORT/
"""
import functools
import http.server
import os
import sys
from pathlib import Path

BASE_PATH = ''
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
    try:
        http.server.test(HandlerClass=handler, port=port)
    except OSError as e:
        # Already running (e.g. spawned by a previous session that's still
        # alive) — treat re-invocation as a no-op instead of a traceback,
        # so "just start the server" is always safe to run again.
        if e.errno == 48:  # Address already in use
            print(f'Port {port} už je obsazený — server na něm pravděpodobně už běží '
                  f'(http://localhost:{port}{BASE_PATH}/). Nic se nespouští znovu.')
            sys.exit(0)
        raise
