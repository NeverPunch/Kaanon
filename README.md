# Kaanon – Extension-Store

Eigene Extensions für die Kaanon-App (Mihon-Fork), erzeugt mit dem Kaanon Extension Builder.

## Store in der App hinzufügen

1. In der App die Einstellungen öffnen → **Durchsuchen** → **Erweiterungs-Stores** (je nach App-Stand auch „Erweiterungs-Repos“).
2. **Hinzufügen** tippen und diese Adresse einfügen:

   ```
   https://raw.githubusercontent.com/NeverPunch/Kaanon/main/index.min.json
   ```

3. Unter **Durchsuchen → Erweiterungen** erscheinen danach alle Extensions dieses Stores; Updates werden dort angezeigt.

Bereits per APK installierte Kaanon-Extensions müssen nicht neu installiert werden: sie tragen dieselbe Signatur und gelten nach dem Hinzufügen nicht mehr als „Verwaist“.

Neuere App-Stände können auch direkt `https://raw.githubusercontent.com/NeverPunch/Kaanon/main/index.json` verwenden.

## Signatur

Alle APKs sind mit demselben Schlüssel signiert. SHA-256-Fingerabdruck des Zertifikats:

`cad5ae9fa0217e9063d869200cd11d0604f5d93396c42b7650084b69c1ec3de4`

Der private Schlüssel liegt nicht in diesem Repository.

## Extensions (44)

| Name | Sprache | Version | Inhalt |
|---|---|---|---|
| Lunar Manga | all | 1.6.9 | gemischt |
| MANGA Plus by SHUEISHA | all | 1.6.69 |  |
| MangaDot | all | 1.6.30 | gemischt |
| MangaFire | all | 1.6.38 | gemischt |
| NovelCool | Deutsch | 1.6.11 |  |
| Asura Scans | Englisch | 1.6.11 |  |
| Atsumaru | Englisch | 1.6.12 | gemischt |
| BatCave | Englisch | 1.6.14 |  |
| Comix | Englisch | 1.6.65 | gemischt |
| Comizy | Englisch | 1.6.11 | gemischt |
| Dynasty Scans | Englisch | 1.6.12 | 18+ |
| En-thunderscans | Englisch | 1.6.13 |  |
| Hive Scans | Englisch | 1.6.11 |  |
| Kingofshojo | Englisch | 1.6.13 |  |
| Lua Scans | Englisch | 1.6.11 | gemischt |
| Manga Demon | Englisch | 1.6.11 |  |
| Mangabat | Englisch | 1.6.12 |  |
| MangaDex | Englisch | 1.6.11 | gemischt |
| Mangafreak | Englisch | 1.6.13 | gemischt |
| MangaGeko | Englisch | 1.6.11 | gemischt |
| MangaHub | Englisch | 1.6.51 | gemischt |
| MangaK | Englisch | 1.6.11 | gemischt |
| Mangakakalot | Englisch | 1.6.13 | gemischt |
| MangaKatana | Englisch | 1.6.12 | gemischt |
| Manganato | Englisch | 1.6.15 | gemischt |
| Mangapill | Englisch | 1.6.15 |  |
| Mangaread | Englisch | 1.6.70 |  |
| Rolia Scan | Englisch | 1.6.11 |  |
| Tapas | Englisch | 1.6.11 | gemischt |
| Tappytoon | Englisch | 1.6.11 | gemischt |
| TCB Scans | Englisch | 1.6.11 |  |
| Toonily | Englisch | 1.6.12 | gemischt |
| Vortex Scans | Englisch | 1.6.11 |  |
| Webtoons.com | Englisch | 1.6.11 |  |
| Weeb Central | Englisch | 1.6.11 | gemischt |
| ManhwaWeb | Spanisch | 1.6.12 | gemischt |
| Olympus Scanlation | Spanisch | 1.6.12 |  |
| ZonaTMO | Spanisch | 1.6.11 | gemischt |
| AnimeSama | Französisch | 1.6.12 |  |
| Sushi-Scan | Französisch | 1.6.11 | gemischt |
| DAYS | Japanisch | 1.6.11 |  |
| Source | Japanisch | 1.6.11 |  |
| Source | Japanisch | 1.6.11 |  |
| Web | Japanisch | 1.6.11 |  |

## Übernommener Community-Code

Diese Extensions enthalten unveränderten Quellcode aus [keiyoushi/extensions-source](https://github.com/keiyoushi/extensions-source) (Apache License 2.0), gebaut mit eigenem Paketnamen und eigener Signatur. Lizenztext und Herkunft stehen im Ordner `lizenz/` und in der APK (`assets/kaanon_lizenz/`). **Die gleichnamige Community-Extension nicht gleichzeitig installieren** (gleiche Quell-ID).

| Name | Paket | Community-Modul | Stand |
|---|---|---|---|
| BatCave | `eu.kanade.tachiyomi.extension.en.kaanon.batcave` | `src/en/batcave` | ee661f5233b3 (2026-11-04) |
| Comix | `eu.kanade.tachiyomi.extension.en.kaanon.comix` | `src/en/comix` | 8947c372cd87 (2026-11-19) |
| Lunar Manga | `eu.kanade.tachiyomi.extension.all.kaanon.lunarmanga` | `src/all/lunaranime` | f1d882a93ef3 (2026-11-18) |
| MANGA Plus by SHUEISHA | `eu.kanade.tachiyomi.extension.all.kaanon.mangaplusbyshueisha` | `src/all/mangaplus` | 8947c372cd87 (2026-11-19) |
| MangaDot | `eu.kanade.tachiyomi.extension.all.kaanon.mangadot` | `src/all/mangadotnet` | f1d882a93ef3 (2026-11-18) |
| MangaFire | `eu.kanade.tachiyomi.extension.all.kaanon.mangafire` | `src/all/mangafire` | f1d882a93ef3 (2026-11-18) |
| MangaHub | `eu.kanade.tachiyomi.extension.en.kaanon.mangahub` | `src/en/mangahubio` | f1d882a93ef3 (2026-11-18) |

Diese Datei wird automatisch erzeugt (`python -m kaanon_builder --store`).
