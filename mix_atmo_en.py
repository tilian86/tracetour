#!/usr/bin/env python3
"""Mix ambient atmosphere under English TraceTour audio files (audio/en/)."""

from pydub import AudioSegment, utils
from pathlib import Path
import os

os.environ["PATH"] += os.pathsep + str(Path.home() / "bin")

AUDIO_DIR = Path(__file__).parent / "audio" / "en"
ATMO_DIR = Path("/Users/florian/Downloads/Atmo")

ATMO_VOLUME = {
    "stadt": -28,
    "stimmen": -30,
    "natur": -26,
    "vogel": -26,
    "nacht": -26,
}

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
    voice = AudioSegment.from_mp3(str(audio_path))
    atmo = AudioSegment.from_mp3(str(atmo_path))
    if len(atmo) < len(voice):
        atmo = atmo * ((len(voice) // len(atmo)) + 1)
    atmo = atmo[:len(voice)]
    atmo = (atmo + volume_db).fade_in(1000).fade_out(2000)
    mixed = voice.overlay(atmo)
    mixed.export(str(audio_path), format="mp3", bitrate="128k")
    return len(voice) / 1000

def main():
    audio_types = ["story", "diary", "fact", "anecdote", "riddle"]
    done = 0
    for station_idx, (atmo_file, atmo_type) in STATION_ATMO.items():
        atmo_path = ATMO_DIR / atmo_file
        if not atmo_path.exists():
            print(f"  WARNUNG: Atmo nicht gefunden: {atmo_path}"); continue
        volume = ATMO_VOLUME[atmo_type]
        for atype in audio_types:
            if atype == "anecdote":
                audio_path = AUDIO_DIR / f"anecdote_{station_idx}.mp3"
            elif atype == "riddle":
                audio_path = AUDIO_DIR / f"riddle_{station_idx}.mp3"
            else:
                audio_path = AUDIO_DIR / f"{atype}_{station_idx}.mp3"
            if not audio_path.exists(): continue
            print(f"  [{station_idx}] {audio_path.name} + atmo ({volume}dB)...", end=" ", flush=True)
            try:
                dur = mix_file(audio_path, atmo_path, volume)
                print(f"OK ({dur:.0f}s)"); done += 1
            except Exception as e:
                print(f"FEHLER: {e}")
    print(f"\nFertig! {done} EN-Dateien mit Atmosphäre gemischt.")

if __name__ == "__main__":
    main()
