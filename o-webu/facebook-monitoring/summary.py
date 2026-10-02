#!/usr/bin/env python3
"""Přepočítá blok "summary" ve všech o-webu/facebook-monitoring/*/yyyy-mm.json.

Spouští se po každém zápisu měsíčního souboru, aby summary nikdy
nerozcházelo s polem "posts". Použití: python3 o-webu/facebook-monitoring/summary.py
"""
import glob, json, os
from collections import Counter

base = os.path.dirname(os.path.abspath(__file__))
for path in sorted(glob.glob(os.path.join(base, '*', '????-??.json'))):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    posts = data['posts']
    dates = sorted(p['published'] for p in posts)
    data['summary'] = {
        'posts': len(posts),
        'by_type': dict(Counter(p['type'] for p in posts).most_common()),
        'shared_from_other_pages': sum(
            1 for p in posts
            if p.get('shared_from') and p['shared_from'].get('page') != 'mestopecky'),
        'first_published': dates[0] if dates else None,
        'last_published': dates[-1] if dates else None,
    }
    # summary hned za metadata, před posts
    ordered = {k: v for k, v in data.items() if k not in ('summary', 'posts')}
    ordered['summary'] = data['summary']
    ordered['posts'] = posts
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(ordered, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(os.path.relpath(path, base), data['summary'])
