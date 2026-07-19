# Kapa — Wochenplaner nach Kapazität

Ein ruhiger Wochenplaner, der nach **Gewicht statt Uhrzeit** plant. Jede Aufgabe
bekommt einen Aufwand (S/M/L/XL), jeder Tag ein Maximum. Eine Kapazitätslinie
zeigt sofort, ob ein Tag noch realistisch ist — oder überläuft.

Konzeptioneller Nachbau der iOS-App *Weekline*, neu gedacht als installierbare
Web-App: plattformübergreifend, kostenlos, ohne Aufgaben-Limit.

## Was drin ist
- **Kapazitätsansicht** je Wochentag mit Über-Grenze-Visualisierung
- **✧ Glätten** — verteilt überladene Tage automatisch auf freie
- **✦ Import & Planen** — Aufgabenliste (z. B. aus Todoist) einfügen → Triage
  (Zitate/Merkzettel/PINs raus), Aufwand geschätzt, unter Tageskapazität verteilt
- **Übertrag** offener Aufgaben in die nächste Woche
- **Wiederkehrende** Aufgaben (jede Woche)
- **Drag & Drop** auf Touch *und* Maus, Antippen zum Bearbeiten
- **Export/Import** (JSON) — volle Datenhoheit
- **Hell/Dunkel** automatisch, **PWA**: installierbar & offline
- **Lokal**: alles in `localStorage`, kein Konto, kein Tracking, keine Server-Calls

## Aufbau
Eine einzige, selbstständige Datei plus PWA-Beiwerk:

```
weekplan/
├── index.html            ← die komplette App (HTML + CSS + JS inline)
├── manifest.webmanifest  ← PWA-Metadaten
├── sw.js                 ← Service Worker (Offline-Shell)
├── icon-192.png / icon-512.png / apple-touch-icon.png
└── README.md
```

Kein Build, kein npm, keine Abhängigkeiten. `index.html` läuft auch allein per
Doppelklick — für „installierbar & offline" müssen die Dateien nebeneinander am
selben Pfad ausgeliefert werden.

## Deployen (separat, ohne Build)

**Cloudflare Pages (Git-verbunden)**
1. Repo mit diesem Ordner-Inhalt anlegen
2. Cloudflare → *Workers & Pages* → *Create* → *Pages* → *Connect to Git*
3. Build-Command **leer**, Output-Verzeichnis **`/`** → *Deploy*
4. Custom Domain optional (z. B. `kapa.example.com`)

**Cloudflare Pages (Direct Upload)**
- *Create* → *Pages* → *Upload assets* → diesen Ordner reinziehen → *Deploy*

**GitHub Pages**
- Ordner-Inhalt ins Repo, *Settings → Pages → Deploy from branch* → Root wählen

## Der KI-Haken (Import & Planen)
Die Einordnung in `classify()` (in `index.html`) ist bewusst eine **transparente,
regelbasierte Demo**. Für echte Todoist-Anbindung wird genau diese Funktion durch
einen Claude-API-Aufruf ersetzt (über einen kleinen Cloudflare-Worker, der den
Todoist-Token und den API-Key hält) — das Modell liest jede Aufgabe im Kontext,
statt Muster zu matchen. Aufwandsschätzung, Deadline-Erkennung und die Verteilung
laufen dann serverseitig; UI und Kapazitätslogik bleiben unverändert.

## Datenschutz
Kein Backend, keine Analytics, keine externen Requests. Der Service Worker cached
nur Dateien der eigenen Herkunft. Daten bleiben im Browser des Geräts; Übertragung
zwischen Geräten nur bewusst per Export/Import.
