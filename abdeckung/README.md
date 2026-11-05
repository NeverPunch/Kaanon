# Kaanon-Abdeckungskarte

Automatisch erzeugt am 2026-11-05 von `werkzeuge/abdeckung/erzeuge_karte.py`. Community-Stand `efa93f5a 2026-11-02`, Store-Stand `009e230 2026-11-05`. 1448 Community-Module, 67 Themes, 106 Kaanon-Extensions.

Dateien: `karte.json` (alle Daten), `karte.html` (filterbare Übersicht, im Browser öffnen), diese Zusammenfassung.

## Übersicht

| Kategorie | Websites | Bedeutung |
|---|---:|---|
| Kaanon · eigene Engine | 95 | schon im Store, mit unserer Engine gebaut |
| Kaanon · Ausweg | 10 | schon im Store, Community-Code unverändert |
| Kandidat · Stufe 1 | 449 | keine Regel-Klasse, Theme schon bei uns gebaut |
| Kandidat · Stufe 2 | 667 | keine Regel-Klasse, eigenständiges Modul oder neues Theme |
| Kandidat · Stufe 3 | 143 | keine Regel-Klasse, braucht neue Engine-Technik oder Entschleierung |
| Nur Ausweg möglich | 77 | Code löst Prüfseiten/CAPTCHAs, nutzt Leser-DRM oder Schlüsseltausch/Signaturen |
| Eigener Server | 7 | selbst gehostet (Komga, LANraragi …), kein Ziel für den Store |

## Stand der Rezepte

Für 989 Kandidaten liegt ein Rezept-Entwurf in `rezepte/` (Stufe 1 als Baukasten, sonst als Site-Model), 270 sind mit Grund zurückgestellt (`rezepte/warteschlange.json`, Auswertung in `rezepte/ENGINE_WUENSCHE_AUS_REZEPTEN.md`). Geprüft gegen die echten Websites wird auf dem PC.

## Zuerst testen

**1 eigene Extensions, deren Website im aktuellen Community-Code eine Regel-Klasse braucht.** Beim Handy-Test je ein Kapitel öffnen. Geht es nicht, sind sie Ausweg-Kandidaten.

- Temple Scan 1.6.11 (templetoons.com): CAPTCHA: CAPTCHA im Code

**1 eigene Extensions, deren Website inzwischen verschleiert, unser Rezept aber nicht entschlüsselt oder entwürfelt.** Das ist keine Regel-Frage, sondern eine Technik-Frage: Das Rezept braucht einen passenden `transform`/`decode`-Schritt. Beim Handy-Test zuerst prüfen.

- Asura Scans 1.6.11 (asurascans.com): Bild-Entwürfelung

## Abgleich mit den Ausweg-Extensions

So stuft die Karte die zehn Websites ein, für die bereits der Community-Code im Store liegt (Kontrolle der Muster):

| Extension | Regel-Klassen laut Karte | Prüfseite von Hand |
|---|---|---|
| BatCave | PRUEFSEITE: Löser-Funktion/Löser-Klasse/WebView-Automatik/bekannter Schutz | – |
| Comikey | DRM: DRM-Format | – |
| Comix | PRUEFSEITE: WebView-Automatik, CAPTCHA: CAPTCHA per WebView/WebView mit CAPTCHA-Bezug | – |
| Lunar Manga | PRUEFSEITE: Löser-Funktion/Löser-Klasse, CAPTCHA: CAPTCHA im Code, SCHLUESSEL: Signatur/HMAC/Schlüsseltausch | – |
| MANGA Plus by SHUEISHA | – | – |
| Manga Tube | PRUEFSEITE: Löser-Funktion/Löser-Klasse/bekannter Schutz | – |
| MangaDot | – | – |
| MangaFire | PRUEFSEITE: Löser-Klasse/WebView-Automatik, CAPTCHA: CAPTCHA per WebView/WebView mit CAPTCHA-Bezug | – |
| MangaHub | –; VERSCHLEIERUNG (Theme) | – |
| ManhwaRead | – | – |

Wo die Spalte „Regel-Klassen“ leer ist, kommt der Grund für den Ausweg von der Website selbst, z. B. eine Prüfseite, die man im WebView von Hand löst und die im Code nicht zu sehen ist. Das findet nur der Prüfstand.

## Die größten Hebel

Kandidaten je Theme (gemeinsame Bauweise). Ein Theme im Rezept-Baukasten öffnet alle seine Websites:

| Theme | Kandidaten | bei uns schon gebaut |
|---|---:|---|
| madara | 207 | ja |
| mangathemesia | 105 | ja |
| zeistmanga | 27 | ja |
| comiciviewer | 25 | ja |
| gigaviewer | 15 | ja |
| keyoapp | 14 | ja |
| yiimanga | 12 | nein |
| mangacatalog | 12 | ja |
| mangahub | 10 | nein |
| pizzareader | 9 | ja |
| initmanga | 8 | ja |
| masonry | 7 | nein |
| uzaymanga | 7 | nein |
| galleryadults | 6 | ja |
| iken | 6 | ja |
| (ohne Theme, Einzelmodule) | 648 | |

## Nach Sprache

| Sprache | Module | Kaanon | Stufe 1 | Stufe 2–3 | Nur Ausweg | Eigener Server |
|---|---:|---:|---:|---:|---:|---:|
| en | 420 | 54 | 130 | 220 | 14 | 2 |
| ja | 139 | 7 | 42 | 65 | 25 | 0 |
| pt-BR | 111 | 2 | 36 | 71 | 2 | 0 |
| es | 104 | 8 | 36 | 53 | 7 | 0 |
| id | 87 | 3 | 42 | 39 | 3 | 0 |
| vi | 84 | 1 | 13 | 63 | 7 | 0 |
| mehrsprachig | 78 | 15 | 13 | 46 | 4 | 0 |
| tr | 78 | 2 | 44 | 29 | 3 | 0 |
| ar | 59 | 1 | 29 | 28 | 1 | 0 |
| all | 56 | 1 | 6 | 45 | 0 | 4 |
| fr | 54 | 4 | 14 | 31 | 5 | 0 |
| zh | 53 | 0 | 1 | 49 | 3 | 0 |
| th | 44 | 5 | 29 | 10 | 0 | 0 |
| ru | 31 | 0 | 0 | 30 | 1 | 0 |
| it | 17 | 0 | 11 | 6 | 0 | 0 |
| ko | 9 | 0 | 1 | 7 | 1 | 0 |
| uk | 7 | 1 | 0 | 5 | 1 | 0 |
| pt | 5 | 0 | 0 | 5 | 0 | 0 |
| zh-Hans | 4 | 0 | 0 | 4 | 0 | 0 |
| ca | 2 | 0 | 0 | 2 | 0 | 0 |
| zh-Hant | 2 | 0 | 0 | 2 | 0 | 0 |
| other | 1 | 0 | 0 | 0 | 0 | 1 |
| bg | 1 | 0 | 1 | 0 | 0 | 0 |
| cs | 1 | 0 | 1 | 0 | 0 | 0 |
| de | 1 | 1 | 0 | 0 | 0 | 0 |

## Nur Ausweg möglich: Gründe

| Regel-Klasse | Module |
|---|---:|
| DRM | 37 |
| PRUEFSEITE | 23 |
| VERSCHLEIERUNG | 23 |
| SCHLUESSEL | 20 |
| CAPTCHA | 13 |

## Nur bei Kaanon (kein Community-Modul für Host oder ID)

- Comizy 1.6.11 (comizy.io)
- Kiraproject 1.6.12 (kiraproject.lat)
- MangaNato 1.6.11 (manganato.gg)

## Methode und Grenzen

- Ausgewertet wird der Kotlin-Code jedes Moduls, seines Themes und seiner Bibliotheken. Kommentare werden entfernt. Texte in Meldungen („bitte im WebView lösen“) zählen nicht als Automatik, sondern als *Prüfseite von Hand*.
- **PRUEFSEITE**: Löser-Klassen/-Funktionen, bekannte Schutz-Namen (DDoS-Guard, Anubis, x-challange …), WebView-Automatik zusammen mit Schutz-Signalen, `cf_clearance` per WebView.
- **CAPTCHA**: `getTurnstileToken` (core), reCAPTCHA/hCaptcha/Turnstile im Code oder als Schlüssel.
- **DRM**: DRM-Formate (e4p, Widevine …) und die Leser-DRM-Bibliotheken speedbinb, publus, clipstudioreader, e4p, ece, aessiv, secretstream.
- **Verschleierung** (keine Regel-Klasse, Technik → Stufe 3): Bild-Entwürfelung, Entschlüsselung mit einem Schlüssel, den die Website selbst ausliefert, XOR. Unsere Engine kann davon schon `aes_cryptojs`, `packer`, `base64` sowie Raster- und Rechteck-Entwürfelung (GigaViewer, ComiciViewer, Madara).
- **SCHLUESSEL**: HMAC/Signaturen, Schlüsseltausch (KeyAgreement, secretstream).
- Regel-Treffer im *Theme* gelten nur als „kann“ (gestrichelt in `karte.html`). Ob eine Website den Pfad nutzt, zeigt erst der Prüfstand. Bei Themes, die wir schon bauen, entscheidet das die Regel-Prüfung je Website.
- **Stufe 1**: Theme bei uns schon gebaut. **Stufe 2**: Einzelmodul oder neues Theme. **Stufe 3**: neue Technik (Protobuf, ZIP, JS-Engine, WebView, JS-Entschleierung) oder neues Theme mit möglicher Regel-Klasse.
- **Login**: 47 Module bieten eine Anmeldung (Passwort/API-Schlüssel) an. Meist ist sie optional, deshalb bleibt die Kategorie unverändert. In `karte.json` steht das als `konto: true`, in `karte.html` als L.
- Ob eine Website online ist, wird nicht geprüft. Zuordnung zu Kaanon: zuerst über die Quell-ID, sonst über den Host.
- Die Karte ist eine Voreinschätzung. Verbindlich ist die Regel-Prüfung im Builder.

## Neu erzeugen

```bash
python3 werkzeuge/abdeckung/erzeuge_karte.py --community <pfad/zu/extensions-source>
```

Ohne `--community` wird der Community-Stand nach `werkzeuge/abdeckung/.community` geklont. Der Ordner ist in `.gitignore`.
