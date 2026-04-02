#!/usr/bin/env python3
"""
TraceTour Kids Audio Generator -- ElevenLabs TTS
Generiert alle Audio-Dateien fuer die Kindertour (kinder.html):
  - prolog.mp3       (Splash-Screen Story)
  - story_0..7.mp3   (Tuebi erzaehlt an jeder Station)

Verwendung:
  python3 generate_audio_kinder.py
  python3 generate_audio_kinder.py --station 0,1,2
  python3 generate_audio_kinder.py --list-voices
"""

import os
import sys
import time
from pathlib import Path

# ============================================================
# KONFIGURATION
# ============================================================

API_KEY = os.environ.get("ELEVENLABS_API_KEY", "sk_18df17d38593a50a53362f37c86f9527c02d4c21ec495fc7")

TUBI_VOICE = "gGrh7S39Hy7hjt4rtiDw"   # Tuebi der Drache

MODEL_ID = "eleven_multilingual_v2"
OUTPUT_DIR = Path(__file__).parent / "audio" / "kinder"

# Max Kreativitaet: stability niedrig, similarity hoch
VOICE_SETTINGS = {
    "stability": 0.25,
    "similarity_boost": 0.85,
    "style": 0.7,
    "use_speaker_boost": True,
}

# ============================================================
# ALLE TEXTE
# ============================================================

PROLOG = (
    "Hilfe!! Ich bin Tübi, ein kleiner Drache, und ich lebe seit fünfhundert Jahren "
    "hinter der großen Uhr am Tübinger Rathaus. Letzte Nacht ist etwas Schreckliches "
    "passiert: Ich habe so doll geniest, dass meine Drachenflamme aus dem Fenster "
    "geflogen ist!\n\n"
    "Sie ist in acht Funken zersprungen und quer durch die Stadt geflogen! "
    "Ohne meine Flamme kann ich nicht fliegen, kein Feuer spucken und nicht mal "
    "meinen Tee warm machen!\n\n"
    "Ich brauche ein mutiges Drachenkind, das mir hilft, alle acht Funken "
    "wiederzufinden. An jedem Ort wartet ein Geheimnis – und wenn du es löst, "
    "kommt ein Funke zurück! Hilfst du mir?"
)

STORIES = [
    # Station 0 - Rathaus/Marktplatz
    (
        "Hier wohne ich – direkt hinter der großen Uhr am Rathaus! "
        "Siehst du den Drachen auf dem Ziffernblatt? Das bin ich! "
        "Seit über fünfhundert Jahren drehe ich mich da oben und schnappe mir "
        "Sonne und Mond. Die Tübinger nennen mich den Drachenzeiger.\n\n"
        "Die Uhr ist eine astronomische Uhr – sie zeigt nicht nur die Zeit, "
        "sondern auch Sternzeichen und Mondphasen. Professor Stoeffler hat sie "
        "fünfzehnhundertelf gebaut – und sie läuft seit über fünfhundert Jahren "
        "ganz ohne Batterie!\n\n"
        "Letzte Nacht saß ich auf meinem Ziffernblatt, als mir eine Feder in die "
        "Nase kitzelte. Ich musste so doll niesen, dass meine Drachenflamme aus "
        "dem Fenster flog! Sie zerplatzte in acht Funken, die über die ganze Stadt "
        "flogen.\n\n"
        "Aber ein Funke ist hier geblieben – direkt am Rathaus!\n\n"
        "Wenn du ganz leise bist, siehst du, wie ich auf der Uhr die Sonne schnappe! "
        "Die Touristen denken, ich wäre nur aus Metall. Wenn die wüssten..."
    ),
    # Station 1 - Schloss Hohentübingen
    (
        "Willkommen in meinem Geheimversteck! Das Schloss ist mein Lieblings-Spielplatz!\n\n"
        "Im Keller steht das zweitgrößte Weinfass der Welt – vierundachtzigtausend Liter, "
        "ungefähr dreihundertsechsunddreißig Badewannen! Heute ist es leer, aber dafür "
        "wohnt darin mein bester Freund: Flatter die Fledermaus! "
        "Er hängt kopfüber drin und schläft den ganzen Tag.\n\n"
        "Das Schloss hat echte Geheimgänge! Zwei enge Tunnel führen vom Innenhof tief "
        "nach unten. Ich spiel dort Fangen mit den Fledermäusen!\n\n"
        "Im Museum liegt die älteste Kunst der Menschheit – eine Figur aus "
        "Mammut-Elfenbein, über fünfunddreißigtausend Jahre alt! Geschnitzt, als es noch "
        "echte Mammuts gab! Daneben: eine Flöte aus einem Vogelknochen – das älteste "
        "Musikinstrument!\n\n"
        "Flatter liebt es, mich im Geheimgang zu erschrecken! Einmal hat er Buh gerufen "
        "und ich hab vor Schreck einen Feuerstrahl an die Decke geschossen – da war "
        "meine Flamme noch heil..."
    ),
    # Station 2 - Stiftskirche / Münzgasse
    (
        "Als kleiner Drache bin ich nachts um die Stiftskirche geflogen – und BUMM! "
        "Gegen den Turm geknallt! Seitdem lehnt er sich acht Zentimeter zur Seite. "
        "Der Turm ist wirklich schief!\n\n"
        "Die Kirche ist über sechshundert Jahre alt. Im Turm hängt die Dominica – "
        "eine Glocke, die klingt, seit Kolumbus in die Schule ging. Mutige können "
        "hundertsiebzig Stufen hochklettern!\n\n"
        "Unter der Kirche liegt Graf Eberhard im Bart – der hieß wirklich so! "
        "Er gründete die Uni Tübingen.\n\n"
        "Und gleich nebenan in der Münzgasse hängt ein lustiges Schild: Dem Dichter "
        "Goethe wurde hier richtig übel! Zu viel Wein! Die Tübinger fanden das so "
        "lustig, dass sie ein Schild aufhängten.\n\n"
        "Die Münzgasse heißt übrigens so, weil hier früher echtes Geld geprägt wurde – "
        "der Tübinger Pfennig! Und es gab ein Studentengefängnis ohne Klo!\n\n"
        "Ob der Turm wegen mir schief ist? Vielleicht... Und der arme Goethe – "
        "hätte lieber meinen Drachenfeuer-Tee trinken sollen statt Wein!"
    ),
    # Station 3 - Georgsbrunnen / Holzmarkt
    (
        "Jetzt lernst du meinen Cousin kennen! Der Drache am Brunnen ist Georg-Drache. "
        "Der arme Kerl spielt seit fünfhundert Jahren den Toten, weil ein Ritter auf "
        "ihm steht!\n\n"
        "Den Georgsbrunnen gibt es seit fünfzehnhundertdreiundzwanzig! "
        "Neunzehnhundertelf hat jemand die Figur im Neckar gefunden – im Fluss! "
        "Den Drachen fand man in einem Keller. Wie die dort landeten, weiß niemand!\n\n"
        "Neunzehnhunderteinundsechzig haben sie den Brunnen abgerissen. Wofür? "
        "Für DREI PARKPLÄTZE! Zum Glück wurde er neunzehnhundertsechsundsiebzig "
        "wieder aufgebaut.\n\n"
        "Ich besuche meinen Cousin jede Nacht. Er erzählt mir, welche Touristen die "
        "lustigsten Selfies machen.\n\n"
        "DREI PARKPLÄTZE! Ich bin IMMER NOCH sauer! Mein Cousin hat fünfzehn Jahre "
        "geschmollt. Jetzt steht er wieder da – ziemlich heldenhaft, oder?"
    ),
    # Station 4 - Hölderlinturm / Neckarfront
    (
        "Der gelbe Turm am Neckar ist der Hölderlinturm!\n\n"
        "Hier lebte der Dichter Friedrich Hölderlin – sechsunddreißig Jahre lang! "
        "Das ist wahrscheinlich länger als deine Eltern alt sind! "
        "Er war krank und wurde von der Familie Zimmer gepflegt. Er dichtete, spielte "
        "Klavier und schaute auf den Neckar.\n\n"
        "Der Turm war Teil der Stadtmauer. Achtzehnhundertfünfundsiebzig hat er gebrannt "
        "und wurde in seiner runden Form wieder aufgebaut – wie ein Phönix!\n\n"
        "Von hier siehst du die Neckarfront – die bunten Häuser, die sich im Wasser "
        "spiegeln. Einer der meistfotografierten Orte Tübingens!\n\n"
        "Ich komme abends hierher, setze mich auf die Mauer und schaue auf den Neckar. "
        "Manchmal reimt sich sogar was in meinem Drachenkopf!\n\n"
        "Sechsunddreißig Jahre in einem Zimmer! Ich wohne seit fünfhundert Jahren "
        "hinter einer Uhr, also verstehe ich das. Aber Hölderlin hatte wenigstens den "
        "Neckar-Blick! Das Museum ist sogar umsonst – wie cool ist das?"
    ),
    # Station 5 - Eberhardsbrücke / Neckar
    (
        "Von der Eberhardsbrücke siehst du den ganzen Neckar!\n\n"
        "Stocherkähne sind flache Holzboote – mit einer langen Stange über den "
        "Flussgrund geschoben. Kein Motor, keine Ruder!\n\n"
        "Jedes Jahr im Juni: das Stocherkahnrennen! Studenten fahren um die Wette – "
        "totales Chaos: Boote krachen, Leute fallen rein, verrückte Kostüme!\n\n"
        "Wer verliert: Lebertran! Öl aus Fischbäuchen – SO eklig! Und die Verlierer "
        "müssen das Rennen nächstes Jahr organisieren!\n\n"
        "Der Neckar war fünfzehnhundertfünfundneunzig so zugefroren, dass Pferdewagen "
        "drüber fuhren! Und Neckar bedeutet in einer uralten Sprache: Wildes Wasser!\n\n"
        "Beim Rennen sitze ich hier auf der Brücke! Einmal hat Lebertran fast MICH "
        "getroffen! Drachenfeuer und Fischöl – das hätte SO gestunken!"
    ),
    # Station 6 - Nonnenhaus
    (
        "Das Nonnenhaus wurde vierzehnhundertachtundachtzig gebaut – als Kolumbus "
        "Amerika entdeckte!\n\n"
        "Früher gab es einen Anbau direkt über dem Fluss. Darin war... das Klo! "
        "Alles fiel runter ins Wasser! Die Bewohner nannten es das Sprachhaus – "
        "aber es war eine Toilette!\n\n"
        "Hier wohnte Leonhart Fuchs – mit zehn Kindern! Er legte einen der ältesten "
        "botanischen Gärten Europas an. Die Blume Fuchsie? Nach IHM benannt!\n\n"
        "Wenn der Buchladen im Erdgeschoss auf hat: Durch ein Glasfenster im Boden "
        "siehst du den Boden von vierzehnhundertachtundachtzig!\n\n"
        "Zehn Kinder! Immer geschrien und gelacht! Leonhart hat mir eine Pflanze "
        "geschenkt – steht hinter der Uhr. Leider bin ich als Gärtner eine Katastrophe..."
    ),
    # Station 7 - Froschkönig-Brunnen (Finale)
    (
        "Die letzte Station – und sie hat eine verrückte Geschichte!\n\n"
        "Der Froschkönig-Brunnen am Ammerkanal zeigt einen Frosch mit Krone. "
        "Aber im Oktober zweitausendfünfundzwanzig wurde der Froschkönig gestohlen! "
        "Jemand hat ihn einfach mitgenommen! Die ganze Stadt suchte – zum Glück "
        "wurde er zurückgebracht.\n\n"
        "Der Brunnen erinnert ans Märchen vom Froschkönig. Manche sagen, der Frosch "
        "war ein verwunschener Drache...\n\n"
        "Hier ist es ruhig – perfekt zum Verschnaufen nach dem Abenteuer!\n\n"
        "Und jetzt... der letzte Funke ist ganz nah! Wenn du das Rätsel löst, "
        "bekomme ich meine Flamme zurück!\n\n"
        "Du hast mir durch die ganze Stadt geholfen, Drachenkind. Du bist ein "
        "echter Freund!\n\n"
        "Der Froschkönig wurde gestohlen! Hoffentlich klaut niemand MICH von der "
        "Rathausuhr! Aber weißt du was? Ich glaube, der Frosch war ein kleiner Drache. "
        "Wir können uns verwandeln – aber psssst!\n\n"
        "Nur noch dieses letzte Rätsel... dann kann ich wieder fliegen!"
    ),
]


# ============================================================
# AUDIO GENERIERUNG
# ============================================================

def generate_audio(text, voice_id, output_path):
    """Generiert eine MP3-Datei via ElevenLabs REST API."""
    import requests

    print(f"  Generiere: {output_path.name} ({len(text)} Zeichen)...", end=" ", flush=True)

    try:
        resp = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": API_KEY,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            json={
                "text": text,
                "model_id": MODEL_ID,
                "voice_settings": VOICE_SETTINGS,
            },
            stream=True,
        )
        if resp.status_code != 200:
            print(f"FEHLER: HTTP {resp.status_code} - {resp.text[:200]}")
            return False

        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=4096):
                f.write(chunk)

        size_kb = output_path.stat().st_size / 1024
        print(f"OK ({size_kb:.0f} KB)")
        return True

    except Exception as e:
        print(f"FEHLER: {e}")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="TraceTour Kids Audio Generator")
    parser.add_argument("--station", type=str, help="Nur bestimmte Stationen (z.B. 0,1,2)")
    parser.add_argument("--prolog-only", action="store_true", help="Nur Prolog generieren")
    parser.add_argument("--dry-run", action="store_true", help="Nur Texte anzeigen, nichts generieren")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Welche Stationen?
    if args.station:
        station_ids = [int(x.strip()) for x in args.station.split(",")]
    else:
        station_ids = list(range(len(STORIES)))

    # Aufgaben sammeln
    tasks = []

    if not args.station or args.prolog_only:
        tasks.append(("prolog.mp3", PROLOG))

    if not args.prolog_only:
        for i in station_ids:
            if i < 0 or i >= len(STORIES):
                print(f"  Station {i} existiert nicht (0-{len(STORIES)-1}), ueberspringe.")
                continue
            tasks.append((f"story_{i}.mp3", STORIES[i]))

    print(f"\n{'='*50}")
    print(f"TraceTour Kids Audio Generator")
    print(f"Voice: Tuebi ({TUBI_VOICE})")
    print(f"Kreativitaet: stability={VOICE_SETTINGS['stability']}, style={VOICE_SETTINGS['style']}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Dateien: {len(tasks)}")
    print(f"{'='*50}\n")

    if args.dry_run:
        for filename, text in tasks:
            print(f"\n--- {filename} ({len(text)} Zeichen) ---")
            print(text[:200] + "..." if len(text) > 200 else text)
        return

    success = 0
    for i, (filename, text) in enumerate(tasks):
        output_path = OUTPUT_DIR / filename
        if output_path.exists():
            print(f"  {filename} existiert bereits, ueberspringe. (Loeschen zum Neu-Generieren)")
            success += 1
            continue

        ok = generate_audio(text, TUBI_VOICE, output_path)
        if ok:
            success += 1

        # Rate-Limit: kurze Pause zwischen Requests
        if i < len(tasks) - 1:
            time.sleep(1.5)

    print(f"\n{'='*50}")
    print(f"Fertig: {success}/{len(tasks)} Dateien generiert")
    total_size = sum(f.stat().st_size for f in OUTPUT_DIR.glob("*.mp3")) / 1024
    print(f"Gesamtgroesse: {total_size:.0f} KB")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
