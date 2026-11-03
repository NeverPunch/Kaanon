# Arbeitsanweisung: Rezepte aus dem Community-Code (Stufe 2/3)

Für Menschen und Agenten gleich. Gemeinsame Warteschlange: jeder nimmt die nächste freie Aufgabe, erledigt sie,
nimmt die nächste. Nichts doppelt, keiner wartet.

**Vorher lesen:** `rezepte/REFERENZ_SITE_MODEL.md`, `rezepte/README.md`. Vorlagen: `rezepte/vorlagen/*.json` (Feld `modell`).
Gute Beispiele: HTML `en.mangapill`, `de.niadd`, `en.mangakatana` · JSON-API `en.asurascans`, `en.atsumaru` ·
Text/RSC `en.drakescans` · next_data `en.tappytoon` · POST/then/let `en.asmhentai`, `ja.source`.
Schon fertige Stufe-2-Rezepte (`rezepte/modelle/`) sind ebenfalls Vorlagen, besonders für Websites desselben Themes.

**Community-Code:** Pfad zu `keiyoushi/extensions-source` (Kotlin), Community-Index `index.json`. Websites werden nicht abgerufen.

## Ablauf je Aufgabe
1. `python3 werkzeuge/rezepte/warteschlange.py nimm --wer <name> --stufe <n>` → Modulpfad (KEINE = fertig).
2. `python3 werkzeuge/rezepte/geruest.py <modul> --index <index.json>` → `rezepte/modelle/<datei>.json` mit `extension`/`quelle`.
3. Kotlin-Code des Moduls (und ggf. `lib-multisrc/<theme>`) ganz lesen; nachbilden, was er tut:
   Anfragen (URL, Methode, Header, Formular/JSON), Pagination, Selektoren/JSON-Pfade, Datum, Status, Bildliste.
4. Modell unter `modell` eintragen (popular, latest, search, details, chapters, pages; headers/rate_limit wie im Code).
   Unsicherheiten als kurze Sätze in `hinweise`.
5. `python3 werkzeuge/rezepte/pruefe_rezepte.py rezepte/modelle/<datei>.json` → keine FEHLER.
6. `python3 werkzeuge/rezepte/warteschlange.py fertig <modul> --datei rezepte/modelle/<datei>.json`
   Nicht ausdrückbar (WebView, JS ausführen, unbekannte Entschlüsselung/Entwürfelung außer aes_cryptojs/packer/base64/grid/rects,
   Protobuf, Signaturen, Login zum Lesen, Rekursion): Gerüst löschen,
   `python3 werkzeuge/rezepte/warteschlange.py zurueck <modul> --grund "<kurz, konkret>"`.

## Regeln
- Keine erfundenen Schlüssel oder Platzhalter. Was es in keiner Vorlage gibt → zurückstellen.
- Regel 0014: keine Prüfseiten/CAPTCHAs lösen, kein DRM, keine Bezahlschranken umgehen, keine selbst erzeugten
  Schlüssel/Signaturen. Gesperrte Kapitel per `skip`/`locked` auslassen.
- Nur eigene `rezepte/modelle/*.json` anlegen; die Warteschlange nur über das Skript ändern.
