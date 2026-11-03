#!/usr/bin/env python3
"""Gerüst für ein Stufe-2-Rezept: füllt extension/quelle aus Community-Index und Karte.

Aufruf: python3 werkzeuge/rezepte/geruest.py src/en/beispiel [--index index.json]
Schreibt rezepte/modelle/<sprache>.<name>.json mit leerem "modell" (falls noch nicht vorhanden)
und gibt den Pfad aus. Das Modell trägt man danach von Hand ein.
"""
import argparse, json, os, sys, urllib.request
HIER = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HIER)
import stufe1  # noqa: E402

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('modul'); ap.add_argument('--index', default=stufe1.INDEX_URL)
    a = ap.parse_args()
    karte = json.load(open(os.path.join(stufe1.STORE, 'abdeckung', 'karte.json'), encoding='utf-8'))
    r = next(x for x in karte['module'] if x['modul'] == a.modul.rstrip('/'))
    idx = json.load(urllib.request.urlopen(a.index) if a.index.startswith('http') else open(a.index, encoding='utf-8'))
    ke = next(e for e in idx['extensionList']['extensions'] if e['packageName'] == r['pkg'])
    ext, _ = stufe1.extension_block(r, ke)
    ziel = os.path.join(stufe1.REZ, 'modelle', stufe1.dateiname(ext) + '.json')
    os.makedirs(os.path.dirname(ziel), exist_ok=True)
    if not os.path.exists(ziel):
        json.dump({'rezept': 'kaanon-rezept/1', 'status': 'entwurf', 'extension': ext,
                   'quelle': dict(modul=r['modul'], community_stand=karte['meta']['community'],
                                  community_version=ke['versionName'], theme=r['theme']),
                   'modell': {'schema': 'kaanon-site-model/2'}, 'hinweise': []},
                  open(ziel, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(os.path.relpath(ziel, stufe1.STORE))

if __name__ == '__main__':
    main()
