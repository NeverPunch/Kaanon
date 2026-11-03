#!/usr/bin/env python3
"""Stufe 1: Baukasten-Rezepte aus dem Community-Code ableiten.

Für jede Aufgabe der Warteschlange mit Stufe 1 und einem Theme, für das unser Builder einen
Baukasten hat, entsteht rezepte/stufe1/<sprache>.<name>.json:

  {"rezept": "kaanon-rezept/1", "extension": {...}, "quelle": {...},
   "baukasten": "madara", "parameter": {"apex": …, …},
   "zusatz": {"community_einstellungen": {...}, "hinweise": [...]}}

Die Parameter sind dieselben, die der Builder in den Vorlagen benutzt (rezepte/vorlagen). Was sich
aus dem Community-Code ableiten lässt, wird übernommen (Verzeichnis, Datumsformat, Kapitelabruf …),
sonst gilt der häufigste Wert der Vorlagen. Alle übrigen Community-Einstellungen stehen wörtlich unter
`zusatz.community_einstellungen`. Die Erkundung im Builder kann damit nachschärfen.

Aufruf: python3 werkzeuge/rezepte/stufe1.py --community <pfad/extensions-source> [--index index.json]
"""
import argparse, collections, glob, json, os, re, sys, urllib.request
from urllib.parse import urlparse

HIER = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.normpath(os.path.join(HIER, '..', '..'))
REZ = os.path.join(STORE, 'rezepte')
sys.path.insert(0, HIER)
import warteschlange as ws  # noqa: E402

INDEX_URL = 'https://raw.githubusercontent.com/keiyoushi/extensions/repo/index.json'

# ------------------------------------------------------------------------------------------------
def kotlin(modul_pfad):
    return '\n'.join(open(f, encoding='utf-8', errors='replace').read()
                     for f in sorted(glob.glob(os.path.join(modul_pfad, '**', '*.kt'), recursive=True)))

def einstellungen(code):
    """Alle `override val/fun X = …` mit ihrem Ausdruck (eine Zeile, gekürzt)."""
    out = {}
    for m in re.finditer(r'override (?:val|fun) (\w+)(?:\(\))?(?:\s*:\s*[\w<>?, ]+)?\s*(?:get\(\))?\s*=\s*([^\n]+)', code):
        out.setdefault(m.group(1), m.group(2).strip()[:200])
    return out

def text(e, k):
    v = e.get(k)
    if v is None: return None
    m = re.match(r'^"((?:[^"\\]|\\.)*)"', v)
    return m.group(1) if m else None

def muster_und_locale(ausdruck):
    if not ausdruck: return None, None
    p = re.search(r'ofPattern\(\s*"([^"]+)"', ausdruck) or re.search(r'SimpleDateFormat\(\s*"([^"]+)"', ausdruck) \
        or re.match(r'^"([^"]+)"', ausdruck)
    loc = None
    m = re.search(r'forLanguageTag\(\s*"([^"]+)"', ausdruck) or re.search(r'Locale\(\s*"([^"]+)"', ausdruck)
    if m: loc = m.group(1)
    elif re.search(r'Locale\.(US|ENGLISH|ROOT|UK)', ausdruck): loc = 'en'
    else:
        m = re.search(r'Locale\.(FRENCH|GERMAN|ITALIAN|JAPANESE|KOREAN|CHINESE)', ausdruck)
        if m: loc = {'FRENCH': 'fr', 'GERMAN': 'de', 'ITALIAN': 'it', 'JAPANESE': 'ja', 'KOREAN': 'ko', 'CHINESE': 'zh'}[m.group(1)]
    return (p.group(1) if p else None), loc

def reihenfolge(muster):
    if not muster: return None
    s = re.sub(r"'[^']*'", '', muster)
    pos = {k: s.find(k) for k in 'dMy' if k in s}
    return ''.join(sorted(pos, key=pos.get)).lower().replace('m', 'm') if len(pos) == 3 else None

# ------------------------------------------------------------------------------------------------
# Baukästen: Community-Einstellungen → Parameter
# ------------------------------------------------------------------------------------------------
def p_madara(code, e, h):
    p = {}
    p['list_mode'] = 'html' if re.search(r':\s*MadaraNoAjax\b', code) else 'ajax'
    cm = re.search(r'chapterMode\s*=\s*ChapterMode\.(\w+)', code)
    p['chapter_mode'] = {'MangaPage': 'page', 'AdminAjax': 'api', 'MangaAjax': 'ajax',
                         'MangaAjaxPaginated': 'ajax_paged', 'MangaAjaxQuery': 'ajax'}.get(cm.group(1) if cm else '', 'ajax')
    # Ohne Angabe: „ajax“ – das findet die Erkundung des Builders bei den meisten Madara-Seiten (22 von 29 Vorlagen).
    if cm and cm.group(1) == 'MangaAjaxQuery': h.append('ChapterMode.MangaAjaxQuery: im Baukasten wie ajax angesetzt, prüfen')
    p['manga_dir'] = (text(e, 'mangaSubString') or 'manga').strip('/')
    muster, loc = muster_und_locale(e.get('chapterDateFormat') or e.get('dateFormat'))
    muster = re.sub(r'(?<!y)yyy(?!y)', 'yyyy', muster) if muster else muster
    p['date_format'] = muster or 'MMMM d, yyyy'
    # Die Sprache zählt nur bei ausgeschriebenen Monatsnamen (MMM/MMMM); sonst wie in den Vorlagen „en“.
    p['date_locale'] = (loc or 'en') if 'MMM' in p['date_format'] else 'en'
    p['date_selector'] = text(e, 'chapterDateSelector') or 'span.chapter-release-date'
    p['image_origin'] = 'keep'; p['image_retry'] = 'no'; p['page_mode'] = 'style_list'; p['skip_premium'] = 'no'
    if 'supportsLatest' in e and 'false' in e['supportsLatest']: h.append('Community: keine „Neueste“-Liste')
    if 'filterNonMangaItems' in e: h.append(f"filterNonMangaItems = {e['filterNonMangaItems']}")
    return p

def p_mangathemesia(code, e, h):
    muster, loc = muster_und_locale(e.get('datePattern') and f'"{text(e, "datePattern")}"' or e.get('dateFormat'))
    if e.get('dateFormat') and not loc: _, loc = muster_und_locale(e['dateFormat'])
    # date_order: in allen Vorlagen „dmy“ (Reihenfolge für rein numerische Daten), unabhängig vom Community-Muster
    p = dict(date_locale=loc or 'en', date_order='dmy',
             manga_dir=(text(e, 'mangaUrlDirectory') or '/manga').strip('/') or 'manga',
             page_mode='img', search_mode='title')
    if 'pageSelector' in e: h.append(f"Seiten-Selektor der Community: {e['pageSelector']}")
    h.append('page_mode: img angesetzt; liefert die Website die Bilder per ts_reader-Skript, „script“ wählen')
    return p

def p_foolslide(code, e, h):
    return dict(popular_path='directory', skip_numeric_names='0', url_modifier=text(e, 'urlModifier') or '')

def p_initmanga(code, e, h):
    if text(e, 'mangaUrlDirectory'): h.append(f"Manga-Verzeichnis der Community: {text(e, 'mangaUrlDirectory')}")
    return dict(latest_slug=text(e, 'latestUrlSlug') or 'recently-updated',
                popular_slug=text(e, 'popularUrlSlug') or 'manga-ranking')

def p_iken(code, e, h):
    pp = re.search(r'\d+', e.get('perPage', '')) if e.get('perPage') else None
    return dict(api_prefix='api.', chapter_mode='api', per_page=pp.group(0) if pp else '18',
                sort_mode='filename' if 'true' in e.get('sortPagesByFilename', '') else 'order')

def p_loneseal(code, e, h):
    api = text(e, 'apiUrl')
    if not api:
        m = re.search(r'"(https://api\.[^"]+)"', code)
        api = m.group(1) if m else None
    if not api: h.append('api_base unbekannt: im Builder per Erkundung ermitteln')
    return dict(api_base=api or '', chapter_title='yes')

def p_zeistmanga(code, e, h):
    return dict(chapter_cat=text(e, 'chapterCategory') or 'Chapter', page_sel='auto', series_label=text(e, 'mangaCategory') or 'Series')

def p_wpcomics(code, e, h):
    lang = e.get('_sprache', 'vi')
    p = dict(chapter_mode='json_id', description_mode='full', latest_path='', pages_suffix='',
             popular_path=text(e, 'popularPath') or 'truyen-tranh-hot', search_path=text(e, 'searchPath') or 'tim-truyen',
             ui_lang=lang if lang in ('vi', 'en') else 'vi')
    h.append('wpcomics: Vorgaben stammen aus NetTruyen; Pfade per Erkundung prüfen')
    return p

def p_mmrcms(code, e, h):
    return dict(item_path=text(e, 'itemPath') if text(e, 'itemPath') is not None else '',
                lang=e.get('_sprache', 'en'), popular_mode='filter')

def p_galleryadults(code, e, h):
    lang = text(e, 'mangaLang') or 'english'
    h.append('galleryadults: Leser-Art (reader) und Seitenstil per Erkundung prüfen')
    return dict(page_style='query', popular_path=f'language/{lang}/popular/', reader='json',
                search_key=text(e, 'basicSearchKey') or 'q')

def p_pizzareader(code, e, h): return dict(api_path='/api')
def p_comiciviewer(code, e, h): return {}
def p_vinetheme(code, e, h): return {}
def p_gigaviewer(code, e, h): return dict(list_keyword='の', list_mode='graphql')
def p_mangacatalog(code, e, h):
    h.append('mangacatalog: Seite listet feste Reihen (sourceList der Community), layout per Erkundung prüfen')
    return dict(layout='tailwind')

BAUKASTEN = {k[2:]: v for k, v in globals().items() if k.startswith('p_')}

# ------------------------------------------------------------------------------------------------
def paket_name(name, ersatz=''):
    """Paketteil aus dem Namen: Akzente entfernen (ộ → o, đ → d), nur a-z0-9.
    Bleibt dabei (z. B. bei koreanischen/chinesischen Namen) zu wenig übrig, gilt der Ordnername des Moduls."""
    import unicodedata
    t = unicodedata.normalize('NFKD', name.lower().replace('đ', 'd'))
    t = re.sub(r'[^a-z0-9]', '', ''.join(c for c in t if not unicodedata.combining(c)))
    if len(t) < 3 and ersatz:
        t = re.sub(r'[^a-z0-9]', '', ersatz.rstrip('/').rsplit('/', 1)[-1].lower())
    return t or 'x'

def extension_block(r, ke):
    """Name, Sprache, Basis-URL, 18+, Paketname und Quellen (mit Community-ID) aus dem Community-Index."""
    quellen = [dict(name=s['name'], sprache=s['language'], quell_id=int(s['id']), home=s['homeUrl'].rstrip('/'))
               for s in ke['sources']]
    sprachen = sorted({q['sprache'] for q in quellen})
    lang = sprachen[0] if len(sprachen) == 1 else 'all'
    ext = dict(name=ke['name'], sprache=lang, base_url=quellen[0]['home'], nsfw=r['cw'] == 'NSFW',
               paket=f"eu.kanade.tachiyomi.extension.{lang}.kaanon.{paket_name(ke['name'], r['modul'])}", quellen=quellen)
    return ext, quellen

def dateiname(ext):
    return f"{ext['sprache']}.{ext['paket'].rsplit('.', 1)[-1]}"

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--community', required=True)
    ap.add_argument('--index', default=INDEX_URL)
    ap.add_argument('--stand', default='')
    a = ap.parse_args()
    idx = json.load(urllib.request.urlopen(a.index) if a.index.startswith('http') else open(a.index, encoding='utf-8'))
    kei = {e['packageName']: e for e in idx['extensionList']['extensions']}
    karte = {r['modul']: r for r in json.load(open(os.path.join(STORE, 'abdeckung', 'karte.json'), encoding='utf-8'))['module']}
    stand = a.stand or json.load(open(os.path.join(STORE, 'abdeckung', 'karte.json'), encoding='utf-8'))['meta']['community']
    os.makedirs(os.path.join(REZ, 'stufe1'), exist_ok=True)
    liste = json.load(open(ws.DATEI, encoding='utf-8'))
    n = collections.Counter()
    for x in liste:
        if x['stufe'] != 1 or x['theme'] not in BAUKASTEN or x['status'] not in ('offen',): continue
        r = karte[x['modul']]
        ke = kei.get(r['pkg'])
        if not ke:
            n['ohne_index'] += 1; continue
        code = kotlin(os.path.join(a.community, r['modul']))
        e = einstellungen(code)
        ext, quellen = extension_block(r, ke)
        sprachen = sorted({q['sprache'] for q in quellen})
        e['_sprache'] = sprachen[0]
        hinweise = []
        params = BAUKASTEN[x['theme']](code, e, hinweise)
        e.pop('_sprache', None)
        apex = urlparse(ext['base_url']).netloc.lower().removeprefix('www.')
        params = {'apex': apex, **params}
        kurz = dateiname(ext)
        rezept = {
            'rezept': 'kaanon-rezept/1', 'status': 'entwurf',
            'extension': ext,
            'quelle': dict(modul=r['modul'], community_stand=stand, community_version=ke['versionName'], theme=x['theme']),
            'baukasten': x['theme'], 'parameter': params,
            'zusatz': dict(community_einstellungen=e, hinweise=hinweise),
        }
        ziel = os.path.join(REZ, 'stufe1', kurz + '.json')
        json.dump(rezept, open(ziel, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        ws.setze(x['modul'], status='fertig', datei=os.path.relpath(ziel, STORE), wer='stufe1.py')
        n[x['theme']] += 1
    print(dict(n), sum(v for k, v in n.items() if k != 'ohne_index'), 'Rezepte')

if __name__ == '__main__':
    main()
