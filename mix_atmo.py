#!/usr/bin/env python3
"""
Mischt leise Hintergrund-Atmo unter die Sprachaufnahmen (Krimi DE + EN, Kindertour).

Wichtig – anders als die alte Fassung (bis 11/2026) wird NIE auf der fertigen Datei gearbeitet:
  audio_roh/<de|en|kinder>/<name>.mp3   sauberes Original (nur lokal, steht in .gitignore)
  audio/…/<name>.mp3                    Ergebnis mit Atmo (das wird ausgeliefert)
Dadurch kann man die Lautstärke jederzeit ändern und einfach neu mischen, ohne dass sich Atmo doppelt.

Ablauf nach einer Neuaufnahme (generate_audio*.py schreibt nach audio/):
  python3 mix_atmo.py            → erkennt die neue Datei am geänderten Inhalt, übernimmt sie als
                                   Original nach audio_roh/ und mischt die Atmo darunter.
Weitere Schalter:
  --nur de|en|kinder   nur ein Teil          --datei story_4   nur Dateien mit diesem Namen
  --lauter 3           Atmo 3 dB lauter (negativ = leiser), gilt für alles, was neu gemischt wird
  --alles              auch unveränderte Dateien neu mischen (nach Änderung der Lautstärke nötig)
  --trocken            nur anzeigen, nichts schreiben

Die Klangbetten liegen in atmo/ (11/2026 mit ElevenLabs „Sound Effects“ erzeugt, je 30 s, Schleife).
Aufnahmen, in die früher schon hörbar Atmo eingemischt wurde (Original verloren), bleiben unberührt.
"""
import argparse, hashlib, json, os, shutil, sys, zlib
from pathlib import Path

import numpy as np
from pydub import AudioSegment

ROOT = Path(__file__).parent
AUDIO = ROOT / "audio"
ROH = ROOT / "audio_roh"
BEDS = ROOT / "atmo"
STAND = ROH / "stand.json"
FFMPEG = Path.home() / "bin" / "ffmpeg"
if FFMPEG.exists():
    AudioSegment.converter = str(FFMPEG)
    os.environ["PATH"] = str(FFMPEG.parent) + os.pathsep + os.environ.get("PATH", "")

# Atmo-Pegel relativ zur Sprache (dB unter dem lauten Sprachpegel). Stimmen-artige Betten leiser.
REL = {"altstadt": -29, "schloss": -29, "markt": -31, "wirtshaus": -31, "park": -31, "fluss": -29, "nacht": -30}
MIN_DB, MAX_DB = -52.0, -44.0     # Grenzen für den Atmo-Pegel (dBFS)
SCHON_ATMO = -49.5                # Pausenpegel, ab dem eine Aufnahme als „hat schon Atmo“ gilt
FADE_IN, FADE_OUT, KREUZ = 1500, 2500, 800

KRIMI = {0: "schloss", 1: "altstadt", 2: "altstadt", 3: "altstadt", 4: "altstadt", 5: "markt", 6: "markt",
         7: "altstadt", 8: "wirtshaus", 9: "park", 10: "park", 11: "park", 12: "park", 13: "altstadt",
         14: "nacht", 15: "fluss", 16: "nacht"}
KRIMI_EXTRA = {"prologue": "altstadt", "guide": "altstadt", "formula": "nacht", "epilog": "nacht", "thanks": "nacht"}
KINDER = {"prolog": "markt", "story_0": "markt", "story_1": "schloss", "story_2": "altstadt", "story_3": "markt",
          "story_4": "fluss", "story_5": "fluss", "story_6": "park", "story_7": "park"}
TYPEN = ("story", "diary", "fact", "anecdote", "riddle", "bonus")


def bett_fuer(teil, name):
    if teil == "kinder":
        return KINDER.get(name)
    if name in KRIMI_EXTRA:
        return KRIMI_EXTRA[name]
    typ, _, nr = name.rpartition("_")
    if typ in TYPEN and nr.isdigit():
        return KRIMI.get(int(nr))
    return None


def pegel(seg):
    """(Pausenpegel, lauter Sprachpegel) in dBFS."""
    a = np.array(seg.set_channels(1).get_array_of_samples()).astype(np.float32) / (1 << (8 * seg.sample_width - 1))
    n = int(seg.frame_rate * 0.05)
    w = a[: len(a) // n * n].reshape(-1, n)
    r = 20 * np.log10(np.sqrt((w ** 2).mean(1)) + 1e-9)
    innen = r[30:-50] if len(r) > 160 else r
    return float(np.percentile(innen, 1)), float(np.percentile(r, 90))


def sha(p):
    return hashlib.sha1(p.read_bytes()).hexdigest()


_bett_cache = {}


def bett(name, laenge_ms, start_ms):
    if name not in _bett_cache:
        b = AudioSegment.from_mp3(str(BEDS / f"{name}.mp3")).set_frame_rate(44100).set_channels(2)
        _bett_cache[name] = b.apply_gain(-30.0 - b.dBFS)          # alle Betten auf gleichen Pegel
    b = _bett_cache[name]
    out = b[start_ms % len(b):]
    while len(out) < laenge_ms:
        out = out.append(b, crossfade=KREUZ)
    return out[:laenge_ms]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nur", choices=["de", "en", "kinder"])
    ap.add_argument("--datei")
    ap.add_argument("--lauter", type=float, default=0.0)
    ap.add_argument("--alles", action="store_true")
    ap.add_argument("--trocken", action="store_true")
    a = ap.parse_args()

    stand = json.loads(STAND.read_text()) if STAND.exists() else {}
    teile = {"de": AUDIO, "en": AUDIO / "en", "kinder": AUDIO / "kinder"}
    n_mix = n_alt = n_gleich = 0
    for teil, ordner in teile.items():
        if a.nur and a.nur != teil:
            continue
        for ziel in sorted(ordner.glob("*.mp3")):
            name = ziel.stem
            if a.datei and a.datei != name:
                continue
            b = bett_fuer(teil, name)
            if not b:
                continue
            key = f"{teil}/{name}"
            roh = ROH / teil / ziel.name
            # Neu aufgenommen (Inhalt weicht vom letzten Mischergebnis ab) oder noch nie gesichert → Original sichern
            neu = (not roh.exists()) or (key in stand and stand[key].get("fertig") != sha(ziel)) or (key not in stand)
            if neu and not (roh.exists() and key not in stand):
                if not a.trocken:
                    roh.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(ziel, roh)
            elif not a.alles:
                n_gleich += 1
                continue
            quelle = roh if roh.exists() else ziel
            stimme = AudioSegment.from_mp3(str(quelle))
            boden, laut = pegel(stimme)
            if boden >= SCHON_ATMO:
                n_alt += 1
                print(f"  {key:22s} hat schon Atmo (Pausen {boden:5.1f} dB) – bleibt")
                if not a.trocken:
                    stand[key] = {"fertig": sha(ziel), "bett": None}
                continue
            ziel_db = max(MIN_DB, min(MAX_DB, laut + REL[b])) + a.lauter
            print(f"  {key:22s} + {b:9s} {ziel_db:5.1f} dB (Sprache {laut:5.1f}, Pausen vorher {boden:5.1f})")
            n_mix += 1
            if a.trocken:
                continue
            stimme = stimme.set_frame_rate(44100).set_channels(2)
            start = zlib.crc32(key.encode()) % 20000
            atmo = bett(b, len(stimme), start).apply_gain(ziel_db + 30.0).fade_in(FADE_IN).fade_out(FADE_OUT)
            stimme.overlay(atmo).export(str(ziel), format="mp3", bitrate="128k")
            stand[key] = {"fertig": sha(ziel), "bett": b, "db": round(ziel_db, 1)}
    if not a.trocken:
        ROH.mkdir(exist_ok=True)
        STAND.write_text(json.dumps(stand, indent=1, sort_keys=True))
    print(f"\nGemischt: {n_mix} · schon mit Atmo: {n_alt} · unverändert übersprungen: {n_gleich}")


if __name__ == "__main__":
    main()
