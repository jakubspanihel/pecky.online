"""Další zdroje do znalostního indexu PečkyBota (kalendář, komise, výbory, školská rada,
organizace, …). Každý zdroj je funkce vracející seznam úryvků {'u': url, 't': titulek, 'x': text};
chunks_extra() je spojí. Volá se z build_peckybot_index.py."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def chunks_extra():
    return []
