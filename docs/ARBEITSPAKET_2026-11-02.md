# Arbeitspaket Builder 3.15 / Engine 11 (Stand 02.11.2026)

Erstellt in der Cloud-Sitzung vom 02.11. Grundlage: Store `NeverPunch/Kaanon` (Commit `718fef6`) und der
aktuelle Community-Stand (`keiyoushi/extensions-source` `efa93f5` vom 02.11., Index mit 1.448 Extensions).

**Grenze dieser Sitzung:** Der Builder-Quellcode (Engine, Prüfstand, Wartung, Wächter, Regel-Prüfung,
Katalog) und der Signierschlüssel liegen nur auf dem PC. In der Cloud war das nicht erreichbar, weder
als Repo noch als freigegebener Ordner. Hier stehen deshalb fertige Entscheidungen und Vorgaben. Die
Umsetzung im Code folgt in der PC-Sitzung, in der Reihenfolge unten. Im Store direkt erledigt ist nur
Punkt 8b.

Reihenfolge (Marathon, ein Fundament):
**A** = vor dem Wartungslauf 05.11. (Punkt 1, Punkt 8a)
**B** = mit dem ersten Neubau danach (Punkte 3, 2, 4)
**C** = Engine 11 (Punkt 6)
**D** = großer Schritt (Punkt 7), erst wenn B und C stabil laufen.
Punkt 5 ist der Lauf selbst.

---

## 1. Prüfstand-Referenz an Regel 0014 anpassen (A, höchste Priorität)

**Entscheidung:** Es gibt eine gemeinsame Torfunktion, die *jede* Stelle fragt, bevor Community-Code
bei uns gegen eine Website läuft: Prüfstand-Referenz, Wartungs-Probeläufe und Wächter.

```
darf_ausfuehren(modul) -> (ja/nein, grund)
  nein, wenn die Regel-Prüfung für das Modul (inkl. core/lib-multisrc-Anteile) eine dieser Klassen meldet:
    PRUEFSEITE   – Prüfseite/Challenge/Guard lösen (auch automatisiert per WebView)
    CAPTCHA
    DRM          – Entschlüsselung geschützter Inhalte / Bild-Descrambling mit Schlüssel
    PAYWALL      – Bezahlschranke umgehen
    SCHLUESSEL   – selbst erzeugte Schlüssel/Signaturen
  sonst ja
```

* Prüfstand: Bei „nein“ wird keine Referenz gemessen. Status: `Referenz übersprungen (Regel 0014: <Klasse>)`.
  Die eigene Engine wird weiter gegen die echte Website gemessen. Ohne Referenz zählt nur, ob Liste,
  Details, Kapitel und Seiten geliefert werden.
* Ausweg-Extensions (die 10) werden von uns **nur gebaut, nie ausgeführt**. Auch ein Wartungs-Update
  prüft nur Bau, Diff und Regel-Anzeige. Der Funktionstest kommt vom Handy (Punkt 4).
* Das Tor nutzt dieselbe Erkennung wie die Regel-Anzeige. Deshalb gehört Punkt 8a dazu, sonst rutscht
  batcave durch.
* Test: Prüfstand mit batcave/manga-tube als Referenz → übersprungen. Mit einem harmlosen Modul
  (z. B. Mangapill) → läuft wie bisher. Eintrag als P-067.

## 8a. Regel-Anzeige untertreibt bei batcave und manga-tube (A, gehört zu 1)

Befund im Community-Code (Stand 02.11.):

| Modul | Was der Code tut | Richtige Klasse |
|---|---|---|
| `src/en/batcave` | `DleGuardResolver`: lädt die Website automatisch in einer unsichtbaren WebView (`runWebViewBlocking`) und wartet auf das Cookie `__guard_trust` („DLE Guard“) | **PRUEFSEITE (automatisch, WebView)** |
| `src/de/mangatube` | `ChallengeInterceptor`: liest `window.__challange`, **rechnet die Aufgabe selbst aus** (`solve(arg1,arg2,op)`) und schickt die Lösung per `x-challange-*`-Header | **PRUEFSEITE (selbst gelöst, Code)** |

Neue Erkennungsmuster für die Regel-Prüfung:
* `runWebViewBlocking`/`WebView` + Warten auf ein bestimmtes Cookie → PRUEFSEITE.
* Klassen/Funktionen `*Challenge*`, `*Guard*Resolver`, `solve*`, Header `x-challange-*`/`x-challenge-*` → PRUEFSEITE.
* Nur der Hinweis „Open in WebView“ ohne Automatik bleibt wie bisher eine Info.
Die Anzeige sperrt weiterhin nichts. Sie nennt die Klasse nur richtig, und das Tor aus Punkt 1 liest sie.

## 2. Umzüge ins Paket übernehmen (B)

**Entscheidung:** Ein erkannter Umzug wird bei *eigenen* Extensions in das Rezept übernommen.
Bei Ausweg-Extensions übernehmen wir ihn nie selbst, dort warten wir auf das Community-Update
(Regel: unverändert übernehmen).

Ablauf in der Wartung:
1. Der Wächter meldet `alter Host → neuer Host` (Weiterleitung 301/302 auf eine andere Domain).
2. Der Umzug gilt als **bestätigt**, wenn eine der beiden Bedingungen erfüllt ist:
   (a) Die Community hat denselben Host im aktuellen Stand.
   (b) Zwei Wartungsläufe hintereinander melden ihn **und** der Prüfstand besteht auf dem neuen Host.
3. Dann: `baseUrl` im Rezept = neuer Host, alter Host → `mirrorUrls` (bleibt für alte Links lesbar),
   versionCode +1, Neubau, Eintrag im Bericht „Umzug übernommen“.
4. **Die Quell-ID bleibt gleich.** Sie hängt an Name und Sprache, nicht am Host. Die Bibliothek bleibt
   also erhalten. Im Code muss sichergestellt sein, dass der Host nicht in die ID einfließt.

Aktuelle Fälle:

| Extension | Store heute | Community heute | Wächter | Folge |
|---|---|---|---|---|
| Mangakakalot | `mangakakalot.gg` | `kakamanga.com` (en.mangakakalot 1.6.28) | → kakamanga | bestätigt nach (a) → übernehmen |
| Manganato | `natomanga.com` | `natomanga.com` | → manganami | noch nicht bestätigt → Weg (b) |

## 3. Doppelte Quell-IDs und falsche Namen (B)

**Befund:** Zwei Doppelungen und mehrere falsch ausgelesene Namen. Ursache ist vermutlich, dass der Name
aus dem Seitentitel oder Klassennamen statt aus dem Community-Modul gelesen wird.

| Paket | Name heute | ID heute | Name Community | ID Community |
|---|---|---|---|---|
| manganato (natomanga.com) | Manganato | 6978911398642923430 | Manganato | 1024627298672457456 |
| manganatogg (manganato.gg) | MangaNato | 6978911398642923430 | – (kein Modul) | – |
| bibibicomiccom | Source | 7890969987970576735 | Bibibi Comic | 3726193166490568923 |
| shonenjumppluscom | Source | 7890969987970576735 | Shonen Jump+ | 5161357527629843269 |
| source (comic-growl.com) | Source | 7890969987970576735 | Comic Growl (Sprache `all`) | 299423548273637501 |
| tonarinoyjjp | Source | 7890969987970576735 | Tonari no Young Jump | 5726629019734498294 |
| days (comic-days.com) | DAYS | eigene | Comic Days | 5332604811772266259 |
| web (younganimal.com) | Web | eigene | Young Animal | 3590997004623427971 |
| mangalt | -Mangalt- | eigene | Mangalt | 1153097454471755439 |

**Entscheidungen (Bibliotheks-Schutz zuerst):**
1. **Grundregel „ID einfrieren“:** Ändert sich ein Name, schreibt der Builder die bisherige ID fest ins
   Paket (`id = <alte ID>`). Ein neuer Name zerstört so keine Bibliothek.
2. **Manganato (natomanga) behält** 6978911398642923430. Das ist die Hauptseite und am
   wahrscheinlichsten in Benutzung.
   **manganato.gg** heißt künftig **„MangaNato.gg“** und bekommt die neue ID **3580403709178109269**.
3. **Die vier „Source“:** Alle bekommen den Community-Namen **und die Community-ID**, wie in der
   Tabelle. Die alte gemeinsame ID 7890969987970576735 behält *nur* die Extension, die du tatsächlich
   nutzt (siehe Frage unten). Nutzt du keine, behält sie keine. Bisher konnte ohnehin immer nur eine
   der vier gleichzeitig geladen sein.
4. **DAYS, Web, -Mangalt-:** Community-Name, ID einfrieren (Regel 1).
5. **Neue Sperre im Veröffentlichen:** Kommt eine Quell-ID in zwei Paketen des Stores vor, bricht die
   Veröffentlichung ab und nennt beide Pakete. Genauso bei einem Namen wie `Source`, `Web`, `Home` oder
   einem Namen, der nur aus Satzzeichen/Großbuchstaben besteht. Damit kommt das nicht wieder.
6. **Namensquelle künftig:** Gibt es ein Community-Modul für denselben Host, nimmt der Builder dessen
   Namen. Nur sonst den Seitentitel.

Weitere 45 Quellen haben eine andere ID als das Community-Modul für denselben Host, z. B. „Deathtollscans“
gegenüber „Death Toll Scans“. Das ist **kein Fehler** und wird **nicht** angefasst, sonst gingen die
Bibliotheken verloren. Folge: Community- und Kaanon-Extension laufen dort nebeneinander, und ein Wechsel
geht über Mihons „Migrieren“.

**Offene Frage an dich (nur du kannst sie beantworten):** Hast du in der Bibliothek Titel aus
bibibi-comic, Shonen Jump+, Comic Growl oder Tonari no Young Jump? Wenn ja, aus welcher davon?
Ohne Antwort gilt Entscheidung 3 mit „keine“.

## 4. Handy-Ergebnisse festhalten (B)

**Entscheidung:** eine einfache Textdatei im Builder-Arbeitsbereich, `pruefung/handy.tsv`, eine Zeile
je Test:

```
datum        paket                         version  ergebnis  notiz
2026-11-03   en.kaanon.mangahub            1.6.49   ok        1 Manga, 1 Kapitel
2026-11-03   all.kaanon.mangafire          1.6.35   fehler    Seiten leer
```

* Im Katalog gilt ein Paket als **„bereit (Handy)“**, wenn der *neueste* Eintrag für genau diese Version
  `ok` ist. Eine neue Version setzt es auf „Handy-Test offen“ zurück.
* Die Kategorie „bereit (PC)“ wird gleich behandelt (Spalte bleibt, Quelle `pc`). So fließen beide
  endlich in die Zahlen ein.
* Für die Ausweg-Extensions ist das der **einzige** Funktionsnachweis (siehe Punkt 1).
* Eintragen: Ergebnisse einfach im Chat durchgeben, die PC-Sitzung schreibt die Zeilen.

## 5. Erster echter Wartungslauf, Do 05.11. 03:00 (Beobachtung)

Danach prüfen und in P-068 festhalten:
- [ ] Folgetermin angelegt (genau einer)?
- [ ] Laufzeit je Phase (Wächter / Community-Abgleich / Bau / Prüfstand / Veröffentlichen). Bisher
      ungefähr 40 Minuten. Größter Block?
- [ ] **Echter Testfall für Community-Updates:** Die Community hat MangaDot inzwischen auf
      versionCode **28** (wir: 27). Der Lauf muss das erkennen, unverändert übernehmen und die NOTICE
      mit `core` neu schreiben. Damit erledigt sich auch 8b im APK.
- [ ] Hat die Wartung keinen Ausweg-Code gegen Websites ausgeführt (nach Punkt 1)?
- [ ] Ist der Berichtstext ohne Rückfrage verständlich: Was ist neu? Was ist gesperrt? Was wartet auf
      das Handy?
- [ ] Achtung beim Abgleich: Die Community baut inzwischen mit einem eigenen Gradle-Plugin
      (`alias(kei.plugins.extension)`, Block `keiyoushi { name = …; versionCode = …; source { … } }`).
      Wenn sich die Form der `build.gradle` gegenüber unserem Stand geändert hat, muss die
      Paketnamen-Ersetzung beim Übernehmen das neue Format kennen.

## 6. Engine-Baustein „bei Fehler erneuern und einmal wiederholen“ (C, Engine 11)

Neuer Rezept-Baustein (REZEPT_SCHEMA):

```
wiederholung:
  bei:        [status 401, status 403, status 419, json_feld "error", leere_antwort]
  erneuere:   <Name eines Rezeptschritts, z. B. "token_holen">   # normale Seitenanfrage
  maximal:    1
```

* Ablauf: Anfrage → Fehler passt zu `bei` → Schritt `erneuere` ausführen (Ergebnis ersetzt Token oder
  Cookie im Engine-Zustand) → Anfrage genau **ein** weiteres Mal. Scheitert sie wieder, gibt es einen
  sichtbaren Fehler und keine Schleife.
* Regel-Grenze: `erneuere` darf nur öffentlich ausgelieferte Werte holen, die alle beim normalen Besuch
  bekommen, z. B. einen Token aus Seiten-HTML oder -JS oder ein Session-Cookie. Wird dafür eine
  Prüfseite, ein Rechenrätsel oder ein Schlüssel gebraucht, ist das eine Regel-Klasse aus Punkt 1, und
  der Baustein bricht ab.
* Damit lässt sich MangaHub als eigene Extension zurückholen. Danach Prüfstand gegen die
  Community-Referenz (falls das Tor sie erlaubt), Handy-Test, und dann ersetzt die eigene Version die
  Ausweg-Version (versionCode höher, gleiche ID).
* ENGINE_WUENSCHE: Eintrag als erledigt markieren, sobald gebaut.

## 7. Festen Community-Stand im Arbeitsbereich erneuern (D)

Unser Stand ist vom 08.10. Der aktuelle Stand `efa93f5` ist vom 02.11. Dazwischen liegen über 400
Änderungen und der Umbau auf das neue Gradle-Plugin (siehe Punkt 5).

Plan:
1. Neuer Arbeitsstand in einem eigenen Ordner, der alte bleibt bis zum Ende unberührt.
2. Unsere Engine-Anbindung an `core` gegen den neuen Stand bauen, dann die Bruchstellen auflisten.
3. Alle eigenen Pakete neu bauen, mit versionCode +1 für alle und unveränderten IDs (Prüfskript:
   ID-Liste vorher gleich ID-Liste nachher, sonst Abbruch).
4. Kompletter Prüfstand-Lauf und Vergleich mit dem letzten Lauf: Es darf nichts schlechter werden.
5. Alles in **einem** Store-Commit veröffentlichen, mit HANDBUCH- und CHANGELOG-Eintrag. Danach den
   alten Stand löschen.
Erst angehen, wenn die Punkte 1 bis 6 eine Wartung lang stabil gelaufen sind.

## 8b. MangaDot-NOTICE (erledigt im Store, 02.11.)

Der Community-Code von MangaDot importiert `keiyoushi.*` (= `core`). In der Store-Kopie
`lizenz/NOTICE-…mangadot.txt` steht die Zeile „Gemeinsame Bibliothek: core“ jetzt mit einem
Nachtrag-Vermerk. Die NOTICE im APK wird beim nächsten MangaDot-Update richtig. Das Update auf 28
steht schon bereit (Punkt 5).

---

## Für die Doku

* PROTOKOLL P-067: Tor `darf_ausfuehren` (Punkt 1), Regel-Klassen batcave und manga-tube korrigiert
  (Punkt 8a).
* PROTOKOLL: Entscheidungen zu Punkt 3 (ID einfrieren, Duplikat-Sperre, Namensquelle Community).
* REZEPT_SCHEMA: Baustein `wiederholung` (Punkt 6).
* HANDBUCH: Umzüge (Punkt 2), `pruefung/handy.tsv` (Punkt 4).
