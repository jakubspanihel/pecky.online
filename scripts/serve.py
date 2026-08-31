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
import http.server
import sys

BASE_PATH = '/pecky.online'


class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = path.split('?', 1)[0].split('#', 1)[0]
        if path == BASE_PATH or path.startswith(BASE_PATH + '/'):
            path = path[len(BASE_PATH):] or '/'
        return super().translate_path(path)


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    http.server.test(HandlerClass=Handler, port=port)
