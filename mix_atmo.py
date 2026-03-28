#!/usr/bin/env python3
"""
Mix ambient atmosphere under TraceTour audio files.
Keeps atmosphere very quiet so narration stays clear.
"""

from pydub import AudioSegment
from pathlib import Path
import sys

AUDIO_DIR = Path(__file__).parent / "audio"
ATMO_DIR = Path("/Users/florian/Downloads/Atmo")

# Atmosphere volume reduction (in dB) — very quiet background
ATMO_VOLUME = {
    "stadt": -28,       # Stadtgeräusche
    "stimmen": -30,     # Stimmengewirr — extra leise
    "natur": -26,       # Naturgeräusche
    "vogel": -26,       # Vogelgezwitscher
    "nacht": -26,       # Nachtgeräusche
}

# Map station index → atmo file + type
STATION_ATMO = {
    0:  ("stadtgeräusche 1.mp3", "stadt"),
    1:  ("stadtgeräusche 1.mp3", "stadt"),
    2:  ("Stadtgeräusche 2.mp3", "stadt"),
    3:  ("Stadtgeräusche 2.mp3", "stadt"),
    4:  ("stadtgeräusche 1.mp3", "stadt"),
    5:  ("Stimmengewirr Menschenmenge.mp3", "stimmen"),
    6:  ("Stimmengewirr Menschenmenge.mp3", "stimmen"),
    7:  ("stadtgeräusche 1.mp3", "stadt"),
    8:  ("Stimmengewirr Menschenmenge.mp3", "stimmen"),
    9:  ("Naturgeräusche.mp3", "natur"),
    10: ("Naturgeräusche 1.mp3", "natur"),
    11: ("Naturgeräusche.mp3", "natur"),
    12: ("Vogelgezwitscher.mp3", "vogel"),
    13: ("Stadtgeräusche 2.mp3", "stadt"),
    14: ("Nachtgeräusche Grillen usw.mp3", "nacht"),
    15: ("Vogelgezwitscher.mp3", "vogel"),
    16: ("Nachtgeräusche Grillen usw.mp3", "nacht"),
}

def mix_file(audio_path, atmo_path, volume_db):
    """Mix atmo under audio file, loop atmo if needed."""
    voice = AudioSegment.from_mp3(str(audio_path))
    atmo = AudioSegment.from_mp3(str(atmo_path))

    # Loop atmo to match voice length
    if len(atmo) < len(voice):
        repeats = (len(voice) // len(atmo)) + 1
        atmo = atmo * repeats
    atmo = atmo[:len(voice)]

    # Apply volume reduction and fade
    atmo = atmo + volume_db
    atmo = atmo.fade_in(1000).fade_out(2000)

    # Mix
    mixed = voice.overlay(atmo)
    mixed.export(str(audio_path), format="mp3", bitrate="128k")
    return len(voice) / 1000  # duration in seconds


def main():
    # Which audio types to mix atmo into
    audio_types = ["story", "diary", "fact", "anecdote"]

    total = 0
    done = 0

    for station_idx, (atmo_file, atmo_type) in STATION_ATMO.items():
        atmo_path = ATMO_DIR / atmo_file
        if not atmo_path.exists():
            print(f"  WARNUNG: Atmo nicht gefunden: {atmo_path}")
            continue

        for atype in audio_types:
            if atype == "anecdote":
                audio_path = AUDIO_DIR / f"anecdote_{station_idx}.mp3"
            elif atype == "story":
                audio_path = AUDIO_DIR / f"story_{station_idx}.mp3"
            elif atype == "diary":
                audio_path = AUDIO_DIR / f"diary_{station_idx}.mp3"
            elif atype == "fact":
                audio_path = AUDIO_DIR / f"fact_{station_idx}.mp3"

            if not audio_path.exists():
                continue

            total += 1
            volume = ATMO_VOLUME[atmo_type]
            print(f"  Station {station_idx}: {audio_path.name} + {atmo_file} ({volume}dB)...", end=" ", flush=True)
            try:
                dur = mix_file(audio_path, atmo_path, volume)
                print(f"OK ({dur:.0f}s)")
                done += 1
            except Exception as e:
                print(f"FEHLER: {e}")

    # Also mix riddle files with same atmo
    for station_idx, (atmo_file, atmo_type) in STATION_ATMO.items():
        riddle_path = AUDIO_DIR / f"riddle_{station_idx}.mp3"
        if not riddle_path.exists():
            continue
        atmo_path = ATMO_DIR / atmo_file
        if not atmo_path.exists():
            continue

        total += 1
        volume = ATMO_VOLUME[atmo_type]
        print(f"  Station {station_idx}: {riddle_path.name} + {atmo_file} ({volume}dB)...", end=" ", flush=True)
        try:
            dur = mix_file(riddle_path, atmo_path, volume)
            print(f"OK ({dur:.0f}s)")
            done += 1
        except Exception as e:
            print(f"FEHLER: {e}")

    print(f"\nFertig! {done}/{total} Dateien mit Atmosphäre gemischt.")


if __name__ == "__main__":
    main()
