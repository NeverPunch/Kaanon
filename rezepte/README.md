# Rezepte aus dem Community-Code

Hier entstehen die Rezepte für alle Websites, die laut Abdeckungskarte (`abdeckung/`) mit unserer
eigenen Engine gebaut werden dürfen. Die Rezepte werden aus dem Community-Code abgeleitet
(Stand: siehe `quelle.community_stand` in jeder Datei). Gebaut, signiert und gegen die echte Website
geprüft wird auf dem PC. Bis dahin hat jedes Rezept `"status": "entwurf"`.

## Stand (05.11.2026)

Alle 1.259 Kandidaten der Abdeckungskarte sind bearbeitet. Keiner ist mehr offen.

| Stufe | Kandidaten | Rezept-Entwurf | zurückgestellt |
|---|---:|---:|---:|
| 1 – Bauweise schon im Baukasten | 449 | 449 (441 Baukasten, 8 Site-Model) | 0 |
| 2 – Einzelmodul / neue Bauweise | 667 | 516 | 151 |
| 3 – neue Technik vermutet | 143 | 24 | 119 |
| **Summe** | **1.259** | **989** | **270** |

- Alle 989 Entwürfe bestehen `pruefe_rezepte.py` ohne Fehler. Keine Paketnamen oder Quell-IDs sind doppelt, weder untereinander
  noch gegenüber dem Store.
- 668 Entwürfe ohne, 321 mit 18+-Inhalten. Die meisten sind englisch (297), dann pt-BR (89), es (74), id (74), ja (73).
- **Nichts davon ist gegen die echten Websites geprüft.** Die Cloud erreicht die Websites nicht. Jedes Rezept nennt in `hinweise`, wo der Bearbeiter
  unsicher war (geratene Pagination, Annahmen zur Engine-Semantik). Diese Stellen zuerst auf dem Prüfstand ansehen.
- Warum die 270 zurückgestellt sind und welcher Engine-Baustein wie viele freischalten würde, steht in
  `ENGINE_WUENSCHE_AUS_REZEPTEN.md`. 67 davon scheitern an Regel 0014 (Login 32, Signatur 27, Prüfseite 8) und bleiben Kandidaten für den Ausweg.

### Offene Fragen an die Engine (für den ersten Prüfstand-Lauf)

Die Bearbeiter haben Konstrukte genutzt, die das Prüfskript erlaubt, die aber in keiner Vorlage belegt sind. Bitte gezielt prüfen:
- Reihenfolge innerhalb eines Feldes: `regex` → `replace` → `decode` → `template`?
- `has_next.exists`: Zählen `null`, `false`, `0` als „nicht vorhanden“? `^`-Wurzelpfad in `json_html`?
- `items: "$"` bei einem einzelnen JSON-Objekt; `script_json`/`inner` außerhalb von `pages`; `subpage` mit JSON.
- `relative`-Datumsangaben in anderen Sprachen als Englisch (viele Rezepte übersetzen per `replace` ins Englische).
- `status_map`: exakter Vergleich oder Teiltreffer, Groß-/Kleinschreibung.
- `let` aus `details` in `chapters` ist belegt (`tr.korelimanga`), in `request_by_page` und Folgeseiten nicht.
- `aes_cryptojs` mit OpenSSL-„Salted__“-Text statt Madara-JSON (`th.nekopost`).

## Ordner

| Ordner/Datei | Inhalt |
|---|---|
| `vorlagen/` | die 96 Rezepte unserer eigenen Extensions, aus den APKs gezogen. Referenz für alles Neue. |
| `stufe1/` | **Baukasten-Rezepte**: `baukasten` + `parameter` wie in den Vorlagen (Madara, MangaThemesia …). |
| `modelle/` | **vollständige Site-Models** für Websites ohne Baukasten (Stufe 2 und 3). |
| `warteschlange.json` | alle Kandidaten mit Status `offen` / `in_arbeit` / `fertig` / `zurueckgestellt` (+ Grund). |
| `ENGINE_WUENSCHE_AUS_REZEPTEN.md` | Gründe der Zurückstellungen, nach fehlendem Baustein sortiert. |
| `AGENTEN_AUFTRAG.md` | Arbeitsanweisung für Stufe-2/3-Rezepte (Mensch oder Agent). |
| `REFERENZ_SITE_MODEL.md` | die Rezeptsprache `kaanon-site-model/2`, aus den Vorlagen abgeleitet. |

## Rahmen jeder Datei (`kaanon-rezept/1`)

```json
{
  "rezept": "kaanon-rezept/1",
  "status": "entwurf",
  "extension": {"name": "…", "sprache": "en", "base_url": "https://…", "nsfw": false,
                "paket": "eu.kanade.tachiyomi.extension.en.kaanon.…",
                "quellen": [{"name": "…", "sprache": "en", "quell_id": 123, "home": "https://…"}]},
  "quelle": {"modul": "src/en/…", "community_stand": "…", "community_version": "1.6.x", "theme": "madara"},
  "baukasten": "madara", "parameter": {"apex": "…", …},          ← Stufe 1
  "modell": {"schema": "kaanon-site-model/2", …},                 ← Stufe 2/3
  "zusatz" / "hinweise": …
}
```

`quell_id` ist die ID der Community-Extension (Name + Sprache). Wie bei unseren bisherigen Extensions gilt:
Community- und Kaanon-Extension derselben Website nicht gleichzeitig installieren.

## Übernahme in den Builder (PC)

1. `stufe1/*.json`: Baukasten `baukasten` mit `parameter` aufrufen, wie bei den Vorlagen (`origin: baukasten:…`).
   `zusatz.community_einstellungen` enthält alle Community-Einstellungen wörtlich, falls die Erkundung nachschärfen soll.
2. `modelle/*.json`: `modell` ist ein fertiges Site-Model und wird wie die Vorlagen ohne `origin` gebaut.
3. Danach Prüfstand und Handy-Test wie gewohnt. Erst dann `status` auf `bereit` setzen.

## Werkzeuge

```bash
python3 werkzeuge/rezepte/vorlagen_extrahieren.py               # Vorlagen aus den APKs neu ziehen
python3 werkzeuge/rezepte/warteschlange.py aufbauen              # Warteschlange aus der Karte
python3 werkzeuge/rezepte/stufe1.py --community <extensions-source>
python3 werkzeuge/rezepte/geruest.py src/en/beispiel             # Gerüst für ein Stufe-2-Rezept
python3 werkzeuge/rezepte/pruefe_rezepte.py                      # alle Rezepte prüfen
python3 werkzeuge/rezepte/warteschlange.py stand
python3 werkzeuge/rezepte/bereinigen.py [--schreiben]          # Sprache/Paket/Dateinamen, Doppelungen
python3 werkzeuge/rezepte/engine_wuensche.py                    # Auswertung der Zurückstellungen
```
