# Handoff: Rezeptsprache und Rezept-Entwürfe (Stand 05.11.2026)

Für die PC-Sitzung. Alles liegt im Store-Repo `NeverPunch/Kaanon` auf dem Branch `claude/peaceful-dirac-h63y4t`
(letzter Stand ab Commit `8cbc162`). Noch nicht auf `main`.

## Worum es geht

Aus dem Community-Code (`keiyoushi/extensions-source`, Stand `efa93f5` vom 02.11.) wurden Rezepte für alle Websites
abgeleitet, die laut Abdeckungskarte mit unserer eigenen Engine gebaut werden dürfen. Die Rezepte sind in **unserer**
Rezeptsprache `kaanon-site-model/2` geschrieben. Ihren Wortschatz habe ich aus den 96 Rezepten gezogen, die in unseren
eigenen APKs stecken. Die Engine-Quelle hatte ich in der Cloud nicht.

**Nichts davon ist gegen echte Websites geprüft.** Alle Rezepte haben `"status": "entwurf"`.

## Stand

| Stufe | Kandidaten | Rezept-Entwurf | zurückgestellt |
|---|---:|---:|---:|
| 1 – Bauweise schon im Baukasten | 449 | 449 (441 Baukasten, 8 Site-Model) | 0 |
| 2 – Einzelmodul / neue Bauweise | 667 | 516 | 151 |
| 3 – neue Technik vermutet | 143 | 24 | 119 |
| **Summe** | **1.259** | **989** | **270** |

- Baukasten-Rezepte (`rezepte/stufe1/`): madara 205, mangathemesia 102, zeistmanga 27, comiciviewer 25, gigaviewer 15,
  mangacatalog 12, pizzareader 9, initmanga 8, je 6 iken/wpcomics/galleryadults/foolslide/vinetheme, je 4 mmrcms/loneseal.
- Site-Models (`rezepte/modelle/`): 548 Dateien, jede mit `hinweise` zu ihren Unsicherheiten.
- Prüfskript: 0 Fehler. Keine doppelten Paketnamen oder Quell-IDs, weder untereinander noch gegenüber dem Store.
- 668 Entwürfe ohne, 321 mit 18+-Inhalten. Sprachen: en 297, pt-BR 89, es 74, id 74, ja 73, tr 61, vi 58, all 53, ar 51 …

## Wo was liegt

| Pfad | Inhalt |
|---|---|
| `rezepte/README.md` | Überblick, Rahmenformat `kaanon-rezept/1`, Übernahme in den Builder |
| `rezepte/REFERENZ_SITE_MODEL.md` | die Rezeptsprache, wie sie aus den Vorlagen hervorgeht (inkl. „Vorsicht“-Abschnitt) |
| `rezepte/vorlagen/` | die 96 Site-Models unserer eigenen Extensions (Referenz, aus den APKs gezogen) |
| `rezepte/stufe1/` | 441 Baukasten-Rezepte (`baukasten` + `parameter`) |
| `rezepte/modelle/` | 548 vollständige Site-Models |
| `rezepte/warteschlange.json` | jede Website mit Status, Bearbeiter, Datei bzw. Grund der Zurückstellung |
| `rezepte/ENGINE_WUENSCHE_AUS_REZEPTEN.md` | Zurückstellungen nach fehlendem Baustein sortiert |
| `rezepte/AGENTEN_AUFTRAG.md` | Arbeitsanweisung für neue Rezepte (Mensch oder Agent) |
| `werkzeuge/rezepte/` | Skripte: Vorlagen ziehen, Stufe-1-Umsetzer, Gerüst, Prüfen, Warteschlange, Bereinigen, Engine-Wünsche |
| `abdeckung/` | Abdeckungskarte (README, karte.json, karte.html) mit Rezept-Stand je Website |
| `docs/ARBEITSPAKET_2026-11-02.md` | die Builder-Punkte 1–8 vom 02.11. (noch offen, siehe unten) |

## Reihenfolge für die PC-Sitzung

### 1. Übernahme in den Builder (kleiner Schritt, zuerst)
Der Builder braucht einen **Rezept-Eingang** für den Rahmen `kaanon-rezept/1`:
- `stufe1/*.json`: Baukasten `baukasten` mit `parameter` aufrufen, genau wie die Vorlagen (`origin: baukasten:…`).
  `zusatz.community_einstellungen` enthält alle Community-Overrides wörtlich. Die Erkundung des Builders kann damit
  nachschärfen.
- `modelle/*.json`: `modell` ist ein fertiges Site-Model und wird wie die Vorlagen ohne `origin` gebaut.
- Aus `extension` kommen: Name, Sprache, Basis-URL, 18+, Paketname (`eu.kanade.tachiyomi.extension.<sprache>.kaanon.<name>`)
  und `quellen` mit `quell_id`. Die ID ist die der Community-Extension, wie bei unseren bisherigen Extensions.

### 2. Engine-Semantik klären (vor dem großen Prüfstand-Lauf)
Die Bearbeiter mussten einige Bedeutungen aus den Vorlagen erschließen. Ein Blick in den Engine-Code beantwortet sie.
Danach `REFERENZ_SITE_MODEL.md` ergänzen:
1. Reihenfolge innerhalb eines Feldes: `regex` → `replace` → `decode` → `template`? (viele Rezepte hängen daran)
2. `has_next.exists`: Zählen `null`, `false`, `0` als „nicht vorhanden“? Funktioniert der `^`-Wurzelpfad in `json_html`?
3. `items: "$"` bei einem einzelnen JSON-Objekt; `script_json`/`inner` außerhalb von `pages`; `subpage` mit JSON.
4. `relative`-Datumsangaben in anderen Sprachen (viele Rezepte übersetzen per `replace` vorher ins Englische).
5. `status_map`: exakter Vergleich oder Teiltreffer, Groß-/Kleinschreibung.
6. `let` aus `details` in `chapters` ist belegt (`tr.korelimanga`). Gilt es auch in `request_by_page` und auf Folgeseiten?
7. `aes_cryptojs` mit OpenSSL-„Salted__“-Text statt Madara-JSON (`th.nekopost`).
8. Verkettete `vars` (`{v.x}` in einer zweiten `vars`-Anfrage, `pt-BR.sagradoimperiodabritannia`).
9. `rate_limit` gilt für alle Hosts, also auch für Bilder?

Hilft eine Antwort nicht weiter, gilt die Regel aus `AGENTEN_AUFTRAG.md`: nur verwenden, was in einer Vorlage belegt ist.

### 3. Prüfstand in Wellen
- **Zuerst Stufe 1, Madara und MangaThemesia** (307 Websites). Der Umsetzer trifft bei unseren eigenen Websites 91 % der
  Parameter. Abweichungen kommen meist von `chapter_mode`, `date_format` und `manga_dir`. Die Erkundung kann sie korrigieren.
- Danach die übrigen Baukästen, dann `modelle/`. In jeder Datei zuerst die `hinweise` lesen. Dort steht, was geraten ist
  (meist Weiterblättern oder Kapitel-Folgeseiten).
- Handy-Test wie bisher, Ergebnis nach `pruefung/handy.tsv` (Arbeitspaket Punkt 4).
- Bestandenes Rezept: `"status": "bereit"`.

### 4. Engine-Bausteine nach Nutzen
Aus `ENGINE_WUENSCHE_AUS_REZEPTEN.md` (270 Zurückstellungen, eine Website kann mehrfach zählen):

| Baustein | Websites |
|---|---:|
| Entschlüsselung/Entwürfelung über aes_cryptojs/packer/grid/rects hinaus (AES-CBC/GCM mit Rohschlüssel, XOR, Streifen, Seed-Permutationen) | 105 |
| Vorab-Anfragen (Token/Nonce/CSRF) in Listen und Kapiteln (`then`/`let` außerhalb von `pages`) | 60 |
| WebView/JavaScript ausführen | 33 |
| Auswahl per Platzhalter (`?feld={u.slug}`, Abgleich in Gesamtlisten) | 31 |
| Framework-Datenformate (SvelteKit-devalue, Livewire, Inertia, Qwik, Server-Actions) | 26 |
| Eltern-/Geschwisterzugriff, Verzweigung je Eintrag | 24 |
| Zahlenbereich erzeugen (Kapitel/Seiten 1..N) | 20 |
| Bild-Anfragen mit Header/POST je Bild | 18 |
| Protobuf/ZIP | 16 |
| Cursor-Blättern (Wert aus voriger Antwort/Header) | 14 |
| Iteration über JSON-Objekte (Maps) | 13 |

Dazu kommen kleine Bausteine, die viele Rezepte robuster machen: Entdoppeln, Kapitel sortieren, `{page+1}` in Selektoren,
Antwort-Header lesen (`X-WP-TotalPages`), String umkehren, URL-Dekodieren, `{lang}` je Quelle.

**Regel 0014 vorher prüfen.** „Entschlüsselung“ zählt nur, wenn die Website den Schlüssel selbst mitliefert. So haben wir es
bei Madara (`aes_cryptojs`) und GigaViewer (`grid`) schon gehalten. 67 Zurückstellungen sind reine Regel-Fälle (Login 32,
Signatur 27, Prüfseite 8) und bleiben Ausweg-Kandidaten.

Nach jedem neuen Baustein: Vorlage anlegen, `pruefe_rezepte.py` kennt ihn dann automatisch. Die passenden Websites in der
Warteschlange mit `warteschlange.py frei <modul>` wieder freigeben und neu bearbeiten.

### 5. Builder-Punkte 1–8 (Arbeitspaket vom 02.11.)
Weiter offen, Details in `docs/ARBEITSPAKET_2026-11-02.md`. Am dringendsten:
- **Punkt 1:** Sperre gegen das Ausführen von Ausweg-Code auf dem PC.
- **Punkt 8a:** Regel-Anzeige für batcave/manga-tube.
- **Punkt 3:** doppelte Quell-IDs bei Manganato und den vier „Source“.

**Korrektur gegenüber dem Arbeitspaket:** Verschleierung, deren Schlüssel die Website selbst mitliefert, ist **keine**
Regel-Klasse. Die Karte ist entsprechend angepasst. Die Warnung zu GigaViewer/ComiciViewer entfällt. Bei Asura Scans fehlt
unserem Rezept vermutlich die Bild-Entwürfelung. Temple Scan braucht ein CAPTCHA, das spricht für den Ausweg.

## Entscheidungen, die ich getroffen habe (bitte gegenlesen)

- **Zeit-Tokens** (md5 aus Zeitstempel + festem Text, wie in unserer Rolia-Scan-Extension) sind erlaubt, wenn sie schon in
  einer Vorlage vorkommen (`en.mangataro`). Wird das bei Rolia beanstandet, gilt es hier ebenso.
- **Öffentliche Zugangsschlüssel**, die die Website jedem Besucher ausliefert (Supabase-anon-Key u. ä.), sind erlaubt
  (z. B. `ar.despairmanga`, `en.webdexscans`, `es.reizucomics`). Sie sind nicht selbst erzeugt.
- **Mehrsprachige Module:** Bildet ein Modell nur eine Sprache sauber ab, wurde `quellen` auf diese gekürzt. Sprache und
  Paket sind angepasst, und es steht in `hinweise`. Nie dieselben Inhalte unter falscher Sprache.
- **Gesperrte/kostenpflichtige Kapitel** werden per `skip`/`locked` ausgelassen, nie umgangen.

## Weiterarbeiten am PC

```bash
python3 werkzeuge/rezepte/warteschlange.py stand
```

```bash
python3 werkzeuge/rezepte/pruefe_rezepte.py
```

```bash
python3 werkzeuge/rezepte/bereinigen.py
```

```bash
python3 werkzeuge/rezepte/engine_wuensche.py
```

```bash
python3 werkzeuge/abdeckung/erzeuge_karte.py --community <pfad/zu/extensions-source>
```

Neue Community-Stände: Karte neu erzeugen, `warteschlange.py aufbauen` (bestehende Status bleiben erhalten),
`stufe1.py --community …` für neue Stufe-1-Websites, den Rest nach `rezepte/AGENTEN_AUFTRAG.md`.
Die Skripte brauchen nur Python 3 ohne Zusatzpakete.
