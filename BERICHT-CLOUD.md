# Bericht: Überarbeitung tracetour.de (Oktober 2026)

**Kurzfassung**
1. Die Kindertour hatte einen echten Live-Fehler: Wer die Hauptfrage einer Station vor der Bonus-Aufgabe beantwortete, kam nicht weiter. Behoben und alle 8 Stationen automatisch durchgespielt.
2. Die Krimi-Tour blieb leer, sobald die Kartenbibliothek nicht lud (Funkloch, blockiertes CDN). Behoben; die Karte liegt jetzt auf dem eigenen Server, die Tour läuft notfalls auch ohne Karte.
3. Die Startseite erklärt jetzt in einem Satz, was TraceTour ist, zeigt Startpunkte, Sprachen und Preis „ab 7,99 €“ und beantwortet 15 statt 8 Kauffragen. Sie lädt 745 KB statt 2,2 MB.
4. Offline-Modus, Barrierefreiheit (0 Fehler im WCAG-AA-Prüfer axe-core) und Datenschutzerklärung sind auf Stand. Die Datenschutzerklärung beschrieb die Code-Prüfung vorher falsch.
5. Vor dem Verkaufsstart musst du 4 Dinge entscheiden: Widerrufsbutton (seit Juni 2026 Pflicht), aktuelle Widerrufsbelehrung, Testcodes im Quelltext, Gerätelimit pro Ticket. Details stehen unten jeweils mit einer Empfehlung.

Alles liegt auf dem Branch `claude/vigilant-sagan-jhhh1c` als Draft-PR gegen `main`. Live ist noch nichts, erst wenn du mergst.

---

## 1. Was ich geändert habe (vorher → nachher)

### Startseite (index.html)

| Bereich | Vorher | Nachher |
|---|---|---|
| Hero-Text | „Kriminalfälle, Rätsel und echte Geschichte vereint in einer gamifizierten Audio-Experience für die Hosentasche …“ | „Ein Stadtspiel zum Mitlaufen: Du folgst einer Spur durch die Altstadt, löst Rätsel an echten Orten und hörst die Geschichte direkt im Ohr. Läuft im Handy-Browser – ohne App, ohne Termin.“ Darunter drei Chips: Krimi für Erwachsene · Drachenabenteuer für Kinder · ab 7,99 € |
| Hero-Etikett | „TraceTour“ (doppelt zum Logo) | „Jetzt in Tübingen · weitere Städte folgen“ |
| Haupt-Button | „MIT CODE STARTEN“ (Fremde haben keinen Code) | „TOUREN ANSEHEN“; daneben „CODE EINLÖSEN“ für Käufer |
| Faktenleiste | 17 Stationen · 120 Min · 1869 „Das Jahr des Rätsels“ · 1790 „Traces zu sammeln“ (Spieljargon) | 2 Touren · 60–120 Minuten zu Fuß · 0 Apps zu installieren · ab 7,99 € einmalig |
| Tourkarten | „1790 Traces“, „Audio-Experience“; Button führte in den Login | Startpunkt („Start am Schloss“ / „Start am Marktplatz“) und Sprache sichtbar; Button „Zu den Tickets“, darunter „Schon einen Code? …“ |
| Kinderkarte auf dem Handy | Oberer Teil (Badge) wurde abgeschnitten | Karte wächst mit dem Text, nichts wird abgeschnitten |
| Englisch-Hinweis Kindertour | fehlte | In der englischen Fassung: „in German“ / „German only“ |
| „So funktioniert's“ | „Code erhalten“, „Stadt erkunden“, „Urkunde sichern“ | „Ticket holen“ (12 Monate einlösbar, auf gutes Wetter warten), „Losgehen“ (48 Stunden ab Start), „Rätsel lösen“ (Tipps, Urkunde) |
| Über uns | „… durch interaktives Storytelling lebendig machen“ | „Unser Ziel: Dass du nach der Tour sagst: ‚Da bin ich schon hundertmal vorbeigelaufen – und hab das nie gesehen.‘“ |
| Preise | Badge „Beliebt“ (vor Verkaufsstart nicht belegbar) | „Spartipp“; Untertitel erklärt 12 Monate / 48 Stunden; sichtbarer Hinweis „Ticketverkauf startet in Kürze“ |
| Zahlungsarten | FAQ nannte Klarna, Preisbereich nicht | Überall einheitlich „z. B. Kreditkarte, Apple Pay oder Google Pay“ |
| FAQ | 8 Fragen | 15 Fragen, neu: Wo Start/Ende? · Regen? · Gruppe? · Verschenken? · Englisch? · Weg/Kinderwagen? · Was ist echt, was erfunden? |
| Weitere Städte | München/Stuttgart „Bald verfügbar“ | „In Planung“ + Link „Schreib uns deine Wunschstadt“ |
| Schluss-Banner | „Kein Gerät nötig außer deinem Smartphone.“ / „MIT CODE STARTEN“ | „Handy, Kopfhörer, bequeme Schuhe – mehr brauchst du nicht.“ / „TICKET SICHERN“ |
| Sprache | Immer Deutsch, bis man umschaltet | Erkennt Englisch aus dem Browser (Touristen), Wahl wird gemerkt |
| Verkaufsstart | Stripe-Links müssten in 4 Buttons von Hand eingebaut werden | Eine Zeile `CHECKOUT_LINKS` oben im Script; leer = alles wie bisher |

### Erwachsenen-App (app.html)

| Problem | Vorher | Nachher |
|---|---|---|
| Kartenbibliothek lädt nicht | Spielbildschirm komplett leer, Tour unspielbar | Leaflet liegt lokal; falls die Karte trotzdem fehlt, erscheinen die Stationen ohne Karte |
| Leeres Antwortfeld abgeschickt | Zählte als Fehlversuch; nach 3× wurde die Station übersprungen (Punkte weg) | Wird ignoriert, Cursor springt ins Feld |
| Schlechtes Netz beim Code-Prüfen | Button hing endlos auf „…“ | Nach 15 s klare Meldung „Bitte gleich nochmal versuchen“ |
| Code ohne Bindestriche getippt / mit Leerzeichen | „Ungültiger Zugangscode“ | Wird automatisch zu `TT-XXXX-XXXX` |
| Kindertour-Code in der Krimi-App | Nur Text „Öffne die Kindertour“ | Mit Link zur Kindertour, Code wird dort vorausgefüllt (und umgekehrt) |
| Name vergessen | Feld bekam stumm den Fokus | Hinweis „Bitte gib zuerst deinen Ermittlernamen ein …“ |
| Fehlermeldungen | Verschwanden nach 3 Sekunden | Bleiben stehen, bis man tippt |
| GPS verweigert | Nichts passierte | Einmaliger Hinweis, dass die Karte trotzdem alle Stationen zeigt |
| Entfernung zur Station | Nur beim Stationswechsel berechnet, beim ersten Halt oft gar nicht | Läuft beim Gehen live mit |
| Trace-Chat | Eingaben und Antworten wurden als HTML eingefügt; hing bei Funkloch | Als Text dargestellt (fett und Zeilenumbrüche gehen), 15-s-Timeout |
| Offline-Download | Beim ersten Besuch nur „Bitte Seite neu laden“; meldete „fertig“, auch wenn Dateien fehlten | Startet sofort, meldet fehlende Dateien und erlaubt Wiederholen |
| Urkunde teilen abgebrochen | Startete trotzdem einen Download | Abbrechen heißt Abbrechen; lange Namen passen auf die Urkunde |
| „Fortschritt löschen“ | Nur im Debug-Modus sichtbar (Datenschutzerklärung versprach es allen) | Für alle sichtbar, mit doppelter Rückfrage |
| Zoomen | Per `user-scalable=no` gesperrt (Barrierefreiheit) | Zoom erlaubt; Eingabefelder 16 px, damit das iPhone nicht ungefragt hineinzoomt; Tempo-Knopf statt Mini-Auswahlliste |

### Kindertour (kinder.html)

| Problem | Vorher | Nachher |
|---|---|---|
| **Hauptfrage vor Bonus-Aufgabe beantwortet** | JavaScript-Fehler, Station ließ sich nicht lösen (live nachgestellt) | Behoben, komplette Tour automatisch durchgespielt |
| Offline | Kein Service Worker, kein Download | Knopf „Für unterwegs speichern (ca. 10 MB)“ |
| Geteilter Link / Fremde ohne Code | Sackgasse: nur Code-Feld, kein Weg zum Kauf | „Noch keinen Code? Hier gibt's die Kindertour“; geteilte Urkunde verlinkt auf `tracetour.de/#kids` |
| Code-Prüfung | Keine Rückmeldung während der Prüfung, kein Timeout | „Moment, Tübi prüft den Code …“, 15-s-Timeout, tolerante Eingabe |
| Selfie ohne Kamera-Zugriff | Absturz in manchen Browsern, leeres Foto vor Kamerastart | Freundlicher Hinweis, kein leeres Foto |
| Fußzeile | „Eine Tour von TraceTour Tübingen“ | „Eine Tour von TraceTour“ (Marke ist nicht auf Tübingen beschränkt) |

### Offline-Modus (sw.js)

- **iPhone-Audio offline:** Audio-Player fragen Dateien stückweise an. Der alte Service Worker antwortete mit der ganzen Datei; Safari spielt das aus dem Cache oft nicht ab. Jetzt kommt die korrekte Teil-Antwort (206). Im Chrome-Test spielt Audio offline; auf einem echten iPhone konnte ich nicht testen.
- **Updates löschen keine Downloads mehr:** Vorher wurde bei jeder neuen Version der ganze Cache gelöscht, auch die 50 MB Audio mitten in der Tour. Jetzt getrennte Caches; vorhandene Downloads werden beim Update übernommen.
- **Funkloch:** Seiten warten höchstens 4 Sekunden aufs Netz, dann kommt die gespeicherte Version. Gibt es keine, erscheint eine freundliche Offline-Seite statt eines Browserfehlers.

### Tempo, Barrierefreiheit, SEO

- **Ladegröße:** Startseite 2,2 MB → 745 KB, App-Start 1,4 MB → 577 KB. Größter Brocken war die Icon-Schrift mit 1,1 MB für 40 Icons; jetzt 14 KB. Fotos neu komprimiert (5,9 → 3,4 MB, kein sichtbarer Unterschied), dabei GPS-Metadaten aus dem Hero-Foto entfernt.
- **Cache-Buster:** CSS/JS-Links tragen `?v=20261026`, damit GitHub Pages und der Service Worker keine alten Dateien ausliefern.
- **Barrierefreiheit (WCAG AA):** axe-core meldet 0 Verstöße auf allen Seiten und App-Screens (vorher u. a. zu blasse Grautöne, Icon-Namen wie „location_on“ wurden vorgelesen, Knöpfe ohne Beschriftung, Audio nicht per Tastatur bedienbar). Weiße Schrift auf dem Marken-Orange hatte nur 3,2:1 Kontrast; Buttons nutzen jetzt #cf4a18 (4,5:1). #f3632d bleibt Akzentfarbe.
- **SEO:** Neuer Titel/Description, Strukturdaten als „TouristTrip“ mit Preisen (vorher ein ungültiger Typ), FAQ-Strukturdaten werden automatisch aus dem sichtbaren Text erzeugt, Sitemap-Datum aktualisiert.

### Rechtstexte

- **Datenschutz Ziffer 10 war falsch:** Dort stand, beim Einlösen werde „ausschließlich der Code“ übertragen. Tatsächlich gehen Code, Tour und eine zufällige Geräte-ID an den Worker, gespeichert werden Geräte-IDs und erste Aktivierung. Jetzt korrekt, mit Rechtsgrundlage.
- **Datenschutz ergänzt:** vollständige Liste der lokal gespeicherten Daten (§ 25 TDDDG), Leaflet nicht mehr bei unpkg, Rechtsgrundlage für OpenStreetMap, mögliche Übermittlung an Stripe, Inc. (USA), neuer Abschnitt „Kontakt per E-Mail“.
- **AGB:** Zahlungsarten ohne feste Klarna-Zusage („werden im Bezahlvorgang angezeigt“), Stand aktualisiert.

**So habe ich getestet:** Headless-Chrome (Playwright) mit Handy-Größe: beide Touren komplett durchgespielt (Krimi auf Deutsch und Englisch bis zur Urkunde), Offline-Download → Neuladen ohne Netz → Audio abspielen, GPS verweigert, Login-Randfälle, axe-core auf allen Seiten, Screenshots mobil und Desktop. Nicht getestet: echtes iPhone/Safari, echter Kauf mit Stripe (noch keine Links), der Worker selbst (aus der Testumgebung nicht erreichbar).

---

## 2. Bewusst nicht geändert

| Was | Warum |
|---|---|
| Alle gesprochenen Texte (Stations-Texte in app.html/kinder.html, generate_audio*.py, MP3s) | Hängen an fertigen Audios. Vorschläge stehen in Abschnitt 4. |
| Geprüfte Fakten (9 Glocken, phrygische Tonleiter, Weinfass laut Guinness …) | Vorgabe. Zweifel stehen in Abschnitt 4. |
| Kauf- und Code-Logik (Worker `/validate`, Tour-Bindung, Geräte-Limit, 48-h-Fenster, Danke-Seite) | Kein klarer Fehler gefunden. Nur die Eingabe im Browser ist toleranter (Leerzeichen, Bindestriche); geprüft wird weiter ausschließlich im Worker. |
| Testcodes `TUEBINGEN2025`, `TUEBINGEN2026`, `PRIVAT` | Werden womöglich gerade von Testern genutzt. Entscheidung unten. |
| Mailtext im Checkout-Worker | Gehört zum Kaufablauf und wird separat deployt. Textvorschlag unten. |
| `noindex` auf allen Seiten | Bewusst gesetzt („Seite im Aufbau“). Entscheidung unten. |
| KI-Proxy (worker.js) | Kein Fehler im engeren Sinn, aber ein Kostenrisiko. Entscheidung unten. |
| Impressum-Adresse | Vorgabe: Sonnenhalde 72, 72829 Engstingen bleibt. |
| Flyer (flyer.html) | Druckvorlage mit eigener Gestaltung; Kontraste dort sind ein Druck-, kein Bildschirmthema. |
| Debug-Panel, Tester-Begrüßung | Nur über Testcodes erreichbar; hängt an der Testcode-Entscheidung. |
| Neue Dienste, Tracker, CDNs | Keine hinzugefügt. Im Gegenteil: unpkg fällt weg. |

---

## 3. Offene Entscheidungen für dich (je mit Empfehlung)

**Vor dem Verkaufsstart (wichtig):**
1. **Widerrufsbutton** (§ 356a BGB, seit 19.06.2026 Pflicht für online geschlossene Verträge): Fehlt er, verlängert sich die Widerrufsfrist auf 12 Monate und 14 Tage. → *Empfehlung: Seite „Vertrag widerrufen“ mit Formular (nur Name, Bestellung/Code, E-Mail) und Knopf „Widerruf bestätigen“ plus automatische Eingangsbestätigung per Mail über den Checkout-Worker bauen. Kann ich in einer Folgerunde umsetzen.*
2. **Widerrufsbelehrung und AGB** auf den Stand vom 19.06.2026 bringen: Die Quellen widersprechen sich, ob das amtliche Muster nur ergänzt wurde oder entfallen ist. → *Empfehlung: Rechtstexte von einem Rechtstext-Dienst (z. B. IT-Recht Kanzlei, Händlerbund) erzeugen lassen, nicht selbst formulieren.*
3. **Zustimmung zum Erlöschen des Widerrufsrechts:** Laut AGB passiert sie mit dem Akzeptieren der AGB. Sie muss aber ausdrücklich erklärt und danach per Mail bestätigt werden (§ 356 Abs. 5, § 312f Abs. 3 BGB). → *Empfehlung: eigene Pflicht-Checkbox im Stripe-Checkout und diesen Satz in die Code-Mail:* „Du hast beim Kauf ausdrücklich zugestimmt, dass wir sofort mit der Bereitstellung beginnen, und bestätigt, dass dein Widerrufsrecht damit erlischt. Unsere AGB: tracetour.de/agb.html“
4. **Testcodes im öffentlichen Quelltext:** Jeder kann `TUEBINGEN2026` nachlesen und gratis spielen; `PRIVAT` schaltet den Debug-Modus frei. → *Empfehlung: vor Verkaufsstart entfernen und Testern normale Codes über den Worker geben.*
5. **Gerätelimit vs. Preis pro Person:** Jeder Code läuft auf bis zu 4 Handys. Drei Freunde kaufen also ein Solo-Ticket für 9,99 € statt drei Team-Tickets für 23,97 €. → *Empfehlung: Limit pro Produkt im Worker (Solo 1, Familie 1 wie auf der Preiskarte, Team 4, Klasse 8) oder ehrlich „pro Handy“ bepreisen.*
6. **Schulklasse (30 Personen) mit 4 Geräten:** → *Empfehlung: Klassen-Code mit höherem Limit; im Text „ein Handy pro Gruppe“ nennen.*
7. **Team-Ticket bei Stripe:** → *Empfehlung: Payment Link mit einstellbarer Menge (min. 3, max. 7).*
8. **Stripe-Links eintragen:** in `CHECKOUT_LINKS` (index.html, oben im Script). → *Empfehlung: erst nach Punkt 1–4.*
9. **`noindex` entfernen:** → *Empfehlung: zum Verkaufsstart auf Startseite und Rechtstexten entfernen; app.html, kinder.html, danke.html behalten `noindex`.*

**Sicherheit und Betrieb:**
10. **ElevenLabs-Keys rotieren** (laut CLAUDE.md noch offen, waren öffentlich): → *Empfehlung: sofort.*
11. **KI-Proxy ist offen:** Jede fremde Website kann über `tracetour-ai…workers.dev` mit eigenem Systemprompt Claude auf deine Kosten nutzen (Limit nur 30/h pro IP und Worker-Instanz). → *Empfehlung: Prompt im Worker bauen, nur Stationsnummer und Frage annehmen, Herkunft auf tracetour.de begrenzen.*
12. **Löschkonzept im Worker:** Codes, E-Mails und Geräte-IDs werden nie gelöscht. → *Empfehlung: z. B. 13 Monate nach Kauf E-Mail und Geräte-IDs entfernen (steuerlich nötige Daten liegen ohnehin bei Stripe).*
13. **Trace/Anthropic in der Datenschutzerklärung:** Rechtsgrundlage für die Übermittlung in die USA fehlt. → *Empfehlung: mit Anthropics Datenverarbeitungsbedingungen ergänzen; ich weiß nicht sicher, ob Anthropic unter dem Data Privacy Framework zertifiziert ist.*
14. **Trace-Begleiter erreichbar?** Aus meiner Testumgebung war der KI-Worker nicht erreichbar, daher ungeprüft. → *Empfehlung: einmal live fragen; ohne Worker antwortet Trace nur mit festen Tipps, die Preisliste verspricht aber „KI-Assistent“.*

**Produkt:**
15. **Echten App-Screenshot zeigen:** `images/app-screenshot.png` liegt ungenutzt im Repo (1 MB). → *Empfehlung: verkleinert im Abschnitt „So funktioniert's“ zeigen; ein echter Screen überzeugt mehr als jede Beschreibung.*
16. **Kundenstimmen:** Es gibt keine. → *Empfehlung: nach den ersten Testern 2–3 echte Zitate (mit Erlaubnis) auf die Startseite.*
17. **„Bildungsplanbezug“ bei Schulklassen:** Behauptung ohne Beleg. → *Empfehlung: konkret machen (Fach/Klassenstufe) oder streichen.*
18. **12-Monate-Einlösefrist** wird vom Worker nicht geprüft (Codes gelten unbegrenzt). → *Empfehlung: so lassen; kulanter als versprochen ist kein Problem.*
19. **Kindertour auf Englisch:** → *Empfehlung: später; ist jetzt überall ehrlich als „nur Deutsch“ gekennzeichnet.*
20. **Kartenkacheln offline:** Werden nicht vorgeladen (Nutzungsregeln von OpenStreetMap). → *Empfehlung: so lassen; FAQ sagt das jetzt offen.*

---

## 4. Vorschläge für gesprochene Texte (nicht umgesetzt)

**Mögliche Faktenfehler (bitte prüfen):**
- **Kindertour, Station 7 „Nonnenhaus“** (kinder.html und generate_audio_kinder.py): „Das Nonnenhaus wurde 1488 gebaut – als Kolumbus Amerika entdeckte!“ Kolumbus kam 1492 an. Vorschlag: „Das Nonnenhaus wurde 1488 gebaut – vier Jahre bevor Kolumbus nach Amerika segelte!“
- **Kindertour, Station 2 „Schloss“:** „das zweitgrößte Weinfass der Welt – 84.000 Liter“. Der Krimi sagt „ältestes erhaltenes Riesenweinfass der Welt“ (Guinness 2019) und „rund 85.000 Liter“, die Infotafel vor Ort laut CLAUDE.md 84.000. Vorschlag für beide Touren einheitlich: „das älteste Riesenweinfass der Welt – 84.000 Liter“ (336 Badewannen passt zu 84.000).
- **Kindertour, Station 3 „Stiftskirche“:** „Die Kirche ist über 600 Jahre alt.“ Laut Infotafel ab 1470 erbaut, also gut 550 Jahre. Vorschlag: „über 550 Jahre alt“ (falls ein Vorgängerbau gemeint ist, so sagen).
- **Kindertour, Frage Station 4** (nur Bildschirmtext): „der 500 Jahre alte Brunnen 1961 abgerissen“. Bei Baujahr 1523 war er 1961 rund 440 Jahre alt. Vorschlag: „der über 400 Jahre alte Brunnen“.
- **Froschkönig (beide Touren):** „gestohlen … zum Glück wurde er zurückgebracht“. CLAUDE.md nennt den Status vor Ort noch als offen. Vor dem Start einmal hingehen.

**Ausstehende Audios** (aus CLAUDE.md und CHANGELOG_AUDIO.md):
- Neu zu erzeugen nach Freigabe: anecdote_7 (DE+EN), bonus_13 (DE+EN), bonus_16 (DE+EN), thanks (EN fehlt ganz; die App blendet die Zeile aus).
- CHANGELOG_AUDIO.md listet 12 Einträge mit 🔄 (z. B. fact_0, fact_2, story_4). Bitte abgleichen, ob die schon erledigt sind; die Liste ist älter als das letzte Audio-Update.
- „Tübi flüstert“-Audios: Das Skript ist vorbereitet (`--whisper`), die Dateien fehlen noch. Würde die Kindertour spürbar lebendiger machen.
- **Wichtig nach dem Neu-Erzeugen:** In sw.js `MEDIA_CACHE` hochzählen (z. B. auf `tracetour-media-v2`), sonst hören Nutzer mit Offline-Download weiter die alte Fassung.

---

## 5. Gut zu wissen nach dem Merge

- Der neue Service Worker übernimmt beim ersten Besuch automatisch und behält vorhandene Offline-Downloads.
- Neues Icon nötig? `tools/subset_icons.py` ausführen (Anleitung im Skript), sonst erscheint statt des Icons sein Name als Text.
- CSS oder JS geändert? Das `?v=`-Datum in den HTML-Links und `ASSET_V` in sw.js anpassen.
- Diese Handgriffe stehen auch in CLAUDE.md.

**Quellen zum Widerrufsbutton:** [§ 356a BGB (dejure.org)](https://dejure.org/gesetze/BGB/356a.html), [IHK Karlsruhe: Widerrufsbutton wird verpflichtend](https://www.ihk.de/karlsruhe/fachthemen/recht/internetrecht/fallback1433495812828/widerrufsbutton-wird-verpflichtend-7020816), [Noerr: Umsetzungsgesetz veröffentlicht](https://www.noerr.com/de/insights/umsetzungsgesetz-zum-widerrufsbutton-veroeffentlicht), [IT-Recht Kanzlei: neue Rechtstexte erforderlich](https://www.it-recht-kanzlei.de/widerrufsbutton-neue-rechtstexte-erforderlich.html), [GK-law: Änderungen ab 19. Juni 2026](https://www.gk-law.de/news-service/reminder-widerrufsbelehrung-aenderungen-ab-19-juni-2026/), [widerrufsbelehrung.de: neue Musterbelehrung](https://www.widerrufsbelehrung.de/blog.php?last=off&blog=010.txt)
