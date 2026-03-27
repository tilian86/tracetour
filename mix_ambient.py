#!/usr/bin/env python3
"""
TraceTour Ambient Mixer
Mischt Hintergrund-Atmosphäre unter die bestehenden TTS-MP3s.

Verwendung:
  python3 mix_ambient.py                  # Alle Dateien mixen
  python3 mix_ambient.py --station 0,4    # Nur bestimmte Stationen
  python3 mix_ambient.py --dry-run        # Nur zeigen, was gemacht wird
  python3 mix_ambient.py --volume 0.15    # Ambient-Lautstärke anpassen (Standard: 0.12)

Benötigt: pip3 install pydub && brew install ffmpeg
"""

import os
import sys
import struct
import random
import math
import wave
import tempfile
from pathlib import Path

try:
    from pydub import AudioSegment
    from pydub.generators import WhiteNoise
except ImportError:
    print("pydub nicht installiert! pip3 install pydub")
    sys.exit(1)

AUDIO_DIR = Path(__file__).parent / "audio"
BACKUP_DIR = Path(__file__).parent / "audio_backup"

# Ambient-Typ pro Station (aus AMBIENT_CONFIGS in index.html)
STATION_AMBIENT = {
    0:  'wind',      # Schloss - Wind auf dem Schlossberg
    1:  'cellar',    # Karzer - Kerkerstille
    2:  'cellar',    # Alte Aula - Gelehrten-Echo
    3:  'city',      # Martinianum - Muenzgassen-Stimmen
    4:  'church',    # Stiftskirche - Kirchenecho
    5:  'market',    # Holzmarkt - Marktgeraeusche
    6:  'market',    # Rathaus - Marktplatz-Leben
    7:  'city',      # Stadtmuseum - Stadtgeraeusche
    8:  'city',      # Ammerschlag - Kneipenatmosphaere
    9:  'wind',      # Haagtorplatz - Wind am Stadtrand
    10: 'water',     # Affenfelsen - Ammerkanal
    11: 'nature',    # Alter Bot. Garten - Voegel und Wind
    12: 'city',      # Neue Aula - Strassengeraeusche
    13: 'water',     # Nonnenhaus - Ammerkanal
    14: 'water',     # Neckarinsel - Neckarrauschen
    15: 'water',     # Indianersteg - Flussrauschen
}


def generate_noise(duration_ms, sample_rate=44100):
    """Generiert weisses Rauschen als Rohsamples."""
    num_samples = int(sample_rate * duration_ms / 1000)
    samples = bytes(
        struct.pack('<h', random.randint(-32768, 32767))
        for _ in range(num_samples)
    )
    return samples


def create_ambient_loop(ambient_type, duration_ms, sample_rate=44100):
    """Erzeugt einen synthetischen Ambient-Loop als AudioSegment."""

    # Basis: Weisses Rauschen, gefiltert je nach Typ
    noise = WhiteNoise().to_audio_segment(duration=duration_ms)

    if ambient_type == 'wind':
        # Tiefes Rauschen + langsames Pulsieren
        filtered = noise.low_pass_filter(400)
        filtered = filtered.low_pass_filter(250)
        # Langsames Fade-Pulsieren simulieren
        chunk_ms = 3000
        result = AudioSegment.silent(duration=0)
        for i in range(0, duration_ms, chunk_ms):
            chunk = filtered[i:i+chunk_ms]
            # Sinusfoermige Lautstaerke-Modulation
            vol_mod = -3 + 3 * math.sin(2 * math.pi * i / 12000)
            chunk = chunk + vol_mod
            result += chunk
        return result[:duration_ms]

    elif ambient_type == 'water':
        # Fliessgeraeusch: tiefes + mittleres Rauschen
        low = noise.low_pass_filter(600)
        mid = noise.low_pass_filter(1200).high_pass_filter(200)
        combined = low.overlay(mid - 6)
        # Leichtes Pulsieren
        chunk_ms = 2000
        result = AudioSegment.silent(duration=0)
        for i in range(0, duration_ms, chunk_ms):
            chunk = combined[i:i+chunk_ms]
            vol_mod = -2 + 2 * math.sin(2 * math.pi * i / 8000)
            chunk = chunk + vol_mod
            result += chunk
        return result[:duration_ms]

    elif ambient_type == 'church':
        # Tiefer Hall + gelegentliches Glockenecho
        deep = noise.low_pass_filter(200)
        deep = deep - 4  # Leiser
        # Gelegentliche "Glocken" (Sinustoene)
        bells = AudioSegment.silent(duration=duration_ms)
        for t in range(0, duration_ms, 9000):
            bell_tone = AudioSegment.silent(duration=0)
            for freq in [220, 330, 440]:
                # Einfacher Sinuston
                samples = []
                bell_dur = 4000  # 4 Sekunden
                for s in range(int(sample_rate * bell_dur / 1000)):
                    val = int(2000 * math.sin(2 * math.pi * freq * s / sample_rate) *
                              math.exp(-s / (sample_rate * 1.5)))
                    samples.append(struct.pack('<h', max(-32768, min(32767, val))))
                tone = AudioSegment(
                    data=b''.join(samples),
                    sample_width=2, frame_rate=sample_rate, channels=1
                )
                if len(bell_tone) == 0:
                    bell_tone = tone
                else:
                    bell_tone = bell_tone.overlay(tone)
            bells = bells.overlay(bell_tone - 12, position=t)
        return deep.overlay(bells)[:duration_ms]

    elif ambient_type == 'cellar':
        # Sehr leises tiefes Rauschen + gelegentliche Tropfen
        deep = noise.low_pass_filter(150) - 6
        drips = AudioSegment.silent(duration=duration_ms)
        t = 0
        while t < duration_ms:
            # Tropfgeraeusch: kurzer hoher Sinuston
            drip_dur = 150
            samples = []
            freq = 400 + random.randint(0, 200)
            for s in range(int(sample_rate * drip_dur / 1000)):
                val = int(1500 * math.sin(2 * math.pi * freq * s / sample_rate) *
                          math.exp(-s / (sample_rate * 0.05)))
                samples.append(struct.pack('<h', max(-32768, min(32767, val))))
            drip = AudioSegment(
                data=b''.join(samples),
                sample_width=2, frame_rate=sample_rate, channels=1
            )
            drips = drips.overlay(drip - 8, position=t)
            t += random.randint(2000, 5000)
        return deep.overlay(drips)[:duration_ms]

    elif ambient_type in ('city', 'market'):
        # Staedtisches Grundrauschen
        base = noise.low_pass_filter(1000).high_pass_filter(100)
        mid = noise.low_pass_filter(2000).high_pass_filter(400) - 8
        combined = base.overlay(mid)
        # Gelegentliche "Stimmen" (moduliertes Rauschen)
        voices = AudioSegment.silent(duration=duration_ms)
        t = 0
        while t < duration_ms:
            voice_dur = random.randint(200, 600)
            voice = noise[t:t+voice_dur].low_pass_filter(800).high_pass_filter(200) - 4
            # Fade
            voice = voice.fade_in(50).fade_out(50)
            voices = voices.overlay(voice, position=t)
            t += random.randint(800, 3000)
        return combined.overlay(voices - 6)[:duration_ms]

    elif ambient_type == 'nature':
        # Wind + Vogelzwitschern
        wind = noise.low_pass_filter(350) - 2
        # Voegel: kurze hohe Toene
        birds = AudioSegment.silent(duration=duration_ms)
        t = 0
        while t < duration_ms:
            freq = random.randint(2000, 4500)
            chirp_dur = random.randint(80, 200)
            samples = []
            for s in range(int(sample_rate * chirp_dur / 1000)):
                # Frequenz-Sweep
                f = freq + 500 * math.sin(2 * math.pi * 8 * s / sample_rate)
                val = int(1200 * math.sin(2 * math.pi * f * s / sample_rate) *
                          math.exp(-s / (sample_rate * 0.08)))
                samples.append(struct.pack('<h', max(-32768, min(32767, val))))
            chirp = AudioSegment(
                data=b''.join(samples),
                sample_width=2, frame_rate=sample_rate, channels=1
            )
            birds = birds.overlay(chirp - 6, position=t)
            t += random.randint(1000, 4000)
        return wind.overlay(birds)[:duration_ms]

    else:
        # Fallback: leises Rauschen
        return noise.low_pass_filter(300)[:duration_ms]


def mix_ambient_into_file(audio_path, ambient_type, volume_db=-18):
    """Mischt Ambient-Sound unter eine bestehende MP3-Datei."""

    # Lade die Sprachdatei
    speech = AudioSegment.from_mp3(str(audio_path))
    duration = len(speech)

    # Erzeuge Ambient-Loop
    ambient = create_ambient_loop(ambient_type, duration + 2000)  # +2s fuer Fade

    # Ambient auf Zielvolumen bringen
    ambient = ambient + volume_db  # Relativ zur Normallautstaerke

    # Ambient trimmen und Fades
    ambient = ambient[:duration + 1000]
    ambient = ambient.fade_in(1500).fade_out(2000)

    # Sprache hat Vorrang - Ambient nur so lang wie Sprache + 1s Nachklang
    # Mix
    mixed = speech.overlay(ambient[:duration])

    # 1s leises Ambient-Nachklingen anhaengen
    if len(ambient) > duration:
        tail = ambient[duration:duration+1000].fade_out(1000)
        mixed = mixed + tail

    # Exportieren (ueberschreibt Original)
    mixed.export(str(audio_path), format='mp3', bitrate='128k')
    return len(mixed)


def main():
    dry_run = '--dry-run' in sys.argv
    volume = -18  # Standard: -18dB unter Normalvolumen (sehr dezent)

    if '--volume' in sys.argv:
        idx = sys.argv.index('--volume')
        volume = float(sys.argv[idx + 1])
        # Konvertiere 0-1 Bereich zu dB
        if volume > 0 and volume <= 1:
            volume = 20 * math.log10(volume)  # z.B. 0.12 -> -18.4 dB

    if '--station' in sys.argv:
        idx = sys.argv.index('--station')
        station_nums = [int(x) for x in sys.argv[idx + 1].split(',')]
    else:
        station_nums = list(range(16))

    # Backup erstellen
    if not dry_run:
        BACKUP_DIR.mkdir(exist_ok=True)
        print(f"Backup-Ordner: {BACKUP_DIR}")

    # Alle MP3s in audio/ sammeln
    audio_files = sorted(AUDIO_DIR.glob('*.mp3'))

    print("=" * 60)
    print("TraceTour Ambient Mixer")
    print("=" * 60)
    print(f"Volume:    {volume:.1f} dB")
    print(f"Stationen: {station_nums}")
    if dry_run:
        print("MODE:      DRY RUN (keine Dateien werden veraendert)")
    print("=" * 60)

    processed = 0
    errors = 0

    for f in audio_files:
        # Station-Nummer aus Dateinamen extrahieren
        name = f.stem  # z.B. "story_0", "anecdote_3"
        parts = name.split('_')
        if len(parts) < 2:
            continue
        try:
            station_num = int(parts[-1])
        except ValueError:
            continue

        if station_num not in station_nums:
            continue

        ambient_type = STATION_AMBIENT.get(station_num, 'city')

        print(f"\n  {f.name} <- {ambient_type}")

        if dry_run:
            processed += 1
            continue

        # Backup
        import shutil
        backup_path = BACKUP_DIR / f.name
        if not backup_path.exists():
            shutil.copy2(f, backup_path)
            print(f"    Backup: {backup_path.name}")

        try:
            duration = mix_ambient_into_file(f, ambient_type, volume)
            print(f"    OK ({duration/1000:.1f}s, {f.stat().st_size/1024:.0f} KB)")
            processed += 1
        except Exception as e:
            print(f"    FEHLER: {e}")
            errors += 1

    print("\n" + "=" * 60)
    print(f"Fertig! {processed} Dateien verarbeitet, {errors} Fehler.")
    if not dry_run:
        print(f"Backups in: {BACKUP_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
