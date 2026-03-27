# Audio-Änderungstracker

Dieses File trackt welche Audio-Dateien neu generiert werden müssen.
Status: ✅ = aktuell, 🔄 = Text geändert, muss neu generiert werden

## Station 0 - Schloss (Rätsel)
- story_0.mp3: ✅
- diary_0.mp3: ✅
- fact_0.mp3: 🔄 Neuer Fakten-Text (Miescher DNA, Vogelherd-Figuren, 84.000 Liter Weinfass) - muss neu generiert werden

## Station 1 - Karzer (Anekdote)
- anecdote_1.mp3: ✅

## Station 2 - Alte Aula (Rätsel)
- story_2.mp3: ✅
- diary_2.mp3: ✅
- fact_2.mp3: 🔄 Neuer Fakten-Text (fünftälteste Uni, 11 Professoren, Melanchthon 21J, Kepler) - muss neu generiert werden

## Station 3 - Martinianum (Anekdote)
- anecdote_3.mp3: ✅

## Station 4 - Stiftskirche (Rätsel)
- story_4.mp3: 🔄 "zwei ungleiche Türme" → "markanter Kirchturm" (korrigiert in Code, Audio noch nicht)
- diary_4.mp3: ✅
- fact_4.mp3: 🔄 Neuer Fakten-Text (15 Württemberger Fürstengruft, Attempto, Turmwächter Weihenmaier) - muss neu generiert werden

## Station 5 - Holzmarkt (Anekdote)
- anecdote_5.mp3: ✅

## Station 6 - Rathaus (Rätsel)
- story_6.mp3: ✅ (Story-Text unverändert, nur Rätsel geändert)
- diary_6.mp3: ✅ (Tagebuch unverändert)
- fact_6.mp3: 🔄 Neuer Fakten-Text (7 Namen, Graf Eberhard oben) - muss neu generiert werden

## Station 7 - Stadtmuseum (Anekdote)
- anecdote_7.mp3: 🔄 Lotte Reiniger Ausstellung entfernt - muss neu generiert werden

## Station 8 - Ammerschlag (Anekdote)
- anecdote_8.mp3: ✅

## Station 9 - Haagtorplatz (Rätsel)
- story_9.mp3: ✅
- diary_9.mp3: ✅
- fact_9.mp3: 🔄 Neuer Fakten-Text (5 Stadttore mit Namen, Torwächter 50 Gulden Abfindung) - muss neu generiert werden

## Station 10 - Affenfelsen (Rätsel)
- story_10.mp3: ✅
- diary_10.mp3: ✅
- fact_10.mp3: 🔄 Neuer Fakten-Text (Stadtmauer 13. Jh. 1,5km, Ammerkanal Mühlen, Recyclingsystem) - muss neu generiert werden

## Station 11 - Alter Bot. Garten (Anekdote)
- anecdote_11.mp3: ✅

## Station 12 - Neue Aula (Anekdote)
- anecdote_12.mp3: ✅

## Station 13 - Nonnenhaus (Rätsel)
- story_13.mp3: 🔄 Erker-Text umgeschrieben (ragt über Gasse hinweg) - muss neu generiert werden
- diary_13.mp3: ✅
- fact_13.mp3: 🔄 Neuer Fakten-Text (besterhaltener Abort Süddeutschland, Fuchs 400 Pflanzen, New Kreüterbuch 1543) - muss neu generiert werden

## Station 14 - Neckarinsel (Anekdote)
- anecdote_14.mp3: ✅

## Station 15 - Indianersteg (Rätsel)
- story_15.mp3: ✅ (Recherche bestätigt: 1869 waren Felder/Neckarauen auf der Südseite – Flucht-Szenario stimmt!)
- diary_15.mp3: ✅
- fact_15.mp3: 🔄 Neuer Fakten-Text (1869 Neckarauen, Südstadt ab 1880er, Bahnhof 1861, Karl-May-Spiele) - muss neu generiert werden

## Zusätzliche Audio-Dateien (NEU zu erstellen):
- intro.mp3: 🆕 Anleitungs-Audio (wie funktioniert die App, Spielmechanik erklären)
- prologue.mp3: 🆕 Einleitungs-Story vorlesen
- epilogue.mp3: 🆕 Abschluss-Story vorlesen (Urkunde, Farewell)

## Hintergrund-Atmosphäre in Audio-Dateien:
- TODO: Ambient-Sounds (Wind, Kirchenglocken, Wasser etc.) direkt in die MP3s mischen
- Benötigt: ffmpeg oder pydub zum Mixen
- Pro Station passende Atmosphäre aus AMBIENT_CONFIGS
