#!/usr/bin/env python3
"""Gemeinsame Warteschlange für die Rezept-Arbeit (rezepte/warteschlange.json).

Alle Kandidaten der Abdeckungskarte stehen in einer Liste. Jeder Bearbeiter (Mensch oder Agent)
nimmt sich die nächste freie Aufgabe, markiert sie als „in_arbeit“, erledigt sie und nimmt die nächste.
Das Sperren läuft über eine Dateisperre, so nimmt nie jemand dieselbe Aufgabe doppelt.

  aufbauen                         Liste aus abdeckung/karte.json anlegen/ergänzen (Status bleibt erhalten)
  nimm --wer NAME [--stufe 2] [--anzahl 5] [--theme madara]
  fertig MODUL --datei rezepte/modelle/x.json
  zurueck MODUL --grund "…"        zurückgestellt (z. B. Engine kann X nicht)
  frei MODUL                       Aufgabe wieder freigeben
  stand                            Übersicht
"""
import argparse, collections, contextlib, datetime, fcntl, json, os, sys

HIER = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.normpath(os.path.join(HIER, '..', '..'))
DATEI = os.path.join(STORE, 'rezepte', 'warteschlange.json')
SPERRE = os.path.join(STORE, 'rezepte', '.warteschlange.lock')

@contextlib.contextmanager
def gesperrt():
    os.makedirs(os.path.dirname(SPERRE), exist_ok=True)
    with open(SPERRE, 'w') as s:
        fcntl.flock(s, fcntl.LOCK_EX)
        try:
            liste = json.load(open(DATEI, encoding='utf-8')) if os.path.exists(DATEI) else []
            yield liste
            tmp = DATEI + '.tmp'
            json.dump(liste, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            os.replace(tmp, DATEI)
        finally:
            fcntl.flock(s, fcntl.LOCK_UN)

jetzt = lambda: datetime.datetime.now().isoformat(timespec='seconds')

def aufbauen(_):
    karte = json.load(open(os.path.join(STORE, 'abdeckung', 'karte.json'), encoding='utf-8'))['module']
    with gesperrt() as liste:
        alt = {x['modul']: x for x in liste}
        neu = []
        for r in karte:
            if r['kategorie'] != 'kandidat': continue
            x = alt.get(r['modul'], dict(modul=r['modul'], status='offen'))
            x.update(name=r['name'], stufe=r['stufe'], theme=r['theme'], sprachen=r['sprachen'][:6],
                     host=(r['hosts'] or [''])[0], nsfw=r['cw'] == 'NSFW')
            neu.append(x)
        neu.sort(key=lambda x: (x['stufe'], x['theme'] or '~', x['modul']))
        liste[:] = neu
    print(len(neu), 'Aufgaben')

def nimm(a):
    with gesperrt() as liste:
        out = []
        for x in liste:
            if len(out) >= a.anzahl: break
            if x['status'] != 'offen': continue
            if a.stufe and x['stufe'] != a.stufe: continue
            if a.theme and (x['theme'] or '') != a.theme: continue
            if a.ohne_theme and x['theme']: continue
            x.update(status='in_arbeit', wer=a.wer, seit=jetzt()); out.append(x['modul'])
    print('\n'.join(out) if out else 'KEINE')

def setze(modul, **kw):
    with gesperrt() as liste:
        for x in liste:
            if x['modul'] == modul:
                x.update(kw); x['geaendert'] = jetzt(); return
    sys.exit(f'unbekannt: {modul}')

def stand(_):
    liste = json.load(open(DATEI, encoding='utf-8'))
    c = collections.Counter((x['stufe'], x['status']) for x in liste)
    for st in sorted({x['stufe'] for x in liste}):
        print(f'Stufe {st}: ' + ', '.join(f'{s} {c[(st, s)]}' for s in ('offen', 'in_arbeit', 'fertig', 'zurueckgestellt') if c[(st, s)]))

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('aufbauen').set_defaults(f=aufbauen)
    p = sp.add_parser('nimm'); p.add_argument('--wer', required=True); p.add_argument('--stufe', type=int)
    p.add_argument('--anzahl', type=int, default=1); p.add_argument('--theme'); p.add_argument('--ohne-theme', action='store_true')
    p.set_defaults(f=nimm)
    p = sp.add_parser('fertig'); p.add_argument('modul'); p.add_argument('--datei', required=True)
    p.set_defaults(f=lambda a: setze(a.modul, status='fertig', datei=a.datei))
    p = sp.add_parser('zurueck'); p.add_argument('modul'); p.add_argument('--grund', required=True)
    p.set_defaults(f=lambda a: setze(a.modul, status='zurueckgestellt', grund=a.grund))
    p = sp.add_parser('frei'); p.add_argument('modul')
    p.set_defaults(f=lambda a: setze(a.modul, status='offen', wer=None))
    sp.add_parser('stand').set_defaults(f=stand)
    a = ap.parse_args(); a.f(a)

if __name__ == '__main__':
    main()
