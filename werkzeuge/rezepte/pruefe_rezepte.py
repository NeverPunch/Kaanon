#!/usr/bin/env python3
"""Prüft neue Rezepte (rezepte/stufe1/*.json, rezepte/modelle/*.json) gegen die Vorlagen.

- gültiges JSON, Rahmen `kaanon-rezept/1` mit Block `extension` und `quelle`
- Site-Model: Pflichtteile, nur Schlüssel, die in den Vorlagen vorkommen,
  nur bekannte Platzhalter, Formate, decode-Arten und transform-Typen,
  jedes {u.x}/{l.x}/{v.x} ist auch definiert
- Stufe 1: bekannter Baukasten, Parameter wie in den Vorlagen (neue Parameter = Warnung)

Aufruf: python3 werkzeuge/rezepte/pruefe_rezepte.py [dateien …]   (ohne Angabe: alle)
Rückgabe 0 = alles in Ordnung, 1 = Fehler gefunden.
"""
import collections, glob, json, os, re, sys

HIER = os.path.dirname(os.path.abspath(__file__))
REZ = os.path.normpath(os.path.join(HIER, '..', '..', 'rezepte'))
FREIE_MAPS = {'headers', 'image_headers', 'cookies', 'form', 'status_map', 'url_vars', 'let', 'vars',
              'variables', 'request_by_page', 'json', 'query'}
# Unterhalb dieser Schlüssel ist alles frei (Anfrage-Inhalte), auch in verschachtelten Objekten
TIEF_FREI = {'json', 'variables', 'form', 'headers', 'image_headers', 'cookies', 'query'}
PFLICHT = ('popular', 'details', 'chapters', 'pages')
PLATZHALTER = re.compile(r'\{([a-z_][a-z0-9_]*(?:\.[^{}\s]+)?|nowf:[^{}]+)\}')
EINFACH = {'base', 'page', 'page0', 'offset', 'query', 'query_raw', 'abs_url', 'url', 'value', 'page_key', 'now_s'}

def vokabular():
    schluessel, baukasten = set(), collections.defaultdict(lambda: collections.defaultdict(set))
    decode, formate, transform = set(), set(), set()
    def walk(o, frei=False):
        if isinstance(o, dict):
            for k, v in o.items():
                if not frei: schluessel.add(k)
                if k in ('decode', 'pre_decode') and isinstance(v, str): decode.add(v)
                if k == 'format' and isinstance(v, str): formate.add(v)
                walk(v, k in FREIE_MAPS or (frei == 'tief') or ('tief' if k in TIEF_FREI else False))
        elif isinstance(o, list):
            for x in o: walk(x, frei if frei == 'tief' else False)
        elif isinstance(o, str) and '"type"' in o:
            for t in re.findall(r'"type"\s*:\s*"(\w+)"', o): transform.add(t)
    for f in glob.glob(os.path.join(REZ, 'vorlagen', '*.json')):
        if f.endswith('index.json'): continue
        d = json.load(open(f, encoding='utf-8'))
        walk(d['modell'])
        if d.get('baukasten'):
            for k, v in (d.get('parameter') or {}).items(): baukasten[d['baukasten']][k].add(v)
    return schluessel, baukasten, decode, formate, transform

def pruefe_modell(m, V, fehler, warn):
    schluessel, _, decode, formate, transform = V
    if m.get('schema') != 'kaanon-site-model/2': fehler.append('schema muss "kaanon-site-model/2" sein')
    for p in PFLICHT:
        if p not in m: fehler.append(f'Pflichtteil fehlt: {p}')
    definiert = collections.defaultdict(set); benutzt = []
    def walk(o, pfad, frei=False):
        if isinstance(o, dict):
            for k, v in o.items():
                if not frei and k not in schluessel: fehler.append(f'unbekannter Schlüssel {pfad}.{k}')
                if k in ('url_vars', 'let', 'vars') and isinstance(v, dict):
                    definiert[k[0]].update(v.keys())
                if k in ('decode', 'pre_decode') and isinstance(v, str) and v not in decode:
                    fehler.append(f'unbekannte decode-Art {v!r} bei {pfad}.{k}')
                if k == 'format' and isinstance(v, str) and v not in formate:
                    fehler.append(f'unbekanntes format {v!r} bei {pfad}')
                walk(v, f'{pfad}.{k}', 'tief' if (frei == 'tief' or k in TIEF_FREI) else (k in FREIE_MAPS))
        elif isinstance(o, list):
            for x in o: walk(x, pfad, frei if frei == 'tief' else False)
        elif isinstance(o, str):
            for t in re.findall(r'"type"\s*:\s*"(\w+)"', o):
                if pfad.endswith('template') and t not in transform: fehler.append(f'unbekannter transform-Typ {t!r}')
            for ph in PLATZHALTER.findall(o):
                if ph in EINFACH or ph.startswith(('nowf:', 'f.')) or re.fullmatch(r'g\d+', ph): continue
                if '.' in ph and ph[0] in 'ulv' and ph[1] == '.':
                    benutzt.append((ph[0], ph[2:].split('.')[0], pfad)); continue
                fehler.append(f'unbekannter Platzhalter {{{ph}}} bei {pfad}')
    walk(m, '')
    for art, name, pfad in benutzt:
        if name not in definiert['u' if art == 'u' else art] and not (art == 'u' and name in ('path',)):
            fehler.append(f'{{{art}.{name}}} benutzt bei {pfad}, aber nirgends definiert')
    if 'search' not in m: warn.append('kein search-Teil')

def pruefe_datei(f, V):
    fehler, warn = [], []
    try:
        d = json.load(open(f, encoding='utf-8'))
    except Exception as e:
        return [f'kein gültiges JSON: {e}'], []
    if d.get('rezept') != 'kaanon-rezept/1': fehler.append('rezept muss "kaanon-rezept/1" sein')
    e = d.get('extension') or {}
    for k in ('name', 'sprache', 'base_url', 'nsfw'):
        if k not in e: fehler.append(f'extension.{k} fehlt')
    if e.get('base_url') and not re.match(r'^https?://[^/]+(/[^?#]*[^/?#])?$', e['base_url']):
        fehler.append('extension.base_url: Schema + Host (+ Pfad), ohne / am Ende')
    if not (d.get('quelle') or {}).get('modul'): fehler.append('quelle.modul fehlt')
    if 'baukasten' in d:
        bk = V[1].get(d['baukasten'])
        if bk is None: fehler.append(f'unbekannter Baukasten {d["baukasten"]!r}')
        else:
            for k, v in (d.get('parameter') or {}).items():
                if k == 'apex': continue
                if k not in bk: warn.append(f'neuer Parameter {k}={v!r} (Baukasten prüfen)')
        if not (d.get('parameter') or {}).get('apex'): fehler.append('parameter.apex fehlt')
    elif 'modell' in d:
        pruefe_modell(d['modell'], V, fehler, warn)
    else:
        fehler.append('weder baukasten noch modell')
    return fehler, warn

def main():
    V = vokabular()
    dateien = sys.argv[1:] or sorted(glob.glob(os.path.join(REZ, 'stufe1', '*.json')) + glob.glob(os.path.join(REZ, 'modelle', '*.json')))
    n_f = n_w = 0
    for f in dateien:
        fe, wa = pruefe_datei(f, V)
        if fe or wa:
            print(os.path.relpath(f, REZ))
            for x in fe: print('  FEHLER ', x)
            for x in wa: print('  Hinweis', x)
        n_f += bool(fe); n_w += bool(wa)
    print(f'{len(dateien)} Rezepte geprüft, {n_f} mit Fehlern, {n_w} mit Hinweisen')
    sys.exit(1 if n_f else 0)

if __name__ == '__main__':
    main()
