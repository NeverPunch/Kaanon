#!/usr/bin/env python3
"""Fasst die Gründe aller zurückgestellten Websites zu Engine-Wünschen zusammen.

Liest rezepte/warteschlange.json und ordnet jeden Grund (Freitext der Bearbeiter) per Stichwort
einer Kategorie zu. Ergebnis: rezepte/ENGINE_WUENSCHE_AUS_REZEPTEN.md, sortiert nach Anzahl Websites.
Eine Website kann mehreren Kategorien angehören.

Aufruf: python3 werkzeuge/rezepte/engine_wuensche.py
"""
import collections, json, os, re
HIER = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.normpath(os.path.join(HIER, '..', '..'))

# (Kategorie, Art, Muster) – Art: "regel" = Regel 0014, kein Engine-Wunsch; "engine" = fehlender Baustein
KATEGORIEN = [
    ('Login/Konto zum Lesen nötig', 'regel', r'login|anmeld|passwort|password|konto|firebase|abo\b|discord'),
    ('Prüfseite/CAPTCHA/Bot-Schutz', 'regel', r'prüfseite|challenge|ddos|captcha|turnstile|cloudflare|clearance|cookie-prüf|bot-schutz|honeypot'),
    ('Signatur/selbst erzeugter Schlüssel', 'regel', r'signatur|hmac|sha-?256|sha256|md5|hash-header|presign|geheim'),
    ('Iteration über JSON-Objekte (Maps)', 'engine', r'objekt-?map|json-objekt|objekt\b.*schlüssel|als map|\(map\)|objektschlüssel|maps\b|map \(|als objekt'),
    ('Auswahl per Platzhalter (Filter/Selektor mit {u.…}, Abgleich per ID/Slug)', 'engine', r'platzhalter|per id|per slug|abgleich|nach slug|per identifier|id-filter|auswahl per|aus der gesamt|aus einer gesamt|gesamtliste|gesamtkatalog|gesamtantwort'),
    ('Zahlenbereich erzeugen (Kapitel/Seiten 1..N)', 'engine', r'zähl|zahlenbereich|zahlenfolge|1\.\.|\.\.n\b|aus einer zahl|aus der seitenzahl|aus der bildanzahl|seitenindex|index-platzhalter|ab 0'),
    ('Blättern in Seitenlisten / Folgeseiten-Ketten', 'engine', r'folgeseite|rel=next|next-link|next\]|paging in pages|blättern in .?pages|über mehrere seiten|mehrere seiten mit|unterseiten|seitenweise'),
    ('Cursor-Blättern (Wert aus voriger Antwort/Header)', 'engine', r'cursor|header x-|antwort-header|x-wp-total|nextpagetoken|last_id'),
    ('Framework-Datenformate (SvelteKit-devalue, Qwik, turbo-stream, Inertia, Livewire, Server-Actions)', 'engine', r'devalue|sveltekit|qwik|turbo-?stream|inertia|livewire|server-action|astro|asp\.net|viewstate|postback'),
    ('Mehrere Quellen/Sprachen mit eigenen Pfaden', 'engine', r'quellen|sprachpfad|sprache.*(pfad|url)|je sprache|locale'),
    ('Entschlüsselung/Entwürfelung außerhalb aes_cryptojs/packer/grid/rects', 'engine', r'aes|xor|verwürfel|entwürfel|streifen|teilbild|umgedreht|umkehr|lzstring|verschleier|rohschlüssel|base64-alphabet|mulberry|xorshift|gcm'),
    ('WebView/JavaScript ausführen/Deobfuskieren', 'engine', r'webview|javascript|js-objekt|js-datei|js-chunk|js-antwort|deobfus|quickjs|eval\(|gepackt|reader\.js|skript.*verschleiert|verschleierten skript'),
    ('Protobuf/ZIP/Binärformate', 'engine', r'protobuf|zip|range-header|byte-bereich|pdf'),
    ('Rekursion, Eltern-/Geschwisterzugriff, Verzweigung je Eintrag', 'engine', r'rekursi|verschachtelt|eltern|vorfahr|geschwister|übergeordnet|verzweig|je typ|je eintrag|auffächer|zweige|alben'),
    ('Feste Listen im Code / Katalog ohne Anfrage', 'engine', r'fest im code|feste (titel)?liste|im code erzeugt|ohne anfrage|ohne abruf|im client|clientseitig|auf dem gerät'),
    ('Vorab-Anfragen (CSRF/Nonce/Token) für Listen und Kapitel', 'engine', r'csrf|nonce|token|vorab|redirect|weiterleitung|then.*(liste|kapitel)|folgeanfrage'),
    ('Bild-Anfragen mit Headern/POST je Bild', 'engine', r'bild-post|je bild|header .{0,20}aus der api|header `fansy`|bild-header'),
    ('Text-Bearbeitung/Übersetzung ins Bild', 'engine', r'ocr|übersetz|sprechblase|svg|bitmap'),
]

def main():
    liste = json.load(open(os.path.join(STORE, 'rezepte', 'warteschlange.json'), encoding='utf-8'))
    zur = [x for x in liste if x['status'] == 'zurueckgestellt']
    treffer = collections.defaultdict(list); ohne = []
    for x in zur:
        g = (x.get('grund') or '').lower()
        ks = [k for k, _, rx in KATEGORIEN if re.search(rx, g)]
        for k in ks: treffer[k].append(x)
        if not ks: ohne.append(x)
    art = {k: a for k, a, _ in KATEGORIEN}
    fertig = sum(1 for x in liste if x['status'] == 'fertig')
    o = ['# Engine-Wünsche aus der Rezept-Arbeit\n',
         f'Automatisch erzeugt von `werkzeuge/rezepte/engine_wuensche.py` aus `rezepte/warteschlange.json`. '
         f'{fertig} Rezepte sind fertig, {len(zur)} Websites sind zurückgestellt. Eine Website kann in mehreren Kategorien stehen.\n',
         '## Fehlende Bausteine der Rezeptsprache (nach Nutzen)\n',
         'Jeder Baustein würde die genannte Zahl zurückgestellter Websites (ganz oder teilweise) freischalten.\n',
         '| Baustein | Websites |', '|---|---:|']
    eng = sorted((k for k in treffer if art[k] == 'engine'), key=lambda k: -len(treffer[k]))
    for k in eng: o.append(f'| {k} | {len(treffer[k])} |')
    o += ['', '## Gründe nach Regel 0014 (keine Engine-Wünsche)\n', '| Grund | Websites |', '|---|---:|']
    for k in sorted((k for k in treffer if art[k] == 'regel'), key=lambda k: -len(treffer[k])):
        o.append(f'| {k} | {len(treffer[k])} |')
    o.append('\nDiese Websites bleiben Kandidaten für den Ausweg (Community-Code unverändert), wenn ein Community-Modul existiert.\n')
    o.append('## Einzelheiten\n')
    for k in eng + [k for k in treffer if art[k] == 'regel']:
        o.append(f'### {k} ({len(treffer[k])})\n')
        for x in sorted(treffer[k], key=lambda x: x['modul']):
            o.append(f"- `{x['modul']}` ({x['name']}): {x.get('grund','')}")
        o.append('')
    if ohne:
        o.append(f'### Ohne Zuordnung ({len(ohne)})\n')
        for x in sorted(ohne, key=lambda x: x['modul']): o.append(f"- `{x['modul']}` ({x['name']}): {x.get('grund','')}")
    open(os.path.join(STORE, 'rezepte', 'ENGINE_WUENSCHE_AUS_REZEPTEN.md'), 'w', encoding='utf-8').write('\n'.join(o) + '\n')
    print(f'{len(zur)} zurückgestellt, {len(ohne)} ohne Zuordnung')
    for k in eng: print(f'  {len(treffer[k]):4}  {k}')

if __name__ == '__main__':
    main()
