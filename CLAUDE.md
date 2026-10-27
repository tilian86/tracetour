# TraceTour — Projekt-Memory

## AKTUELLER STAND (27.10.2026, nachmittags) — zuerst lesen
**Zusammenarbeit (rechte Hand / linke Hand):** Es arbeiten zwei Claude-Sessions an TraceTour: eine Cloud-Session (kein Mac-Zugriff, keine Keys) und eine am Mac (ElevenLabs-Key in `.env`, wrangler-Login). Regeln, damit nichts Verbessertes verloren geht:
1. Vor jeder Arbeit `git fetch` und auf dem aktuellen Stand aufsetzen; nie alte Dateiversionen über neue kopieren.
2. Solange PR #1 offen ist, Inhalte (Texte, Audios, Bilder) gern auf `main`, Code-Umbauten auf dem PR-Branch. Wer den anderen Zweig einmergt, behält bei Konflikten **Inhalte aus main** und **Code aus dem Branch** – und prüft danach per Test.
3. Nach jeder Session diesen Abschnitt aktualisieren (was erledigt, was offen). Erst das ist „die Memory“ für alle Chats.
4. Geheimnisse (Testcodes, Keys) NIE in dieses Repo schreiben.

**Stand der Zweige:**
- `main` (live): enthält die Arbeit der Mac-Session vom 27.10.: Kindertour-Fakten korrigiert (ältestes Weinfass statt zweitgrößtes, Kirche über 500 Jahre, „noch bevor Kolumbus Amerika entdeckte“, Parkplätze ohne „drei“, Froschkönig nicht zurück/neuer bestellt, unbelegte Geheimgänge und „Neckar 1595 zugefroren“ ersetzt, Schlosstor-Quiz → Landsknechte statt Hirsch-Wappen), Kindertour-Audios Station 1–7 neu vertont, Krimi-Audios anecdote_7, bonus_13, bonus_16 (DE+EN) und thanks EN neu, neue Tübi-Bilder Station 0–7, Desktop-Fehler Kindertour behoben.
- PR #1 (Draft, Branch `claude/vigilant-sagan-jhhh1c`, https://github.com/tilian86/tracetour/pull/1): main ist dort **eingemergt** (Commit d4edb0e, Inhalte aus main übernommen). Zusätzlich: Kindertour-Bug (Station hing, wenn Hauptfrage vor Bonus-Aufgabe beantwortet) behoben, persönliche Begrüßung auch in der Kindertour (Flag `personal`), Krimi-App läuft ohne Leaflet weiter, neue Landingpage-Texte/FAQ (15 Fragen), Offline-Modus neu (sw.js), WCAG AA, Datenschutz korrigiert, Testcodes über Worker-Secret, Trace als „Digitaler Begleiter“ + KI-Hinweis im Chat (Pflicht Art. 50 KI-VO), Performance (Icon-Font 14 KB, Bilder komprimiert). Bericht: `BERICHT-CLOUD.md`.

**Einheitlicher Einstieg (neu, PR #1):** `code.html` (erreichbar als tracetour.de/code) ist DIE Seite zum Code-Einlösen. Alle „Code einlösen“-Links der Startseite zeigen dorthin. Der Code bestimmt die Tour: Worker prüft erst als Krimi-Code, bei `wrong_tour` als Kinder-Code, dann Weiterleitung nach app.html bzw. kinder.html (Code vorausgefüllt, Prüfergebnis im localStorage, keine zweite Prüfung). Gilt ein Code für beide Touren (`tours` in der Worker-Antwort), zeigt die Seite eine Auswahl. Gespeicherte Spielstände erscheinen dort als „Weiterspielen“. Den Namen gibt man weiterhin in der jeweiligen Tour ein. Danke-Seite und Code-Mail verlinken weiter direkt in die gekaufte Tour.

**Kindertour-Name:** ein Feld für Kind oder ganze Familie (Platzhalter „z. B. Mia oder Mia & Ben“, max. 30 Zeichen), steht auf der Urkunde. Familien tragen einfach alle Namen ein.

**Testcodes:** stehen NICHT mehr im Quelltext. `TUEBINGEN2025`, `TUEBINGEN2026`, `PRIVAT` gelten nur noch bis zum Merge von PR #1 (live auf main funktionieren sie noch). Neue Testcodes stehen im Worker-Secret `TESTER_CODES`, kommagetrennt, Format `TT-XXXX-XXXX` (nur A–Z und 2–9). Flags: `adult|kids|both` (Tour), `debug` (Debug-Leiste, nur für Florian), `personal` (persönliche Begrüßung mit Bitte um Feedback an florian@tracetour.de – in beiden Touren; in der Kindertour richtet sie sich an die ganze Familie, „Für die Großen: …“). Geplante Aufteilung (27.10.): 1 Code `both+debug` für Florian, 1 Code `adult+personal` (Freunde Krimi), 1 Code `kids+personal` (Freunde Kindertour), 1 Code `both+personal` (Freunde beide Touren); weitere Codes pro Gruppe, wenn einzeln sperrbar sein soll. Kein Geräte-Limit, kein 48-h-Fenster, sperren = Code aus dem Secret löschen. Die konkreten Codes stehen nur im Secret und im Chat, nicht hier.

### Nächste Schritte am Mac (Reihenfolge einhalten)
1. ElevenLabs-Key rotieren (alter war öffentlich), neuen Key in `.env` (nicht ins Repo).
2. `cd checkout-worker && npx wrangler secret put TESTER_CODES` (Wert: Codes mit Flags, siehe oben), dann `npx wrangler deploy`.
3. Mit einem neuen Testcode auf dem Branch-Stand testen (lokal `python3 -m http.server`), dann PR #1 als „Ready“ markieren und mergen. Danach Freunden die neuen Codes schicken.
4. Ab dem Merge: neu vertonte oder ersetzte Audios/Bilder in `MEDIA_REFRESH` (sw.js) eintragen und `CORE_CACHE` hochzählen – NICHT mehr `CACHE_NAME` (gibt es im neuen sw.js nicht mehr).
5. Vertonungs-Modell: alle Skripte nutzen `eleven_multilingual_v2`. Eleven v4 ist seit 28.09.2026 verfügbar; vor einem Wechsel eine Station mit v2 und v4 vergleichen (geklonte Stimmen können unter v4 anders klingen, Kosten prüfen). Noch nicht entschieden.

### Offen / widersprüchlich (Florian entscheidet)
- **Hirsch-Wappen:** April-Stadtgang notiert „Hirsch ist das größte Tier auf dem Wappen ✓“ (Krimi-Rätsel Station 0, Antwort „hirsch“). Die Mac-Session hat das Wappen am 27.10. für die Kindertour als „unbelegt“ ersetzt. Beides passt nicht zusammen → vor Ort klären, ggf. Krimi-Rätsel Station 0 anpassen (gesprochener Text + Audio riddle_0).
- Froschkönig: Krimi sagt „Sie bestellte sofort einen neuen. Schau mal, ob er schon wieder da ist!“ – passt zur Kindertour; Status vor Ort prüfen.

### Vor dem Verkaufsstart (offen)
- **Widerrufsrecht:** Florian will nach Code-Einlösung keinen Widerruf. Lösung: korrektes vorzeitiges Erlöschen bei digitalen Inhalten (§ 356 BGB): eigene Pflicht-Checkbox im Stripe-Checkout (ausdrückliche Zustimmung zum sofortigen Beginn + Kenntnis vom Verlust des Widerrufsrechts) UND Bestätigung dieser Zustimmung in der Code-Mail (§ 312f BGB). Ist das sauber umgesetzt, ist laut IT-Recht Kanzlei (16.06.2026) kein Widerrufsbutton (§ 356a BGB) nötig. Fehlt einer der Bausteine: Widerruf bis 12 Monate + 14 Tage möglich. Mail-Satz-Vorschlag steht in BERICHT-CLOUD.md.
- **Widerrufsbelehrung/AGB:** Amtliches Muster (Anlage 1 EGBGB) wurde zum 19.06.2026 ergänzt (BGBl. 2026 I Nr. 28), nicht abgeschafft (eine Kanzlei behauptete Letzteres – Einzelmeinung). Empfehlung: Belehrung + Muster-Widerrufsformular von Rechtstext-Dienst erzeugen lassen; Absatznummer des Erlöschens (§ 356 Abs. 5 oder 6) dabei prüfen.
- Stripe ist noch nicht eingerichtet. Stripe-Payment-Links in `CHECKOUT_LINKS` (index.html) eintragen; Team-Ticket mit einstellbarer Menge 3–7.
- **Entschieden 27.10.:** vorerst KEIN Kombiticket (Touren einzeln buchen) und KEINE Geschenkkarte – Käufer bekommen nur den Code per Mail und leiten ihn zum Verschenken weiter (so steht es auch in FAQ 12). Flyer (flyer.html): QR-Code führt auf https://tracetour.de (Startseite) – bleibt so, dort informiert man sich und kauft.
- `noindex` auf Startseite und Rechtstexten entfernen (app/kinder/danke behalten).
- **Gerätelimit:** gilt global (Worker-Variable `DEVICE_CAP`, Standard 4) – nicht in Stripe. Pro Produkt ginge über Stripe-Metadaten (`devices`) + kleine Worker-Änderung; noch nicht entschieden.
- KI-Proxy (`worker.js`) ist offen nutzbar (eigener Systemprompt möglich) → härten.
- **Native App:** Florian überlegt eine App. Empfehlung bisher: erst PWA („Zum Homescreen hinzufügen“, Manifest fehlt noch), weil App-Stores bei digitalen Inhalten 15–30 % nehmen und „ohne App“ ein Verkaufsargument ist.

## Stadtgang 2. April 2026 — Erkenntnisse vor Ort

### Station 0 — Schloss Hohentübingen
- **Fotos gemacht:** Schlosstor, Außenansicht, Infotafel Geschichte, DNS-Tafel (Miescher 1869), Wildpferd-Skulptur, Augustus-Kopf "Täuschend echt!", MUT-Öffnungszeiten
- **Cafe Musee: DAUERHAFT GESCHLOSSEN** — muss in App korrigiert werden falls erwähnt
- **Rätsel verifiziert:** Hirsch ist das größte Tier auf dem Wappen ✓ (⚠️ 27.10.: Mac-Session hält das Hirsch-Wappen für unbelegt – siehe „Offen / widersprüchlich“ oben)
- **MUT Museum:** Mi–So 10–17 Uhr, Do bis 19 Uhr, AlbCard-Partner
- **Schloss Öffnungszeiten:** täglich 7–20 Uhr
- **Schloss-Fakten von Infotafel:** 1078 erste Erwähnung "Castrum Twingia", 1477 Eberhard im Bart Uni-Gründer, Riesenfass 84.000 Liter (1549), 1816 Schloss an Uni übergeben
- **DNS-Tafel:** Friedrich Miescher entdeckte 1869 in der Schlossküche das Nuklein (DNS) — passt perfekt zur 1869-Story
- **Wildpferd:** Original aus Mammutelfenbein, ~40.000 Jahre alt, 4,82 cm, UNESCO-Weltkulturerbe, aus Vogelherd-Höhle im Lonetal
- **Schleichweg Schloss → Münzgasse:** Enge Gasse mit Steintreppen zwischen Häusern, kommt bei Hausnr. 3 auf der Münzgasse raus (bei Hotel am Schloss / Mauganeschtle). Toll für Kinder-Tour, NICHT kinderwagentauglich (Treppen!). Für beide Touren einbauen mit Variante: mit Kinderwagen (Hauptweg) / ohne (Schleichweg)
- GPS-Koordinaten aus Foto-EXIF nutzen für exakte Navigation in beiden Touren

### Station 1 — Studentenkarzer (Münzgasse 20)
- **Nicht zugänglich** von außen, nur Eingangstür sichtbar
- Foto der Eingangstür gemacht (viel Graffiti)

### Station 2 — Alte Aula (Münzgasse 30)
- **Fotos gemacht:** Fassade quer, Infotafel
- **Rätsel verifiziert:** Infotafel bestätigt "1547 erbaut" und "1777 zum 300-jährigen Jubiläum umgebaut" ✓
- Rätsel 1777 − 300 = 1477 funktioniert perfekt

### Station 3 — Martinianum (Münzgasse 13)
- **Fotos gemacht:** "Hier kotzte Goethe"-Schild, Cottahaus-Tafel, Banner, Fassade
- **Cottahaus-Tafel:** "Hier wohnte Goethe, 7.–16. September 1797"
- **Banner:** "Damit auch künftige Goethes hier kotzen können! www.muezgasse13.de"
- **Rätsel-/Story-Idee:** Kontrast zwischen elegantem Goethe-Aufenthalt im Cottahaus (schöner Blick ins Neckartal) und dem deftigen "Hier kotzte Goethe"-Schild nebenan

### Station 4 — Stiftskirche
- **Fotos gemacht:** Infotafel, Turm+Uhr, Hauptportal (Holzmarkt-Seite), Evangelistensymbole, Georgs-Relief, Kirchenwand-Details
- **Infotafel:** "Ab 1470 in spätgotischem Stil errichtet, seit 1534 evangelisch. Chor zunächst auch Festsaal der Universität, seit 1537 Grablege der württembergischen Herzöge."
- **Turmhöhe 56m:** Bestätigt (anderweitig recherchiert), steht NICHT auf der Infotafel vor Ort
- **Evangelistensymbole Turmecken:** Muschelkalk, 1932/33, Fritz von Graevenitz (1892–1959). Kunstpfad Tübingen Station 9. "Hervorstehende Tierplastiken auf halber Höhe des Turms"
- **Zwei Fabelwesen am Hauptportal:** Links und rechts über dem Spitzbogen (spätgotisch, älter als Graevenitz-Symbole)
- **Georgs-Relief über Fenster:** Ritter auf Pferd tötet Drachen, Prinzessin dabei, Wappen oben rechts — an der Kirchenwand Richtung Holzmarkt
- **Goldener Wetterhahn** auf der Turmspitze — mögliches Rätsel-Element
- **Rätsel-Idee Kinder-Tour:** "Stell dich vor den Georgsbrunnen. Schau den Drachentöter an. Jetzt dreh dich um — wo versteckt sich noch ein Drachentöter an der Kirchenwand?"
- **Rätsel-Idee Erwachsene:** "Vom Brunnen siehst du den Drachentöter zweimal. Welche Person ist im Steinrelief dabei, die auf dem Brunnen fehlt?" → Antwort: Prinzessin
- **Noch offen:** Glocken dorische Tonleiter? Turmneigung 1962-64? Turmbesteigung möglich + Preis? → zu Hause recherchieren

### Station 5 — Holzmarkt & Georgsbrunnen
- **Fotos gemacht:** Georg + Drache close-up, mit Turm im Hintergrund
- **Brunnen hat 4 Rohre** — Rätsel "wie viele Rohre" nicht gut genug, stattdessen Drachentöter-Rätsel (siehe Station 4)

### Station 6 — Rathaus & Marktplatz
- **Fotos gemacht:** Rathaus-Fassade quer, astronomische Uhr close-up (Drachenzeiger sichtbar!), Uhren-Gesamtansicht, Neptunbrunnen (mehrere Perspektiven), Marktplatz-Panorama
- **Rätsel Drachenzeiger verifiziert** ✓ — goldener verzierter Zeiger auf astronomischer Uhr, Sonne links, Mond rechts, Tierkreiszeichen
- **Infotafel "Zerstörung der kommunalen Demokratie":** 31.3.1933 Gemeinderat aufgelöst, Hugo Benzinger (KPD) ins KZ Heuberg, Simon Hayum (liberal, jüdisch) zum Rücktritt gezwungen. Mai 1933: erstes Freibadverbot für "Juden und Fremdrasse" im Deutschen Reich
- **Neptunbrunnen — noch offen:** Zigarren-Figuren der Handwerker sichtbar? WMF/Waffenstahl verifizieren? Zu Hause recherchieren
- **"Zur Krone"** — nicht explizit gecheckt, zu Hause recherchieren
- **Fassaden-Inschriften:** "Anno 1435", "Anno 1508" und weitere Jahreszahlen sichtbar

### Station 7 — Kornhaus/Stadtmuseum
- **Fotos gemacht:** Fachwerk-Fassade quer, Öffnungszeiten-Tür, Veranstaltungsaushang April 2026
- **Öffnungszeiten verifiziert:** Mi, Fr–So 11–17 Uhr, **Eintritt frei** ✓
- **Sonntagsführungen:** 5€, ermäßigt 3€ ✓
- **Offener Kunst Freitag:** 14:30–16:30 für Kinder, 3€ Kind / 7€ Erwachsene
- **Ausstellungen aktuell:** "My Generation – Jung sein in Tübingen" (bis 6.4.2026), "Über Städte und Dörfer" (Mahler, bis 31.5.2026), Lotte Reiniger Dauerausstellung, neue Ausstellung ab Feb 2027: "Der erste Trickfilm! 100 Jahre Abenteuer des Prinzen Achmed"
- **Room of Memories: EXISTIERT** ✓ — Dauerausstellung, Serious Game über NS in Tübingen. Dachboden-Raum mit sprechendem Spiegel, 2–4 Personen, ca. 50 Min, ab 14 Jahre. Kein Schild am Eingang, ist drinnen. Quelle: stadtmuseum-tuebingen.de
- **Adresse:** Kornhausstraße 10, 72070 Tübingen

### Noch ausstehende Stationen
- Station 8 — Ammerschlag: Foto, schiefes Fachwerk Ammergasse (Stadtfunken Geheimtipps-Karte)
- Station 9 — Haagtorplatz: Eisvogel-Streetart noch da?
- Station 10 — Froschkönig-Brunnen: Ist er wieder da nach Diebstahl?
- Station 11 — Affenfelsen: Radfahrerkönig noch da?
- Station 12 — Alter Bot. Garten: Hölderlin-Denkmal
- Station 13 — Neue Aula: Attempto-Giebel
- Station 14 — Nonnenhaus: "Sprachhaus" Rückseite sichtbar?
- Station 15 — Platanenallee/Neckarinsel
- Station 16 — Indianersteg

## Foto-Guidelines
- **App-Stationsfotos:** Querformat
- **Stadtfunken-Karten:** Querformat
- **Infotafeln:** Egal, Hauptsache lesbar
- GPS-EXIF-Daten aus Fotos für exakte Koordinaten in der App nutzen

## Code-Änderungen (2. April 2026 — Session)
- Sound-Fix: AudioContext resume() abwarten vor Oszillator-Scheduling, Gain erhöht
- Audio-Unlock: Listener bleibt aktiv bis Context running (nicht mehr {once:true})
- Karzer-Koordinaten korrigiert auf (48.5198596, 9.0549385)
- Scroll-to-top bei Stationswechsel (gamePanel.scrollTop = 0)
- Alte Aula Rätsel: Neues Mathe-Rätsel (1777 − 300 = 1477) statt Jahreszahl an Fassade
- Stiftskirche Rätsel: Multiple-Choice Turmhöhe (45m/56m/68m/74m) statt Jahrhundert-Frage
- Anecdote "Gesehen"-Button: Expliziter "Weiter"-Button statt auto-navigation
- Auto-Resume: Bei gespeichertem Spielstand direkt zur Tour-Auswahl statt Login
- Landing Page: Stats-Bar und Tour-Card Metadata auf CSS Grid umgestellt für Mobile

## Offene Aufgaben
- Evangelistensymbole + Wetterhahn als mögliche Rätsel-Elemente prüfen
- GPS-Koordinaten aus Foto-EXIF für alle Stationen aktualisieren (Station 3 bereits via OSM korrigiert)
- Froschkönig-Status vor Ort prüfen (Story sagt "schau ob er wieder da ist")
- Erledigt: Cafe Musee entfernt, Schleichweg eingebaut, Drachentöter-Rätsel eingebaut, Goethe-Story eingebaut, Glocken/Turmneigung recherchiert (9 Glocken, phrygisch, NS-Luftschutzkeller)

## Launch-Audit Mai 2026 (Commit 5de919e)
Kompletter Audit + Fixes: Bonusfragen 13/16, EN-Neptun-Sync, Quiz "Sieben Fragen", Station-3-GPS, XP-Guards, sw.js v2 (sprachbewusst, Leaflet-Cache), API-Keys aus Skripten entfernt (.env). Details in Auto-Memory project_tracetour.md.
NOCH OFFEN: ElevenLabs-Keys rotieren (waren public!). Erledigt 27.10.: die 7 Audios (anecdote_7, bonus_13, bonus_16 DE+EN, thanks EN) sind neu vertont.

## Audit Oktober 2026 (Branch claude/vigilant-sagan-jhhh1c, Bericht: BERICHT-CLOUD.md)
- **Icon-Schrift:** fonts/materialsymbols-subset.woff2 (nur genutzte Icons, 14 KB). Neues Icon in index.html/app.html → `tools/subset_icons.py` ausführen (Anleitung im Skript) und `?v=` in fonts/fonts.css hochzählen. Volle Schrift liegt in fonts/source/.
- **Leaflet** liegt lokal in vendor/leaflet/ (kein unpkg mehr).
- **Cache-Buster:** CSS/JS-Links tragen `?v=20261026`. Bei Änderungen an CSS/JS: Datum in allen HTML-Links UND `ASSET_V` in sw.js anpassen.
- **Service Worker:** `CORE_CACHE` hochzählen bei Code-Änderungen. Neu vertonte/ersetzte Audios oder Bilder in `MEDIA_REFRESH` eintragen (+ `CORE_CACHE` hochzählen) – sonst behalten Offline-Nutzer die alte Fassung. `MEDIA_CACHE` nur im Notfall hochzählen (löscht alle Downloads).
- **Verkaufsstart:** Stripe-Links in `CHECKOUT_LINKS` (index.html, oben im Script) eintragen → Buttons werden zu „Jetzt buchen“, Hinweis „Verkauf startet in Kürze“ verschwindet.
- **Button-Orange** für weiße Schrift: `bg-cta` (#cf4a18, WCAG AA). #f3632d bleibt Akzentfarbe.
- **Tailwind ohne node_modules im Repo:** Pakete in einen Temp-Ordner installieren und mit `NODE_PATH=<temp>/node_modules <temp>/node_modules/.bin/tailwindcss -c tailwind.config.js -i tailwind-input.css -o css/tailwind.css --minify` bauen.

## Tailwind-Build (seit 2026-07-16)
index.html nutzt STATISCHES css/tailwind.css (kein CDN mehr!). Nach Änderungen an Utility-Klassen in index.html neu bauen:
```bash
npm install -D tailwindcss@3 @tailwindcss/forms @tailwindcss/container-queries
npx tailwindcss -c tailwind.config.js -i tailwind-input.css -o css/tailwind.css --minify
```
Config: tailwind.config.js (Repo-Root), Input: tailwind-input.css. Node 22 in ~/.local/node.
