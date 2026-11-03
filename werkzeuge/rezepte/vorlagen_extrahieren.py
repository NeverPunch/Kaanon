#!/usr/bin/env python3
"""Zieht die Site-Models (kaanon-site-model) aus den eigenen APKs des Stores.

Jede eigene Extension trägt ihr Rezept als JSON im Code. Diese Vorlagen sind die Referenz
für neue Rezepte: rezepte/vorlagen/<sprache>.<name>.json (+ vorlagen/index.json).
Aufruf: python3 werkzeuge/rezepte/vorlagen_extrahieren.py
"""
import json, os, re, sys, zipfile
HIER = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.normpath(os.path.join(HIER, '..', '..'))
ZIEL = os.path.join(STORE, 'rezepte', 'vorlagen')

def modelle_aus_dex(dex):
    out = []
    for m in re.finditer(rb'"schema"\s*:\s*"kaanon-site-model/\d+"', dex):
        s = dex.rfind(b'{', 0, m.start())
        out.append(json.JSONDecoder().raw_decode(dex[s:s + 2_000_000].decode('utf-8', 'replace'))[0])
    return out

def main():
    idx = json.load(open(os.path.join(STORE, 'index.json'), encoding='utf-8'))['extensionList']['extensions']
    ausweg = {f[7:-4] for f in os.listdir(os.path.join(STORE, 'lizenz')) if f.startswith('NOTICE-')}
    os.makedirs(ZIEL, exist_ok=True)
    uebersicht = []
    for e in idx:
        if e['packageName'] in ausweg: continue
        apk = os.path.join(STORE, 'apk', e['resources']['apkUrl'].rsplit('/', 1)[1])
        with zipfile.ZipFile(apk) as z:
            dex = b''.join(z.read(n) for n in z.namelist() if n.endswith('.dex'))
        modelle = modelle_aus_dex(dex)
        if len(modelle) != 1:
            print('WARNUNG', e['packageName'], len(modelle), 'Modelle', file=sys.stderr); continue
        m = modelle[0]
        kurz = e['packageName'].split('extension.', 1)[1].replace('kaanon.', '')
        baukasten, params = None, None
        o = m.get('origin', '')
        if o.startswith('baukasten:'):
            t, _, js = o.partition(' '); baukasten = t.split(':', 1)[1]; params = json.loads(js)
        datei = dict(extension=dict(name=e['name'], paket=e['packageName'], version=e['versionName'],
                                    inhalt=e['contentWarning'], quellen=e['sources']),
                     baukasten=baukasten, parameter=params, modell=m)
        json.dump(datei, open(os.path.join(ZIEL, kurz + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        uebersicht.append(dict(datei=kurz + '.json', name=e['name'], baukasten=baukasten,
                               home=e['sources'][0]['homeUrl'] if e['sources'] else None))
    uebersicht.sort(key=lambda x: x['datei'])
    json.dump(uebersicht, open(os.path.join(ZIEL, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(len(uebersicht), 'Vorlagen')

if __name__ == '__main__':
    main()
