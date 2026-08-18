#!/bin/bash
cd "$(dirname "$0")"
echo "Spouštím lokální server pro pecky.online na http://localhost:8000"
echo "Pro ukončení stiskni Ctrl+C nebo zavři toto okno."
open "http://localhost:8000"
python3 -m http.server 8000
