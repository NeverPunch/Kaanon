#!/usr/bin/env python3
"""Abschluss-Bereinigung aller Rezepte (stufe1/ + modelle/).

- `extension.sprache` passend zu den verbliebenen Quellen (eine Sprache → diese, sonst „all“)
- `extension.paket` und Dateiname passend zu Sprache + Name (wie geruest.py)
- doppelte Paketnamen und doppelte Quell-IDs finden (untereinander und gegen den Store)
- Warteschlange zeigt auf die richtige Datei

Aufruf: python3 werkzeuge/rezepte/bereinigen.py [--schreiben]
Ohne --schreiben wird nur berichtet.
"""
import collections, glob, json, os, sys
HIER = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HIER)
import stufe1, warteschlange as ws  # noqa: E402

def main():
    schreiben = '--schreiben' in sys.argv
    store = json.load(open(os.path.join(stufe1.STORE, 'index.json'), encoding='utf-8'))['extensionList']['extensions']
    store_pakete = {e['packageName'] for e in store}
    store_ids = {s['id']: e['packageName'] for e in store for s in e['sources']}
    dateien = sorted(glob.glob(os.path.join(stufe1.REZ, 'stufe1', '*.json')) + glob.glob(os.path.join(stufe1.REZ, 'modelle', '*.json')))
    umbenannt, pakete, ids, meldungen = {}, collections.defaultdict(list), collections.defaultdict(list), []
    for f in dateien:
        d = json.load(open(f, encoding='utf-8'))
        e = d['extension']
        sprachen = sorted({q['sprache'] for q in e.get('quellen', [])}) or [e['sprache']]
        soll = sprachen[0] if len(sprachen) == 1 else 'all'
        geaendert = False
        if e['sprache'] != soll:
            meldungen.append(f"{os.path.basename(f)}: sprache {e['sprache']} → {soll}"); e['sprache'] = soll; geaendert = True
        paket = f"eu.kanade.tachiyomi.extension.{soll}.kaanon.{stufe1.paket_name(e['name'], d['quelle']['modul'])}"
        if e.get('paket') != paket:
            meldungen.append(f"{os.path.basename(f)}: paket → {paket}"); e['paket'] = paket; geaendert = True
        ziel = os.path.join(os.path.dirname(f), stufe1.dateiname(e) + '.json')
        if schreiben and geaendert:
            json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        if ziel != f:
            if os.path.exists(ziel) and ziel not in umbenannt.values():
                meldungen.append(f'KONFLIKT Dateiname: {os.path.basename(f)} → {os.path.basename(ziel)} existiert schon')
            else:
                meldungen.append(f'{os.path.basename(f)} → {os.path.basename(ziel)}')
                if schreiben: os.replace(f, ziel)
                umbenannt[f] = ziel
                f = ziel
        pakete[paket].append(os.path.basename(f))
        for q in e.get('quellen', []):
            ids[q['quell_id']].append(os.path.basename(f))
    for p, fs in pakete.items():
        if len(fs) > 1: meldungen.append(f'DOPPELTES PAKET {p}: {fs}')
        if p in store_pakete: meldungen.append(f'PAKET SCHON IM STORE {p}: {fs}')
    for i, fs in ids.items():
        if len(set(fs)) > 1: meldungen.append(f'DOPPELTE QUELL-ID {i}: {sorted(set(fs))}')
        if i in store_ids: meldungen.append(f'QUELL-ID SCHON IM STORE {i} ({store_ids[i]}): {fs}')
    if schreiben and umbenannt:
        rel = {os.path.relpath(a, stufe1.STORE): os.path.relpath(b, stufe1.STORE) for a, b in umbenannt.items()}
        with ws.gesperrt() as liste:
            for x in liste:
                if x.get('datei') in rel: x['datei'] = rel[x['datei']]
    print('\n'.join(meldungen) or 'alles sauber')
    print(f'{len(dateien)} Rezepte, {len(meldungen)} Meldungen', '(geschrieben)' if schreiben else '(nur Bericht)')

if __name__ == '__main__':
    main()
