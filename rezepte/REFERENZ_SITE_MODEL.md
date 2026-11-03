# Referenz: Rezeptsprache `kaanon-site-model/2`

Abgeleitet aus den 96 Rezepten, die in unseren eigenen APKs stecken (`rezepte/vorlagen/`).
Wer ein neues Rezept schreibt, sucht sich zuerst die ähnlichste Vorlage und weicht nur dort ab,
wo die Website es verlangt. Erfundene Schlüssel sind verboten. Das Prüfskript
(`werkzeuge/rezepte/pruefe_rezepte.py`) lässt nur Schlüssel zu, die in den Vorlagen vorkommen.

## Aufbau

```
{
  "schema": "kaanon-site-model/2",
  "headers": {...}, "image_headers": {...}, "cookies": {...}, "rate_limit": {"permits": 2, "period_ms": 1000},
  "vars": {...},                       # selten: Werte mit Ablaufzeit (Token o. ä.)
  "popular": LISTE, "latest": LISTE, "search": LISTE,
  "details": DETAILS, "chapters": KAPITEL, "pages": SEITEN
}
```
`popular`, `details`, `chapters`, `pages` sind Pflicht. `latest` und `search` sind optional, aber erwünscht.

## Anfragen (`request`)

- Als Text: eine URL-Vorlage, z. B. `"{base}/manga/page/{page}/?m_orderby=views"`.
- Als Objekt: `{"url": …, "method": "POST", "headers": {…}, "form": {…}}` bzw. `"body"` + `"content_type"`,
  oder für GraphQL `{"json": {"query": …, "variables": {…}}}`.
- Sonderwerte: `"{abs_url}"` = absolute URL des Mangas/Kapitels; in `chapters` heißt `"request": "details"`:
  „dieselbe Seite wie die Details, nicht neu laden“.
- `request_by_page`: abweichende Anfrage für bestimmte Seitennummern (z. B. `{"1": "details"}`).

### Platzhalter
| Platzhalter | Bedeutung |
|---|---|
| `{base}` | Basis-URL der Website (ohne `/` am Ende) |
| `{page}` / `{page0}` | Seitennummer ab 1 / ab 0 |
| `{offset}` | `(page-1) * page_size` |
| `{query}` / `{query_raw}` | Suchtext URL-kodiert / roh (z. B. für Formulare) |
| `{abs_url}`, `{url}` | absolute bzw. relative URL des aktuellen Eintrags |
| `{u.NAME}` | Wert aus `url_vars` (Regex-Gruppe aus der Eintrags-URL) |
| `{l.NAME}` | Wert aus `let` |
| `{f.PFAD}` | Feld aus dem aktuellen JSON-Eintrag |
| `{v.NAME}` | Wert aus `vars` |
| `{value}` | Ergebnis des Feldes (in `template`) |
| `{g1}`, `{g2}` … | Regex-Gruppen (in `transform`) |
| `[[ … ]]` | optionaler Abschnitt, entfällt, wenn ein Platzhalter darin leer ist |

## Formate (`format`)

`html` (Standard), `json`, `text` (Regex über Rohtext), `json_html` (JSON, dessen Feld HTML enthält → `html_path`),
`script_json` / `scripts` (JSON aus `<script>`), `next_data` (Next.js `__NEXT_DATA__`).

## Selektoren und Pfade

- **HTML:** CSS-Selektor, optional `@attribut`: `a@href`, `img@img` (bestes Bild aus src/data-src/srcset …),
  `@ownText` (nur eigener Text), `@html`, `@title`, `@content`, `@style` …
  Ohne `@` wird der Text genommen.
- **JSON:** Punkt-Pfad, `*` für alle Listenelemente, `?feld=wert` als Filter, `$` = Wurzel:
  `"series.genres.*.name"`, `"readableProduct.pageStructure.pages.*.?type=main"`.
- **Liste** statt Einzelwert = Ausweichkette: der erste Treffer gewinnt.
- **Objekt** statt Text = Feld mit Verarbeitung:
  `{"path": …, "regex": …, "group": 1, "replace": [[muster, ersatz]], "template": "…{value}…",
    "decode": "json|html|html_text|base64|packer|aes_cryptojs", "key": …, "const": "…",
    "all": true, "join": ", ", "default": …, "union": true, "regex_all": true}`.

## Listen (`popular`, `latest`, `search`)

```
"request": …, "format": …, "items": SELEKTOR/PFAD,
"fields": {"url": …, "title": …, "cover": …},
"has_next": {"exists": SEL} | {"full": true} | {"lt": [pfad_seite, pfad_gesamt]} | {"total": PFAD} | {"const": false},
"page_size": 24, "skip": BEDINGUNG, "page_map": [...], "html_path": PFAD, "client_filter": true
```
`has_next.full`: Es gibt eine nächste Seite, solange die Seite voll ist (`page_size` Einträge).

## Details

```
"request": "{abs_url}", "url_vars": {"slug": "/series/([^/]+)"}, "let": {...},
"fields": {"title", "cover", "description", "author", "artist", "genres", "status"},
"status_map": {"ongoing": 1, "completed": 2, "licensed": 3, "publishing finished": 4, "cancelled": 5, "hiatus": 6}
```
Statuswerte wie in Mihon: 1 laufend, 2 abgeschlossen, 3 lizenziert, 4 Veröffentlichung beendet, 5 abgebrochen, 6 pausiert.

## Kapitel

```
"request": …, "items": …, "fields": {"url", "name", "date", "number", "scanlator"},
"date_format": "iso" | "epoch_s" | "epoch_ms" | "MMMM d, yyyy" | ["dd/MM/yyyy", "relative"],
"date_locale": "en", "reverse": true, "skip": BEDINGUNG, "locked": {"path": …, "equals": …},
"paging": {"has_next": {...}, "max_pages": 30}, "join": {...}
```
`"relative"` versteht Angaben wie „2 hours ago“. `skip`: `{"any": [pfad, …]}`, `{"path": …, "equals": …}`,
`{"path": …, "regex": …}`, `{"path": …, "is_future": "iso"}`. Gesperrte/kostenpflichtige Kapitel werden übersprungen,
nie umgangen.

## Seiten

```
"request": "{abs_url}", "items": SEL/PFAD, "image": "@img" | PFAD,
"script_regex": "(?s)var pages = (\\[.*?\\]);",  # Bildliste aus Skript
"block_regex": …, "inner": {...}, "then": [ … ], "subpage": {...},
"transform": {...}, "referer": "chapter", "include"/"exclude": REGEX, "sort": {...}
```
- `inner`: Wert entpacken (z. B. `decode: aes_cryptojs` mit `key`) und darin weiter auswerten.
- `then`: Folgeanfragen nacheinander, Ergebnisse über `let` weiterreichen.
- `subpage`: Jede Bildseite ist eine eigene HTML-Seite, das Bild steht dort.
- `transform`: Bild-Entwürfelung, die die Engine kann: `{"type": "grid", …}` (GigaViewer/ComiciViewer) und
  `{"type": "rects", …}` (Madara). Andere Verfahren kann die Engine nicht → Stufe 3, kein Rezept.

## Grenzen (Regel 0014)

Keine Prüfseiten oder CAPTCHAs lösen, kein Leser-DRM, keine Bezahlschranken umgehen, keine selbst erzeugten Schlüssel
oder Signaturen. Verschleierung, deren Schlüssel die Website selbst mitliefert (z. B. Madara-`chapter_data`), ist erlaubt.
Muss ein Rezept dafür etwas erfinden, das in keiner Vorlage vorkommt, wird die Website zurückgestellt.
