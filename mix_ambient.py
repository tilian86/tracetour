#!/usr/bin/env python3
"""
TraceTour Ambient Mixer
Mischt Hintergrund-Atmosphaere unter die bestehenden TTS-MP3s.

Verwendung:
  python3 mix_ambient.py                  # Alle Dateien mixen
  python3 mix_ambient.py --station 0,4    # Nur bestimmte Stationen
  python3 mix_ambient.py --dry-run        # Nur zeigen, was gemacht wird

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
    from pydub.generators import WhiteNoise, Sine
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
    10: 'city',      # Froschkoenig-Brunnen - Altstadt bei Cafe Hirsch
    11: 'water',     # Affenfelsen - Ammerkanal
    12: 'nature',    # Alter Bot. Garten - Voegel und Wind
    13: 'city',      # Neue Aula - Strassengeraeusche
    14: 'water',     # Nonnenhaus - Ammerkanal
    15: 'water',     # Neckarinsel - Neckarrauschen
    16: 'water',     # Indianersteg - Flussrauschen
}

# Volume by track type (dB attenuation from ambient generator output)
TRACK_TYPE_VOLUME = {
    'story':    -26,   # Immersive narrative - full ambient
    'diary':    -26,   # Immersive narrative - full ambient
    'anecdote': -28,   # Atmospheric but less distracting
    'fact':     -32,   # Informational - ambient barely noticeable
}
DEFAULT_VOLUME = -28


def _make_tone(freq, duration_ms, amplitude=2000, decay_s=1.5, sample_rate=44100):
    """Helper: generate a sine tone with exponential decay."""
    samples = []
    n = int(sample_rate * duration_ms / 1000)
    for s in range(n):
        val = int(amplitude * math.sin(2 * math.pi * freq * s / sample_rate) *
                  math.exp(-s / (sample_rate * decay_s)))
        samples.append(struct.pack('<h', max(-32768, min(32767, val))))
    return AudioSegment(
        data=b''.join(samples),
        sample_width=2, frame_rate=sample_rate, channels=1
    )


def create_ambient_loop(ambient_type, duration_ms, sample_rate=44100):
    """Erzeugt einen synthetischen Ambient-Loop als AudioSegment."""

    noise = WhiteNoise().to_audio_segment(duration=duration_ms)

    if ambient_type == 'wind':
        # Deep filtered noise as base
        base = noise.low_pass_filter(300).low_pass_filter(200)
        # Build with slow pulsing + occasional gusts
        chunk_ms = 2000
        result = AudioSegment.silent(duration=0)
        for i in range(0, duration_ms, chunk_ms):
            chunk = base[i:i + chunk_ms]
            # Slow sine modulation for breathing effect
            phase = 2 * math.pi * i / 15000
            vol_mod = -4 + 3 * math.sin(phase) + 1.5 * math.sin(phase * 2.7)
            chunk = chunk + vol_mod
            result += chunk

        # Add occasional gusts (higher freq burst with fade)
        gusts = AudioSegment.silent(duration=duration_ms)
        t = random.randint(3000, 6000)
        while t < duration_ms - 4000:
            gust_dur = random.randint(2000, 4000)
            gust = noise[t:t + gust_dur].low_pass_filter(500).high_pass_filter(80)
            gust = gust - 4
            gust = gust.fade_in(int(gust_dur * 0.4)).fade_out(int(gust_dur * 0.5))
            gusts = gusts.overlay(gust, position=t)
            t += random.randint(6000, 14000)

        return result.overlay(gusts - 3)[:duration_ms]

    elif ambient_type == 'water':
        # Layered water: deep flow + mid ripple + occasional rush
        low = noise.low_pass_filter(500).low_pass_filter(400)
        mid = noise.low_pass_filter(1500).high_pass_filter(200) - 6
        high_ripple = noise.low_pass_filter(3000).high_pass_filter(800) - 12

        combined = low.overlay(mid).overlay(high_ripple)

        # Gentle pulsing for flow feel
        chunk_ms = 1500
        result = AudioSegment.silent(duration=0)
        for i in range(0, duration_ms, chunk_ms):
            chunk = combined[i:i + chunk_ms]
            vol_mod = -2 + 1.5 * math.sin(2 * math.pi * i / 7000) + 0.8 * math.sin(2 * math.pi * i / 3500)
            chunk = chunk + vol_mod
            result += chunk

        # Occasional louder rushing sounds
        rushes = AudioSegment.silent(duration=duration_ms)
        t = random.randint(5000, 10000)
        while t < duration_ms - 5000:
            rush_dur = random.randint(3000, 5000)
            rush = noise[t:t + rush_dur].low_pass_filter(2000).high_pass_filter(100)
            rush = rush - 3
            rush = rush.fade_in(int(rush_dur * 0.3)).fade_out(int(rush_dur * 0.5))
            rushes = rushes.overlay(rush, position=t)
            t += random.randint(8000, 18000)

        return result.overlay(rushes - 4)[:duration_ms]

    elif ambient_type == 'church':
        # Deep reverberant base
        deep = noise.low_pass_filter(150).low_pass_filter(120) - 3

        # Realistic bell tones with harmonics and varied timing
        bells = AudioSegment.silent(duration=duration_ms)
        t = random.randint(2000, 5000)
        while t < duration_ms - 6000:
            # Each bell strike: fundamental + harmonics with different decay rates
            fundamental = random.choice([196, 220, 247, 262])  # G3, A3, B3, C4
            bell_dur = random.randint(5000, 7000)
            bell_tone = AudioSegment.silent(duration=0)

            # Harmonics: fundamental, 2x, 3x, 4.5x, 5.2x (bells have inharmonic partials)
            harmonic_ratios = [1.0, 2.0, 3.0, 4.5, 5.2, 6.3]
            harmonic_amps = [2500, 1800, 1200, 600, 400, 250]
            harmonic_decays = [2.5, 1.8, 1.2, 0.8, 0.6, 0.4]

            for ratio, amp, decay in zip(harmonic_ratios, harmonic_amps, harmonic_decays):
                freq = fundamental * ratio
                if freq > sample_rate / 2:
                    continue
                tone = _make_tone(freq, bell_dur, amplitude=amp, decay_s=decay, sample_rate=sample_rate)
                if len(bell_tone) == 0:
                    bell_tone = tone
                else:
                    bell_tone = bell_tone.overlay(tone)

            # Apply a slight attack to avoid click
            bell_tone = bell_tone.fade_in(15)
            bells = bells.overlay(bell_tone - 10, position=t)
            t += random.randint(7000, 15000)

        return deep.overlay(bells)[:duration_ms]

    elif ambient_type == 'cellar':
        # Very deep resonant base with echo effect
        deep = noise.low_pass_filter(120).low_pass_filter(100) - 4
        # Add a second layer slightly delayed for echo/resonance feel
        echo_layer = deep - 6
        resonant = deep.overlay(echo_layer[200:] + AudioSegment.silent(duration=200), position=0)

        # Water drips with more echo
        drips = AudioSegment.silent(duration=duration_ms)
        t = random.randint(1000, 3000)
        while t < duration_ms - 1000:
            drip_dur = random.randint(100, 200)
            freq = random.randint(500, 800)
            amp = random.randint(800, 1800)
            # Primary drip
            drip = _make_tone(freq, drip_dur, amplitude=amp, decay_s=0.04, sample_rate=sample_rate)
            # Echo of drip (quieter, slightly delayed)
            drip_echo = drip - 8
            drip_echo2 = drip - 14

            drips = drips.overlay(drip - 6, position=t)
            if t + 180 < duration_ms:
                drips = drips.overlay(drip_echo, position=t + 180)
            if t + 400 < duration_ms:
                drips = drips.overlay(drip_echo2, position=t + 400)

            t += random.randint(2500, 7000)

        # Occasional deep rumble
        rumbles = AudioSegment.silent(duration=duration_ms)
        rt = random.randint(8000, 15000)
        while rt < duration_ms - 3000:
            rumble_dur = random.randint(2000, 3000)
            rumble = noise[rt:rt + rumble_dur].low_pass_filter(80) - 4
            rumble = rumble.fade_in(int(rumble_dur * 0.4)).fade_out(int(rumble_dur * 0.5))
            rumbles = rumbles.overlay(rumble, position=rt)
            rt += random.randint(12000, 25000)

        return resonant.overlay(drips).overlay(rumbles - 3)[:duration_ms]

    elif ambient_type == 'city':
        # Constant low urban hum
        base_hum = noise.low_pass_filter(400).high_pass_filter(60) - 2
        # Mid-frequency steady layer
        mid_steady = noise.low_pass_filter(1200).high_pass_filter(200) - 8
        combined = base_hum.overlay(mid_steady)

        # Slow modulation for "traffic" feel
        chunk_ms = 3000
        result = AudioSegment.silent(duration=0)
        for i in range(0, duration_ms, chunk_ms):
            chunk = combined[i:i + chunk_ms]
            vol_mod = -1 + 1.0 * math.sin(2 * math.pi * i / 20000)
            chunk = chunk + vol_mod
            result += chunk

        # Sparse distant voice murmurs
        voices = AudioSegment.silent(duration=duration_ms)
        t = random.randint(3000, 6000)
        while t < duration_ms - 1000:
            voice_dur = random.randint(300, 800)
            voice = noise[t:t + voice_dur].low_pass_filter(700).high_pass_filter(180) - 6
            voice = voice.fade_in(80).fade_out(100)
            voices = voices.overlay(voice, position=t)
            t += random.randint(3000, 8000)  # Less frequent than market

        return result.overlay(voices - 4)[:duration_ms]

    elif ambient_type == 'market':
        # Busier, brighter base than city
        base = noise.low_pass_filter(1200).high_pass_filter(100)
        mid = noise.low_pass_filter(2500).high_pass_filter(300) - 6
        combined = base.overlay(mid)

        # More energetic modulation
        chunk_ms = 2000
        result = AudioSegment.silent(duration=0)
        for i in range(0, duration_ms, chunk_ms):
            chunk = combined[i:i + chunk_ms]
            vol_mod = -2 + 1.5 * math.sin(2 * math.pi * i / 6000) + 0.5 * math.sin(2 * math.pi * i / 2500)
            chunk = chunk + vol_mod
            result += chunk

        # Frequent voice-like bursts (more than city)
        voices = AudioSegment.silent(duration=duration_ms)
        t = random.randint(500, 1500)
        while t < duration_ms - 500:
            voice_dur = random.randint(150, 500)
            # Vary pitch range for different "speakers"
            low_cut = random.randint(150, 300)
            high_cut = random.randint(600, 1200)
            voice = noise[t:t + voice_dur].low_pass_filter(high_cut).high_pass_filter(low_cut) - 3
            voice = voice.fade_in(30).fade_out(50)
            voices = voices.overlay(voice, position=t)
            t += random.randint(400, 2000)  # Much more frequent than city

        return result.overlay(voices - 4)[:duration_ms]

    elif ambient_type == 'nature':
        # Richer wind base with rustling leaves
        wind_base = noise.low_pass_filter(300).low_pass_filter(250) - 2
        # Rustling leaves: higher freq filtered noise, pulsing
        leaves = AudioSegment.silent(duration=duration_ms)
        t = 0
        while t < duration_ms - 1000:
            rustle_dur = random.randint(500, 1500)
            rustle = noise[t:t + rustle_dur].low_pass_filter(4000).high_pass_filter(1500) - 10
            rustle = rustle.fade_in(int(rustle_dur * 0.3)).fade_out(int(rustle_dur * 0.4))
            leaves = leaves.overlay(rustle, position=t)
            t += random.randint(800, 3000)

        # Varied bird calls with different patterns
        birds = AudioSegment.silent(duration=duration_ms)
        t = random.randint(500, 2000)
        while t < duration_ms - 500:
            call_type = random.choice(['chirp', 'trill', 'tweet', 'warble'])

            if call_type == 'chirp':
                # Single short chirp
                freq = random.randint(2500, 5000)
                chirp = _make_tone(freq, random.randint(60, 150), amplitude=1000, decay_s=0.06, sample_rate=sample_rate)
                birds = birds.overlay(chirp - 4, position=t)

            elif call_type == 'trill':
                # Rapid repeated notes
                freq = random.randint(2000, 4000)
                pos = t
                for _ in range(random.randint(3, 7)):
                    note = _make_tone(freq + random.randint(-100, 100), 40, amplitude=800, decay_s=0.03, sample_rate=sample_rate)
                    if pos < duration_ms:
                        birds = birds.overlay(note - 5, position=pos)
                    pos += random.randint(50, 90)

            elif call_type == 'tweet':
                # Two-note call (high-low or low-high)
                f1 = random.randint(2500, 4500)
                f2 = f1 + random.choice([-400, -300, 300, 400, 500])
                t1 = _make_tone(f1, 120, amplitude=1100, decay_s=0.08, sample_rate=sample_rate)
                t2 = _make_tone(max(f2, 800), 120, amplitude=1100, decay_s=0.08, sample_rate=sample_rate)
                birds = birds.overlay(t1 - 4, position=t)
                if t + 180 < duration_ms:
                    birds = birds.overlay(t2 - 4, position=t + 180)

            elif call_type == 'warble':
                # Frequency sweep chirp
                warble_dur = random.randint(200, 400)
                freq_start = random.randint(2000, 3500)
                samples = []
                n = int(sample_rate * warble_dur / 1000)
                for s in range(n):
                    progress = s / n
                    freq = freq_start + 1500 * math.sin(2 * math.pi * 6 * progress)
                    val = int(900 * math.sin(2 * math.pi * freq * s / sample_rate) *
                              math.exp(-s / (sample_rate * 0.15)))
                    samples.append(struct.pack('<h', max(-32768, min(32767, val))))
                warble = AudioSegment(
                    data=b''.join(samples),
                    sample_width=2, frame_rate=sample_rate, channels=1
                )
                birds = birds.overlay(warble - 5, position=t)

            t += random.randint(1500, 5000)

        return wind_base.overlay(leaves - 2).overlay(birds)[:duration_ms]

    else:
        # Fallback: very quiet low noise
        return noise.low_pass_filter(300)[:duration_ms]


def get_volume_for_track(filename):
    """Determine ambient volume based on track type prefix."""
    stem = Path(filename).stem
    prefix = stem.split('_')[0]
    return TRACK_TYPE_VOLUME.get(prefix, DEFAULT_VOLUME)


def mix_ambient_into_file(audio_path, ambient_type, volume_db=-26):
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
        tail = ambient[duration:duration + 1000].fade_out(1000)
        mixed = mixed + tail

    # Exportieren (ueberschreibt Original)
    mixed.export(str(audio_path), format='mp3', bitrate='128k')
    return len(mixed)


def main():
    dry_run = '--dry-run' in sys.argv

    if '--station' in sys.argv:
        idx = sys.argv.index('--station')
        station_nums = [int(x) for x in sys.argv[idx + 1].split(',')]
    else:
        station_nums = list(range(17))

    # Backup erstellen
    if not dry_run:
        BACKUP_DIR.mkdir(exist_ok=True)
        print(f"Backup-Ordner: {BACKUP_DIR}")

    # Alle MP3s in audio/ sammeln
    audio_files = sorted(AUDIO_DIR.glob('*.mp3'))

    print("=" * 60)
    print("TraceTour Ambient Mixer v2")
    print("=" * 60)
    print(f"Volume:    Per-track-type (story/diary=-26dB, anecdote=-28dB, fact=-32dB)")
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
        volume = get_volume_for_track(f.name)

        print(f"\n  {f.name} <- {ambient_type} @ {volume}dB")

        if dry_run:
            processed += 1
            continue

        try:
            duration = mix_ambient_into_file(f, ambient_type, volume)
            print(f"    OK ({duration / 1000:.1f}s, {f.stat().st_size / 1024:.0f} KB)")
            processed += 1
        except Exception as e:
            print(f"    FEHLER: {e}")
            import traceback
            traceback.print_exc()
            errors += 1

    print("\n" + "=" * 60)
    print(f"Fertig! {processed} Dateien verarbeitet, {errors} Fehler.")
    print("=" * 60)


if __name__ == "__main__":
    main()
