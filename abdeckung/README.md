# Kaanon-Abdeckungskarte

Automatisch erzeugt am 2026-11-02 von `werkzeuge/abdeckung/erzeuge_karte.py`. Community-Stand `efa93f5a 2026-11-02`, Store-Stand `b5db5d2 2026-11-02`. 1448 Community-Module, 67 Themes, 106 Kaanon-Extensions.

Dateien: `karte.json` (alle Daten), `karte.html` (filterbare Übersicht, im Browser öffnen), diese Zusammenfassung.

## Übersicht

| Kategorie | Websites | Bedeutung |
|---|---:|---|
| Kaanon · eigene Engine | 95 | schon im Store, mit unserer Engine gebaut |
| Kaanon · Ausweg | 10 | schon im Store, Community-Code unverändert |
| Kandidat · Stufe 1 | 449 | keine Regel-Klasse, Theme schon bei uns gebaut |
| Kandidat · Stufe 2 | 667 | keine Regel-Klasse, eigenständiges Modul oder neues Theme |
| Kandidat · Stufe 3 | 58 | keine Regel-Klasse, braucht neue Engine-Technik |
| Nur Ausweg möglich | 162 | Code löst Prüfseiten/CAPTCHAs, entschlüsselt oder signiert |
| Eigener Server | 7 | selbst gehostet (Komga, LANraragi …), kein Ziel für den Store |

## Zuerst testen

**7 eigene Extensions, deren Website im aktuellen Community-Code eine Regel-Klasse braucht.** Unsere Engine baut sie ohne diese Technik. Vermutlich liefern sie keine lesbaren Seiten mehr. Beim Handy-Test je ein Kapitel öffnen. Geht es nicht, sind sie Ausweg-Kandidaten.

- Asura Scans 1.6.11 (asurascans.com): DRM: Bild-Entwürfelung
- Doodmanga 1.6.12 (doodmanga.com): DRM: Bild-Entwürfelung
- MangaIsekaiThai 1.6.12 (mangaisekaithai.net): DRM: Bild-Entwürfelung
- ManhuaBug.com 1.6.12 (manhuabug.com): DRM: Bild-Entwürfelung
- ManhuaThai 1.6.12 (manhuathai.com): DRM: Bild-Entwürfelung
- ManhwaBreakup 1.6.12 (manhwabreakup.com): DRM: Bild-Entwürfelung
- Temple Scan 1.6.11 (templetoons.com): CAPTCHA: CAPTCHA im Code

**8 eigene Extensions auf GigaViewer/ComiciViewer.** Diese Theme-Familien verwürfeln die Bilder je Seite (Kennung `#scramble` in der Bild-Adresse). Die Community entwürfelt sie, das wäre für uns DRM. Prüfen: Kommen die Bilder in unserer Version lesbar an?

- comiciviewer: -Mangalt- 1.6.11, Source 1.6.11, Source 1.6.11, Web 1.6.11
- gigaviewer: DAYS 1.6.11, Ourfeel 1.6.11, Source 1.6.11, Source 1.6.11

## Abgleich mit den Ausweg-Extensions

So stuft die Karte die zehn Websites ein, für die bereits der Community-Code im Store liegt (Kontrolle der Muster):

| Extension | Regel-Klassen laut Karte | Prüfseite von Hand |
|---|---|---|
| BatCave | PRUEFSEITE: Löser-Funktion/Löser-Klasse/WebView-Automatik/bekannter Schutz | – |
| Comikey | DRM: DRM-Format | – |
| Comix | PRUEFSEITE: WebView-Automatik, CAPTCHA: CAPTCHA per WebView/WebView mit CAPTCHA-Bezug, DRM: Bild-Entwürfelung | – |
| Lunar Manga | PRUEFSEITE: Löser-Funktion/Löser-Klasse, CAPTCHA: CAPTCHA im Code, DRM: Entschlüsselung, SCHLUESSEL: Signatur/HMAC/Schlüsseltausch | – |
| MANGA Plus by SHUEISHA | DRM: XOR-Verschleierung | – |
| Manga Tube | PRUEFSEITE: Löser-Funktion/Löser-Klasse/bekannter Schutz | – |
| MangaDot | – | – |
| MangaFire | PRUEFSEITE: Löser-Klasse/WebView-Automatik, CAPTCHA: CAPTCHA per WebView/WebView mit CAPTCHA-Bezug | – |
| MangaHub | –; DRM (Theme) | – |
| ManhwaRead | – | – |

Wo die Spalte „Regel-Klassen“ leer ist, kommt der Grund für den Ausweg von der Website selbst, z. B. eine Prüfseite, die man im WebView von Hand löst und die im Code nicht zu sehen ist. Das findet nur der Prüfstand.

## Die größten Hebel

Kandidaten je Theme (gemeinsame Bauweise). Ein Theme im Rezept-Baukasten öffnet alle seine Websites:

| Theme | Kandidaten | bei uns schon gebaut |
|---|---:|---|
| madara | 207 | ja |
| mangathemesia | 102 | ja |
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
| (ohne Theme, Einzelmodule) | 569 | |

## Nach Sprache

| Sprache | Module | Kaanon | Stufe 1 | Stufe 2–3 | Nur Ausweg | Eigener Server |
|---|---:|---:|---:|---:|---:|---:|
| en | 420 | 54 | 130 | 208 | 26 | 2 |
| ja | 139 | 7 | 42 | 37 | 53 | 0 |
| pt-BR | 111 | 2 | 36 | 68 | 5 | 0 |
| es | 104 | 8 | 36 | 49 | 11 | 0 |
| id | 87 | 3 | 42 | 36 | 6 | 0 |
| vi | 84 | 1 | 13 | 51 | 19 | 0 |
| mehrsprachig | 78 | 15 | 13 | 43 | 7 | 0 |
| tr | 78 | 2 | 44 | 26 | 6 | 0 |
| ar | 59 | 1 | 29 | 24 | 5 | 0 |
| all | 56 | 1 | 6 | 45 | 0 | 4 |
| fr | 54 | 4 | 14 | 31 | 5 | 0 |
| zh | 53 | 0 | 1 | 39 | 13 | 0 |
| th | 44 | 5 | 29 | 8 | 2 | 0 |
| ru | 31 | 0 | 0 | 30 | 1 | 0 |
| it | 17 | 0 | 11 | 6 | 0 | 0 |
| ko | 9 | 0 | 1 | 7 | 1 | 0 |
| uk | 7 | 1 | 0 | 5 | 1 | 0 |
| pt | 5 | 0 | 0 | 5 | 0 | 0 |
| zh-Hans | 4 | 0 | 0 | 4 | 0 | 0 |
| ca | 2 | 0 | 0 | 2 | 0 | 0 |
| zh-Hant | 2 | 0 | 0 | 1 | 1 | 0 |
| other | 1 | 0 | 0 | 0 | 0 | 1 |
| bg | 1 | 0 | 1 | 0 | 0 | 0 |
| cs | 1 | 0 | 1 | 0 | 0 | 0 |
| de | 1 | 1 | 0 | 0 | 0 | 0 |

## Nur Ausweg möglich: Gründe

| Regel-Klasse | Module |
|---|---:|
| DRM | 134 |
| PRUEFSEITE | 23 |
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
- **DRM**: Bild-Entwürfelung (scramble, SeedRandom), Entschlüsselung (Cipher, AES-Helfer aus core, decrypt…), XOR-Verschleierung, Bibliotheken speedbinb, publus, clipstudioreader, e4p, ece, aessiv, secretstream.
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
