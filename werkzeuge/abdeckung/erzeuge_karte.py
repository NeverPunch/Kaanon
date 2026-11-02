#!/usr/bin/env python3
"""Kaanon-Abdeckungskarte.

Gleicht alle Module der Community-Sammlung (keiyoushi/extensions-source) mit dem
Kaanon-Store ab und schätzt je Website ein, ob sie
  - schon im Store ist (eigene Engine oder Ausweg),
  - mit unserer Engine gebaut werden darf (Kandidat, Stufe 1-3) oder
  - nach Regel 0014 nur als Ausweg (unveränderter Community-Code) in Frage kommt.

Die Einschätzung beruht auf festen Mustern im Quellcode (Modul + Theme + Bibliotheken).
Sie ist eine Voreinschätzung. Verbindlich bleibt die Regel-Prüfung im Builder.

Nur Standardbibliothek. Aufruf (Beispiel):
  python3 erzeuge_karte.py --community ../extensions-source --store .. --aus ../abdeckung
Fehlt --community, wird der Community-Stand flach geklont (git nötig).
Fehlt --index, wird der aktuelle Community-Index geladen.
"""
import argparse, collections, datetime, json, os, re, subprocess, sys, urllib.request
from urllib.parse import urlparse

INDEX_URL = 'https://raw.githubusercontent.com/keiyoushi/extensions/repo/index.json'
REPO_URL = 'https://github.com/keiyoushi/extensions-source.git'

# ----------------------------------------------------------------------------------------------
# Kotlin zerlegen: Code ohne Kommentare/Strings, Strings getrennt
# ----------------------------------------------------------------------------------------------
def zerlege(src):
    code, strings, i, n = [], [], 0, len(src)
    while i < n:
        c = src[i]
        if src.startswith('//', i):
            j = src.find('\n', i); i = n if j < 0 else j
        elif src.startswith('/*', i):
            tiefe, i = 1, i + 2
            while i < n and tiefe:
                if src.startswith('/*', i): tiefe += 1; i += 2
                elif src.startswith('*/', i): tiefe -= 1; i += 2
                else: i += 1
        elif src.startswith('"""', i):
            j = src.find('"""', i + 3); j = n if j < 0 else j
            strings.append(src[i + 3:j]); code.append('""'); i = j + 3
        elif c == '"':
            j, buf = i + 1, []
            while j < n and src[j] != '"' and src[j] != '\n':
                if src[j] == '\\': buf.append(src[j:j + 2]); j += 2; continue
                buf.append(src[j]); j += 1
            strings.append(''.join(buf)); code.append('""'); i = j + 1
        elif c == "'":
            start = i + 3 if i + 1 < n and src[i + 1] == '\\' else i + 2
            j = src.find("'", start)
            code.append("''"); i = (n if j < 0 else j + 1)
        else:
            code.append(c); i += 1
    return ''.join(code), strings

# ----------------------------------------------------------------------------------------------
# Muster
# ----------------------------------------------------------------------------------------------
WEBVIEW = re.compile(r'\brunWebView(Blocking)?\b|\bWebViewClient\b|android\.webkit\.WebView\b|\bevaluateJavascript\b|\bevaluateJs\b|\binjectAtDocumentStart\b')
SCHUTZ_SIGNAL = re.compile(r'(?i)challenge|challange|clearance|captcha|turnstile|guard|ddos|trust')
SCHUTZ_NAMEN = re.compile(r'(?i)__ddg\d|ddos-guard|sucuri|x-challange|x-challenge|anubis|proof.?of.?work|hashcash|__guard_trust')
LOESER_KLASSE = re.compile(r'\b(class|object)\s+\w*(Challenge|Challange|Guard|Ddos|DDoS|Captcha|Cloudflare|Bypass)\w*')
LOESER_FUN = re.compile(r'\bfun\s+(solve|bypass)\w*\s*\(')
CAPTCHA_CODE = re.compile(r'\bgetTurnstileToken\b|(?i:\w*(recaptcha|hcaptcha|turnstile)\w*)')
CAPTCHA_WORT = re.compile(r'(?i)captcha')
BILD = re.compile(r'(?i)\w*(descrambl|unscrambl|scrambl)\w*|\bSeedRandom\b')
ENTSCHL = re.compile(r'Cipher\.getInstance|\bSecretKeySpec\b|\b(aesCbc|aesGcm|aesCtr|aesEcb|newAesCipher|aesDecrypt\w*|cryptoJsDecrypt|evpBytesToKey|rc4)\b|(?i:\w*decrypt\w*)')
XOR = re.compile(r'\bxorInPlace\b|\bXorInterceptor\b|\.xor\(')
DRM_KENNUNG = re.compile(r'(?i)(^|[^a-z])drm([^a-z]|$)|widevine|playready|\be4p\b')
SIGNATUR = re.compile(r'Mac\.getInstance|\bhmac\w*|\bHmac\w*|\bKeyPairGenerator\b|\bKeyAgreement\b|(?i:\w*(generateSignature|signRequest|signUrl|createSignature)\w*)')
KONTO = re.compile(r'(?i)password|passwort')
LOKAL = re.compile(r'^(localhost|127\.|10\.|192\.168\.|0\.0\.0\.0)')  # selbst gehostete Server (Komga & Co.)
KONTO_PREF = re.compile(r'(?i)api.?key|access.?token|auth.?token')
MANUELL = re.compile(r'(?i)webview.*(captcha|cloudflare|challenge|verif|solve|bypass|protection|block)|(captcha|cloudflare|challenge|verif\w*|protection).*webview')

LIB_KLASSEN = {  # Bibliotheken, deren Zweck eine Regel-Klasse ist
    'speedbinb': {'DRM': 'lib:speedbinb'}, 'publus': {'DRM': 'lib:publus'},
    'clipstudioreader': {'DRM': 'lib:clipstudioreader'}, 'e4p': {'DRM': 'lib:e4p'},
    'ece': {'DRM': 'lib:ece'}, 'aessiv': {'DRM': 'lib:aessiv'},
    'secretstream': {'DRM': 'lib:secretstream', 'SCHLUESSEL': 'lib:secretstream (X25519)'},
}
TECHNIK = {
    'json_api': re.compile(r'parseAs<|kotlinx\.serialization|@Serializable'),
    'html': re.compile(r'asJsoup|Jsoup|\.select\(|selectFirst'),
    'graphql': re.compile(r'(?i)graphql'),
    'nextjs_rsc': re.compile(r'(?i)nextjs|reactFlight|__next_f|__NEXT_DATA__'),
    'protobuf': re.compile(r'(?i)protobuf|parseAsProto'),
    'packed_js': re.compile(r'(?i)unpacker|Unpacker|eval\(function\(p,a,c,k,e'),
    'js_engine': re.compile(r'(?i)quickjs|duktape|rhino|javascriptengine'),
    'zip': re.compile(r'(?i)zipinputstream|keiyoushi\.zip'),
    'lzstring': re.compile(r'LZString'),
}
EXOTISCH = {'protobuf', 'zip', 'js_engine', 'webview', 'deobfuskation'}
REGELN = ('PRUEFSEITE', 'CAPTCHA', 'DRM', 'SCHLUESSEL')


def pruefe(texte, libs):
    """texte: Liste von Kotlin-Quelltexten. Liefert (regel, manuell, konto, technik)."""
    code, strings = [], []
    for t in texte:
        c, s = zerlege(t); code.append(c); strings += s
    C = '\n'.join(code)
    tok = '\n'.join(s for s in strings if not re.search(r'\s', s))   # Header-/Cookie-Namen, Schlüssel
    msg = '\n'.join(s for s in strings if re.search(r'\s', s))       # Meldungen, Selektoren
    r = collections.defaultdict(set)
    wv = bool(WEBVIEW.search(C))
    signal = bool(SCHUTZ_SIGNAL.search(C) or SCHUTZ_SIGNAL.search(tok))
    if LOESER_KLASSE.search(C): r['PRUEFSEITE'].add('Löser-Klasse')
    if LOESER_FUN.search(C): r['PRUEFSEITE'].add('Löser-Funktion')
    if SCHUTZ_NAMEN.search(C) or SCHUTZ_NAMEN.search(tok): r['PRUEFSEITE'].add('bekannter Schutz')
    if wv and signal: r['PRUEFSEITE'].add('WebView-Automatik')
    if wv and re.search(r'(?i)cf_clearance', C + tok): r['PRUEFSEITE'].add('Cloudflare per WebView')
    if CAPTCHA_CODE.search(C) or re.search(r'(?i)recaptcha|hcaptcha|turnstile', tok): r['CAPTCHA'].add('CAPTCHA im Code')
    if wv and CAPTCHA_WORT.search(C): r['CAPTCHA'].add('CAPTCHA per WebView')
    # WebView läuft und Meldungen/Selektoren beziehen sich auf einen Schutz: automatischer Versuch wahrscheinlich
    if wv and re.search(r'(?i)cloudflare|challenge|challange|ddos|cf-turnstile', msg): r['PRUEFSEITE'].add('WebView mit Schutz-Bezug')
    if wv and re.search(r'(?i)captcha|turnstile|recaptcha', msg): r['CAPTCHA'].add('WebView mit CAPTCHA-Bezug')
    if BILD.search(C): r['DRM'].add('Bild-Entwürfelung')
    if ENTSCHL.search(C): r['DRM'].add('Entschlüsselung')
    if XOR.search(C): r['DRM'].add('XOR-Verschleierung')
    if DRM_KENNUNG.search(C) or DRM_KENNUNG.search(tok): r['DRM'].add('DRM-Format')
    if SIGNATUR.search(C): r['SCHLUESSEL'].add('Signatur/HMAC/Schlüsseltausch')
    for l in libs:
        for k, v in LIB_KLASSEN.get(l, {}).items(): r[k].add(v)
    manuell = bool(MANUELL.search(msg)) and not (r['PRUEFSEITE'] or r['CAPTCHA'])
    konto = bool(KONTO.search(C + '\n' + tok + '\n' + msg)) or (
        'EditTextPreference' in C and bool(KONTO_PREF.search(C + tok + msg)))
    technik = sorted(k for k, rx in TECHNIK.items() if rx.search(C) or rx.search(tok))
    if wv and not (r['PRUEFSEITE'] or r['CAPTCHA']): technik.append('webview')
    if 'synchrony' in libs: technik.append('deobfuskation')
    if 'textinterceptor' in libs: technik.append('text')
    return {k: sorted(v) for k, v in r.items() if v}, manuell, konto, sorted(set(technik))

# ----------------------------------------------------------------------------------------------
# Einlesen
# ----------------------------------------------------------------------------------------------
def kt_texte(d):
    out = []
    for root, _, files in os.walk(d):
        for f in sorted(files):
            if f.endswith(('.kt', '.java')):
                out.append(open(os.path.join(root, f), encoding='utf-8', errors='replace').read())
    return out

def build_datei(d):
    for n in ('build.gradle.kts', 'build.gradle'):
        p = os.path.join(d, n)
        if os.path.exists(p): return open(p, encoding='utf-8').read()
    return ''

def libs_aus(build): return sorted(set(re.findall(r'project\(":lib:([\w-]+)"\)', build)))
host = lambda u: urlparse(u if '//' in u else '//' + u).netloc.lower().removeprefix('www.')

def git_stand(pfad):
    try:
        return subprocess.check_output(['git', '-C', pfad, 'log', '-1', '--format=%h %cs'], text=True).strip()
    except Exception:
        return 'unbekannt'

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    hier = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument('--community', help='Pfad zu keiyoushi/extensions-source (sonst wird geklont)')
    ap.add_argument('--index', default=INDEX_URL, help='Community-index.json (Pfad oder URL)')
    ap.add_argument('--store', default=os.path.join(hier, '..', '..'), help='Pfad zum Kaanon-Store-Repo')
    ap.add_argument('--aus', default=os.path.join(hier, '..', '..', 'abdeckung'), help='Ausgabeordner')
    a = ap.parse_args()

    R = a.community
    if not R:
        R = os.path.join(hier, '.community')
        if os.path.isdir(R): subprocess.check_call(['git', '-C', R, 'pull', '-q', '--depth', '1'])
        else: subprocess.check_call(['git', 'clone', '-q', '--depth', '1', REPO_URL, R])
    if a.index.startswith('http'):
        with urllib.request.urlopen(a.index, timeout=120) as f: kei_idx = json.load(f)
    else:
        kei_idx = json.load(open(a.index, encoding='utf-8'))
    kei = {e['packageName']: e for e in kei_idx['extensionList']['extensions']}
    kaa = json.load(open(os.path.join(a.store, 'index.json'), encoding='utf-8'))['extensionList']['extensions']
    liz = os.path.join(a.store, 'lizenz')
    ausweg = {f[len('NOTICE-'):-4] for f in os.listdir(liz) if f.startswith('NOTICE-')}

    # Kaanon nach ID und Host
    k_id, k_host, k_alle = {}, {}, {}
    for e in kaa:
        art = 'ausweg' if e['packageName'] in ausweg else 'eigen'
        rec = dict(pkg=e['packageName'], name=e['name'], version=e['versionName'], art=art,
                   hosts=sorted({host(s['homeUrl']) for s in e['sources']}))
        k_alle[e['packageName']] = rec
        for s in e['sources']:
            k_id[int(s['id'])] = rec; k_host.setdefault(host(s['homeUrl']), rec)

    # Themes
    themes = {}
    for t in sorted(os.listdir(f'{R}/lib-multisrc')):
        b = build_datei(f'{R}/lib-multisrc/{t}')
        themes[t] = dict(libs=libs_aus(b), texte=kt_texte(f'{R}/lib-multisrc/{t}'))
        p = pruefe(themes[t]['texte'], themes[t]['libs'])
        themes[t]['kann'], themes[t]['technik'] = p[0], p[3]

    rows, gesehen = [], set()
    for lang in sorted(os.listdir(f'{R}/src')):
        for m in sorted(os.listdir(f'{R}/src/{lang}')):
            d = f'{R}/src/{lang}/{m}'; b = build_datei(d)
            g = lambda k: (re.search(rf'\b{k}\s*=\s*"([^"]*)"', b) or [None, None])[1]
            theme = g('theme'); pkg = 'eu.kanade.tachiyomi.extension.' + (g('pkgName') or f'{lang}.{m}')
            libs = set(libs_aus(b)) | set(themes.get(theme, {}).get('libs', []))
            regel, manuell, konto, technik = pruefe(kt_texte(d), libs)
            if theme in themes:  # Technik des Themes gehört dazu, Regel-Treffer des Themes nur als "kann"
                technik = sorted(set(technik) | set(themes[theme]['technik']))
            ke = kei.get(pkg); srcs = ke['sources'] if ke else []
            hosts = sorted({host(s['homeUrl']) for s in srcs} | {host(u) for u in re.findall(r'baseUrl\s*=\s*"([^"]+)"', b)})
            kz = next((k_id[int(s['id'])] for s in srcs if int(s['id']) in k_id), None) \
                or next((k_host[h] for h in hosts if h in k_host), None)
            if kz: gesehen.add(kz['pkg'])
            hart = sorted(k for k in REGELN if k in regel)
            if kz: kat = 'kaanon_' + kz['art']
            elif hart: kat = 'nur_ausweg'
            elif any(LOKAL.match(h) for h in hosts): kat = 'server'
            else: kat = 'kandidat'
            rows.append(dict(
                modul=f'src/{lang}/{m}', name=(ke or {}).get('name') or g('name') or m, pkg=pkg,
                sprachen=sorted({s['language'] for s in srcs}) or [lang], hosts=hosts,
                theme=theme, libs=sorted(libs), community_version=(ke or {}).get('versionName'),
                cw=(re.search(r'ContentWarning\.(\w+)', b) or [None, None])[1],
                regel=regel, theme_kann=themes.get(theme, {}).get('kann', {}) if theme else {},
                manuell=manuell, konto=konto, technik=technik, kaanon=kz, kategorie=kat))

    eigene_themes = {r['theme'] for r in rows if r['kategorie'] == 'kaanon_eigen' and r['theme']}
    for r in rows:
        r['familie_bekannt'] = bool(r['theme']) and r['theme'] in eigene_themes
        r['stufe'] = None
        if r['kategorie'] == 'kandidat':
            if EXOTISCH & set(r['technik']): r['stufe'] = 3
            elif r['familie_bekannt']: r['stufe'] = 1
            elif r['theme_kann']: r['stufe'] = 3
            else: r['stufe'] = 2
    nur_kaanon = sorted((v for k, v in k_alle.items() if k not in gesehen), key=lambda v: v['name'])

    meta = dict(community=git_stand(R), store=git_stand(a.store), erzeugt=datetime.date.today().isoformat(),
                module=len(rows), themes=len(themes), kaanon=len(kaa))
    os.makedirs(a.aus, exist_ok=True)
    json.dump(dict(meta=meta, module=rows, nur_in_kaanon=nur_kaanon), open(os.path.join(a.aus, 'karte.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    schreibe_html(rows, meta, nur_kaanon, os.path.join(hier, 'vorlage.html'), os.path.join(a.aus, 'karte.html'))
    schreibe_readme(rows, meta, nur_kaanon, os.path.join(a.aus, 'README.md'))
    print(collections.Counter(r['kategorie'] for r in rows), meta)

# ----------------------------------------------------------------------------------------------
# Ausgabe
# ----------------------------------------------------------------------------------------------
KAT_CODE = {'kaanon_eigen': 'E', 'kaanon_ausweg': 'A', 'kandidat': 'K', 'nur_ausweg': 'N', 'server': 'C'}
ABK = {'PRUEFSEITE': 'P', 'CAPTCHA': 'C', 'DRM': 'D', 'SCHLUESSEL': 'S'}

def schreibe_html(rows, meta, nur_kaanon, vorlage, ziel):
    daten = []
    for r in rows:
        k = r['kaanon']; sp = r['sprachen']
        daten.append([r['name'], r['hosts'][0] if r['hosts'] else '', ' '.join(sp[:6]) + (' …' if len(sp) > 6 else ''),
                      len(sp), r['theme'] or '', KAT_CODE[r['kategorie']], r['stufe'] or 0, 1 if r['cw'] == 'NSFW' else 0,
                      ''.join(ABK[x] for x in REGELN if x in r['regel']),
                      ''.join(ABK[x] for x in REGELN if x in r['theme_kann']),
                      f"{k['name']} {k['version']}" if k else '', r['modul'], 1 if r['familie_bekannt'] else 0,
                      1 if r['manuell'] else 0, 1 if r['konto'] else 0])
    t = open(vorlage, encoding='utf-8').read()
    t = t.replace('__DATA__', json.dumps(daten, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))
    t = t.replace('__META__', json.dumps(dict(meta, nur_kaanon=[f"{v['name']} ({', '.join(v['hosts'])})" for v in nur_kaanon]),
                                         ensure_ascii=False).replace('</', '<\\/'))
    open(ziel, 'w', encoding='utf-8').write(t)

def schreibe_readme(rows, meta, nur_kaanon, ziel):
    c = collections.Counter(r['kategorie'] if r['kategorie'] != 'kandidat' else f"k{r['stufe']}" for r in rows)
    eig = [r for r in rows if r['kategorie'] == 'kaanon_eigen']
    warn = [r for r in eig if any(k in r['regel'] for k in REGELN)]
    theme_warn = collections.defaultdict(list)
    for r in eig:
        if not r['regel'] and 'DRM' in r['theme_kann'] and r['theme'] in ('gigaviewer', 'comiciviewer'):
            theme_warn[r['theme']].append(r)
    K = [r for r in rows if r['kategorie'] == 'kandidat']
    th = collections.Counter(r['theme'] for r in K if r['theme'])
    L = lambda r: r['sprachen'][0] if len(r['sprachen']) == 1 else 'mehrsprachig'
    lt = collections.defaultdict(collections.Counter)
    for r in rows: lt[L(r)][r['kategorie'] if r['kategorie'] != 'kandidat' else f"k{r['stufe']}"] += 1
    ausw = [r for r in rows if r['kategorie'] == 'kaanon_ausweg']
    kl = collections.Counter(k for r in rows if r['kategorie'] == 'nur_ausweg' for k in r['regel'])
    fmt = lambda r: ', '.join(f"{k}: {'/'.join(v)}" for k, v in r['regel'].items() if k in REGELN) or '–'
    o = []
    w = o.append
    w('# Kaanon-Abdeckungskarte\n')
    w(f"Automatisch erzeugt am {meta['erzeugt']} von `werkzeuge/abdeckung/erzeuge_karte.py`. "
      f"Community-Stand `{meta['community']}`, Store-Stand `{meta['store']}`. "
      f"{meta['module']} Community-Module, {meta['themes']} Themes, {meta['kaanon']} Kaanon-Extensions.\n")
    w('Dateien: `karte.json` (alle Daten), `karte.html` (filterbare Übersicht, im Browser öffnen), diese Zusammenfassung.\n')
    w('## Übersicht\n')
    w('| Kategorie | Websites | Bedeutung |\n|---|---:|---|')
    for k, t, d in [('kaanon_eigen', 'Kaanon · eigene Engine', 'schon im Store, mit unserer Engine gebaut'),
                    ('kaanon_ausweg', 'Kaanon · Ausweg', 'schon im Store, Community-Code unverändert'),
                    ('k1', 'Kandidat · Stufe 1', 'keine Regel-Klasse, Theme schon bei uns gebaut'),
                    ('k2', 'Kandidat · Stufe 2', 'keine Regel-Klasse, eigenständiges Modul oder neues Theme'),
                    ('k3', 'Kandidat · Stufe 3', 'keine Regel-Klasse, braucht neue Engine-Technik'),
                    ('nur_ausweg', 'Nur Ausweg möglich', 'Code löst Prüfseiten/CAPTCHAs, entschlüsselt oder signiert'),
                    ('server', 'Eigener Server', 'selbst gehostet (Komga, LANraragi …), kein Ziel für den Store')]:
        w(f'| {t} | {c[k]} | {d} |')
    w('')
    w('## Zuerst testen\n')
    w(f'**{len(warn)} eigene Extensions, deren Website im aktuellen Community-Code eine Regel-Klasse braucht.** '
      'Unsere Engine baut sie ohne diese Technik. Vermutlich liefern sie keine lesbaren Seiten mehr. '
      'Beim Handy-Test je ein Kapitel öffnen. Geht es nicht, sind sie Ausweg-Kandidaten.\n')
    for r in sorted(warn, key=lambda r: r['kaanon']['name']):
        w(f"- {r['kaanon']['name']} {r['kaanon']['version']} ({', '.join(r['hosts'][:2])}): {fmt(r)}")
    w('')
    if theme_warn:
        n = sum(len(v) for v in theme_warn.values())
        w(f'**{n} eigene Extensions auf GigaViewer/ComiciViewer.** Diese Theme-Familien verwürfeln die Bilder je Seite '
          '(Kennung `#scramble` in der Bild-Adresse). Die Community entwürfelt sie, das wäre für uns DRM. '
          'Prüfen: Kommen die Bilder in unserer Version lesbar an?\n')
        for t, lst in sorted(theme_warn.items()):
            w(f"- {t}: " + ', '.join(f"{r['kaanon']['name']} {r['kaanon']['version']}" for r in sorted(lst, key=lambda r: r['kaanon']['name'])))
        w('')
    w('## Abgleich mit den Ausweg-Extensions\n')
    w('So stuft die Karte die zehn Websites ein, für die bereits der Community-Code im Store liegt (Kontrolle der Muster):\n')
    w('| Extension | Regel-Klassen laut Karte | Prüfseite von Hand |\n|---|---|---|')
    for r in sorted(ausw, key=lambda r: r['kaanon']['name']):
        tk = ', '.join(f'{k} (Theme)' for k in r['theme_kann'])
        w(f"| {r['kaanon']['name']} | {fmt(r)}{'; ' + tk if tk else ''} | {'ja' if r['manuell'] else '–'} |")
    w('\nWo die Spalte „Regel-Klassen“ leer ist, kommt der Grund für den Ausweg von der Website selbst, z. B. eine Prüfseite, '
      'die man im WebView von Hand löst und die im Code nicht zu sehen ist. Das findet nur der Prüfstand.\n')
    w('## Die größten Hebel\n')
    w('Kandidaten je Theme (gemeinsame Bauweise). Ein Theme im Rezept-Baukasten öffnet alle seine Websites:\n')
    w('| Theme | Kandidaten | bei uns schon gebaut |\n|---|---:|---|')
    eigene = {r['theme'] for r in eig if r['theme']}
    for t, n in th.most_common(15):
        w(f"| {t} | {n} | {'ja' if t in eigene else 'nein'} |")
    w(f"| (ohne Theme, Einzelmodule) | {sum(1 for r in K if not r['theme'])} | |\n")
    w('## Nach Sprache\n')
    w('| Sprache | Module | Kaanon | Stufe 1 | Stufe 2–3 | Nur Ausweg | Eigener Server |\n|---|---:|---:|---:|---:|---:|---:|')
    for l, x in sorted(lt.items(), key=lambda kv: -sum(kv[1].values())):
        w(f"| {l} | {sum(x.values())} | {x['kaanon_eigen'] + x['kaanon_ausweg']} | {x['k1']} | {x['k2'] + x['k3']} | {x['nur_ausweg']} | {x['server']} |")
    w('')
    w('## Nur Ausweg möglich: Gründe\n')
    w('| Regel-Klasse | Module |\n|---|---:|')
    for k, n in kl.most_common(): w(f'| {k} | {n} |')
    w('')
    if nur_kaanon:
        w('## Nur bei Kaanon (kein Community-Modul für Host oder ID)\n')
        for v in nur_kaanon: w(f"- {v['name']} {v['version']} ({', '.join(v['hosts'])})")
        w('')
    w('## Methode und Grenzen\n')
    w('- Ausgewertet wird der Kotlin-Code jedes Moduls, seines Themes und seiner Bibliotheken. Kommentare werden entfernt. '
      'Texte in Meldungen („bitte im WebView lösen“) zählen nicht als Automatik, sondern als *Prüfseite von Hand*.')
    w('- **PRUEFSEITE**: Löser-Klassen/-Funktionen, bekannte Schutz-Namen (DDoS-Guard, Anubis, x-challange …), '
      'WebView-Automatik zusammen mit Schutz-Signalen, `cf_clearance` per WebView.')
    w('- **CAPTCHA**: `getTurnstileToken` (core), reCAPTCHA/hCaptcha/Turnstile im Code oder als Schlüssel.')
    w('- **DRM**: Bild-Entwürfelung (scramble, SeedRandom), Entschlüsselung (Cipher, AES-Helfer aus core, decrypt…), '
      'XOR-Verschleierung, Bibliotheken speedbinb, publus, clipstudioreader, e4p, ece, aessiv, secretstream.')
    w('- **SCHLUESSEL**: HMAC/Signaturen, Schlüsseltausch (KeyAgreement, secretstream).')
    w('- Regel-Treffer im *Theme* gelten nur als „kann“ (gestrichelt in `karte.html`). Ob eine Website den Pfad nutzt, '
      'zeigt erst der Prüfstand. Bei Themes, die wir schon bauen, entscheidet das die Regel-Prüfung je Website.')
    w('- **Stufe 1**: Theme bei uns schon gebaut. **Stufe 2**: Einzelmodul oder neues Theme. **Stufe 3**: neue Technik '
      '(Protobuf, ZIP, JS-Engine, WebView, JS-Entschleierung) oder neues Theme mit möglicher Regel-Klasse.')
    w(f"- **Login**: {sum(1 for r in rows if r['konto'])} Module bieten eine Anmeldung (Passwort/API-Schlüssel) an. Meist ist sie optional, "
      'deshalb bleibt die Kategorie unverändert. In `karte.json` steht das als `konto: true`, in `karte.html` als L.')
    w('- Ob eine Website online ist, wird nicht geprüft. Zuordnung zu Kaanon: zuerst über die Quell-ID, sonst über den Host.')
    w('- Die Karte ist eine Voreinschätzung. Verbindlich ist die Regel-Prüfung im Builder.\n')
    w('## Neu erzeugen\n')
    w('```bash\npython3 werkzeuge/abdeckung/erzeuge_karte.py --community <pfad/zu/extensions-source>\n```\n')
    w('Ohne `--community` wird der Community-Stand nach `werkzeuge/abdeckung/.community` geklont. Der Ordner ist in `.gitignore`.')
    open(ziel, 'w', encoding='utf-8').write('\n'.join(o) + '\n')


if __name__ == '__main__':
    main()
