# Rezepte aus dem Community-Code

Hier entstehen die Rezepte für alle Websites, die laut Abdeckungskarte (`abdeckung/`) mit unserer
eigenen Engine gebaut werden dürfen. Die Rezepte werden aus dem Community-Code abgeleitet
(Stand: siehe `quelle.community_stand` in jeder Datei). Gebaut, signiert und gegen die echte Website
geprüft wird auf dem PC. Bis dahin hat jedes Rezept `"status": "entwurf"`.

## Ordner

| Ordner/Datei | Inhalt |
|---|---|
| `vorlagen/` | die 96 Rezepte unserer eigenen Extensions, aus den APKs gezogen. Referenz für alles Neue. |
| `stufe1/` | **Baukasten-Rezepte**: `baukasten` + `parameter` wie in den Vorlagen (Madara, MangaThemesia …). |
| `modelle/` | **vollständige Site-Models** für Websites ohne Baukasten (Stufe 2 und 3). |
| `warteschlange.json` | alle Kandidaten mit Status `offen` / `in_arbeit` / `fertig` / `zurueckgestellt` (+ Grund). |
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
```
