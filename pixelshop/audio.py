"""Tiny NES-style chiptune synth: pulse/triangle/noise voices, songs, SFX, mixer.

Songs are public-domain compositions (Grieg, Joplin) in original chip arrangements.
"""
import re
import wave

import numpy as np

SR = 44100
NOTE_RE = re.compile(r"^([A-G])(#|b)?(-?\d)$")
_SEMI = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi(n):
    if isinstance(n, (int, float)):
        return n
    m = NOTE_RE.match(n)
    if not m:
        raise ValueError(n)
    s = _SEMI[m.group(1)] + {"#": 1, "b": -1, None: 0}[m.group(2)]
    return 12 * (int(m.group(3)) + 1) + s


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------------ voices
def _phase(freq, n):
    f = np.broadcast_to(np.asarray(freq, np.float64), (n,))
    return np.cumsum(f / SR) % 1.0


def pulse(freq, n, duty=0.5):
    return np.where(_phase(freq, n) < duty, 1.0, -1.0)


def triangle(freq, n):
    p = _phase(freq, n)
    tri = 2 * np.abs(2 * p - 1) - 1
    return np.round(tri * 7.5) / 7.5  # 4-bit stepped, like the NES


def noise(n, rate=8000, seed=0):
    hold = max(1, int(SR / rate))
    rng = np.random.default_rng(seed)
    v = rng.choice([-1.0, 1.0], size=n // hold + 2)
    return np.repeat(v, hold)[:n]


def env(n, a=0.004, d=0.06, s=0.6, r=0.03):
    t = np.arange(n) / SR
    dur = n / SR
    e = np.where(t < a, t / a, s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    rel = np.clip((dur - t) / r, 0, 1)
    return e * rel


# ------------------------------------------------------------------ buffer
class Track:
    def __init__(self, seconds):
        self.buf = np.zeros(int(seconds * SR) + SR, np.float64)

    def add(self, t, sig, gain=1.0):
        i = int(t * SR)
        if i >= len(self.buf) or i + len(sig) <= 0:
            return
        if i < 0:
            sig, i = sig[-i:], 0
        j = min(len(self.buf), i + len(sig))
        self.buf[i:j] += gain * sig[: j - i]

    def note(self, t, dur, m, wave="pulse", vol=0.2, duty=0.25, vib=0.0, a=0.004, d=0.08, s=0.55,
             slide=0.0):
        n = int(dur * SR)
        if n <= 8:
            return
        f = hz(midi(m)) * np.ones(n)
        if slide:
            f *= 2 ** (slide * np.linspace(0, 1, n) / 12)
        if vib and dur > 0.25:
            tt = np.arange(n) / SR
            f *= 1 + vib * np.sin(2 * np.pi * 5.5 * tt) * np.clip((tt - 0.15) / 0.2, 0, 1)
        if wave == "pulse":
            sig = pulse(f, n, duty)
        elif wave == "tri":
            sig = triangle(f, n)
        else:
            raise ValueError(wave)
        self.add(t, sig * env(n, a, d, s), vol)


# ------------------------------------------------------------------ drums
def kick(tr, t, vol=0.5):
    n = int(0.12 * SR)
    f = 150 * np.exp(-np.arange(n) / SR * 28) + 40
    tr.add(t, triangle(f, n) * env(n, 0.001, 0.05, 0.0, 0.02), vol)


def snare(tr, t, vol=0.25):
    n = int(0.11 * SR)
    tr.add(t, noise(n, 11000, int(t * 1000)) * env(n, 0.001, 0.04, 0.0, 0.03), vol)


def hat(tr, t, vol=0.08):
    n = int(0.035 * SR)
    tr.add(t, noise(n, 22000, int(t * 997)) * env(n, 0.0005, 0.012, 0.0, 0.01), vol)


# ------------------------------------------------------------------ chords
CHORDS = {"": [0, 4, 7], "m": [0, 3, 7], "7": [0, 4, 7, 10], "m7": [0, 3, 7, 10],
          "dim": [0, 3, 6], "maj7": [0, 4, 7, 11]}


def chord_notes(name, octave=4):
    m = re.match(r"^([A-G][#b]?)(.*)$", name)
    root = midi(m.group(1) + str(octave))
    return [root + i for i in CHORDS[m.group(2)]]


def parse_seq(s):
    """'E5:1 C6:2 r:1' -> [(note_or_None, steps), ...]"""
    out = []
    for tok in s.split():
        n, l = tok.split(":")
        out.append((None if n == "r" else n, float(l)))
    return out


# ------------------------------------------------------------------ songs
# Each song: steps_per_beat, melody seq, chords per bar [(chord, steps), ...], style.
ENTERTAINER = dict(  # Scott Joplin, 1902 (public domain)
    spb=4, bar=8,
    pickup="D5:1 D#5:1",
    melody=" ".join([
        "E5:1 C6:2 E5:1 C6:2 E5:1 C6:9",
        "C6:1 D6:1 D#6:1 E6:1 C6:1 D6:1 E6:2 B5:1 D6:2 C6:3 D5:1 D#5:1",
        "E5:1 C6:2 E5:1 C6:2 E5:1 C6:9",
        "A5:1 G5:1 F#5:1 A5:1 C6:1 E6:2 D6:1 C6:1 A5:1 D6:4 D5:1 D#5:1",
        "E5:1 C6:2 E5:1 C6:2 E5:1 C6:9",
        "C6:1 D6:1 D#6:1 E6:1 C6:1 D6:1 E6:2 B5:1 D6:2 C6:3 D5:1 D#5:1",
    ]),
    chords="C:8 C:8 C:8 G7:4 C:4 C:8 C:8 F:4 D7:4 G7:8 C:8 C:8 C:8 G7:4 C:4",
    style="rag",
)

MOUNTAIN_KING = dict(  # Edvard Grieg, 1875 (public domain)
    spb=2, bar=8,
    pickup="",
    melody=" ".join([
        "A4:1 B4:1 C5:1 D5:1 E5:1 C5:1 E5:2",
        "D#5:1 B4:1 D#5:2 D5:1 A#4:1 D5:2",
        "A4:1 B4:1 C5:1 D5:1 E5:1 C5:1 E5:1 A5:1",
        "G5:1 E5:1 C5:1 E5:1 G5:4",
    ]),
    chords="Am:32",
    style="march",
)

MORNING_MOOD = dict(  # Edvard Grieg, 1875 (public domain)
    spb=3, bar=6,
    pickup="",
    melody=" ".join([
        "G5:1 E5:1 D5:1 C5:1 D5:1 E5:1",
        "G5:1 E5:1 D5:1 C5:1 D5:1 E5:1",
        "D5:1 E5:1 G5:1 E5:1 G5:1 A5:1",
        "E5:1 A5:1 G5:1 E5:1 D5:1 C5:1",
        "C5:6",
    ]),
    chords="C:12 G:6 F:6 C:6",
    style="pastoral",
)


def _transpose(seq, k):
    out = []
    for n, l in seq:
        out.append((None if n is None else midi(n) + k, l))
    return out


def render_song(song, seconds, bpm, layers_at=(0, 0, 0), sections=None, gain=1.0, end_at=None):
    """Render a looping arrangement.

    bpm: number or callable(t) -> bpm (for accelerando).
    layers_at: times at which (lead, harmony, drums) enter.
    sections: list of semitone transpositions for successive loops of the melody.
    end_at: stop scheduling notes at this time.
    """
    tr = Track(seconds)
    spb = song["spb"]
    bpm_f = bpm if callable(bpm) else (lambda t: bpm)
    mel = parse_seq(song["melody"])
    pick = parse_seq(song["pickup"]) if song["pickup"] else []
    chords = [(c.split(":")[0], float(c.split(":")[1])) for c in song["chords"].split()]
    sections = sections or [0]
    end_at = seconds if end_at is None else end_at

    t, step_dur = 0.0, lambda tt: 60.0 / bpm_f(tt) / spb
    # pickup
    for n, l in pick:
        d = l * step_dur(t)
        if n:
            tr.note(t, d * 0.9, n, "pulse", 0.16, 0.25)
        t += d
    loop = 0
    lead_t, harm_t, drum_t = layers_at
    while t < end_at:
        k = sections[loop % len(sections)]
        # melody + harmony
        tm = t
        events = []
        for n, l in _transpose(mel, k):
            d = l * step_dur(tm)
            events.append((tm, d, n))
            tm += d
        loop_end = tm
        for (st, d, n) in events:
            if st >= end_at or n is None:
                continue
            if song["style"] == "march":
                # bass voices the theme two octaves down, staccato (like the bassoons)
                tr.note(st, d * 0.55, n - 24, "tri", 0.42, a=0.002, d=0.05, s=0.3)
                if st >= lead_t:
                    tr.note(st, d * 0.6, n, "pulse", 0.12, 0.25, a=0.002, d=0.05, s=0.5)
                if st >= harm_t:
                    tr.note(st, d * 0.6, n + 12, "pulse", 0.06, 0.125, a=0.002, d=0.04, s=0.4)
            else:
                lead_vol = 0.15 if st >= lead_t else 0.0
                if lead_vol:
                    tr.note(st, d * 0.92, n, "pulse", lead_vol, 0.25, vib=0.004)
                if st >= harm_t:  # NES-style echo voice
                    tr.note(st + 0.11, d * 0.85, n, "pulse", 0.05, 0.125, vib=0.004)
        # accompaniment
        tc, ci = t, 0
        total_steps = sum(l for _, l in mel)
        consumed = 0.0
        while consumed < total_steps and tc < end_at:
            name, l = chords[ci % len(chords)]
            ci += 1
            notes = chord_notes(name, 3)
            for s in range(int(l)):
                d = step_dur(tc)
                if tc >= end_at:
                    break
                pos = (consumed + s) % song["bar"]
                if song["style"] == "rag":
                    if pos % 4 == 0:
                        root = notes[0] - 12 if pos % 8 == 0 else notes[2] - 12
                        tr.note(tc, d * 1.6, root, "tri", 0.38, a=0.002, d=0.08, s=0.5)
                    elif pos % 4 == 2:
                        for nn in notes[:3]:
                            tr.note(tc, d * 0.8, nn + 12, "pulse", 0.035, 0.5, a=0.001, d=0.03, s=0.3)
                elif song["style"] == "march":
                    if tc >= drum_t:
                        if pos % 2 == 0:
                            kick(tr, tc, 0.45)
                        if pos % 4 == 2:
                            snare(tr, tc, 0.18)
                        hat(tr, tc, 0.05)
                elif song["style"] == "pastoral":
                    # rolling arpeggio, one chord tone per step
                    arp = notes + [notes[0] + 12]
                    tr.note(tc, d * 0.95, arp[int(pos) % len(arp)] + 12, "pulse", 0.045, 0.5,
                            a=0.002, d=0.1, s=0.4)
                    if pos % song["bar"] == 0:
                        tr.note(tc, d * song["bar"] * 0.95, notes[0] - 12, "tri", 0.32, d=0.4, s=0.6)
                if song["style"] == "rag" and tc >= drum_t:
                    if pos % 4 == 0:
                        kick(tr, tc, 0.28)
                    if pos % 4 == 2:
                        hat(tr, tc, 0.06)
                if song["style"] == "pastoral" and tc >= drum_t:
                    if pos % 3 == 0:
                        kick(tr, tc, 0.22 if pos % 6 == 0 else 0.12)
                    hat(tr, tc, 0.04)
                tc += d
            consumed += l
        t = loop_end
        loop += 1
    return tr.buf * gain


# ------------------------------------------------------------------ SFX
def sfx_blip(tr, t, pitch="A5", vol=0.06):
    tr.note(t, 0.03, pitch, "pulse", vol, 0.5, a=0.001, d=0.02, s=0.2)


def sfx_coin(tr, t, vol=0.16):
    tr.note(t, 0.06, "B5", "pulse", vol, 0.5, a=0.001, d=0.05, s=0.8)
    tr.note(t + 0.06, 0.22, "E6", "pulse", vol, 0.5, a=0.001, d=0.1, s=0.3)


def sfx_tick(tr, t, vol=0.05, pitch="E6"):
    tr.note(t, 0.018, pitch, "pulse", vol, 0.25, a=0.0005, d=0.01, s=0.2)


def sfx_select(tr, t, vol=0.12):
    tr.note(t, 0.05, "E5", "pulse", vol, 0.5, a=0.001, d=0.03, s=0.6)
    tr.note(t + 0.05, 0.08, "A5", "pulse", vol, 0.5, a=0.001, d=0.04, s=0.5)


def sfx_kaching(tr, t, vol=0.14):
    snare(tr, t, 0.12)
    for i, n in enumerate(["C6", "E6", "G6", "C7"]):
        tr.note(t + i * 0.035, 0.09, n, "pulse", vol, 0.25, a=0.001, d=0.05, s=0.4)
    sfx_coin(tr, t + 0.16, vol)


def sfx_buzz(tr, t, vol=0.22):
    n = int(0.5 * SR)
    tt = np.arange(n) / SR
    gate = (np.sin(2 * np.pi * 9 * tt) > -0.3).astype(float)
    sig = (pulse(98, n, 0.5) + pulse(104, n, 0.25)) * 0.5 * gate * env(n, 0.002, 0.5, 0.7, 0.05)
    tr.add(t, sig, vol)


def sfx_thud(tr, t, vol=0.35):
    n = int(0.16 * SR)
    f = 220 * np.exp(-np.arange(n) / SR * 18) + 50
    tr.add(t, triangle(f, n) * env(n, 0.001, 0.06, 0.0, 0.03), vol)


def sfx_whoosh(tr, t, dur=0.35, vol=0.07):
    n = int(dur * SR)
    rates = np.linspace(3000, 16000, n)
    sig = np.concatenate([noise(int(dur * SR / 8) + 1, r, i) for i, r in enumerate(rates[:: n // 8 + 1])])[:n]
    tr.add(t, sig * env(n, dur * 0.4, dur, 0.0, dur * 0.5), vol)


def sfx_fanfare(tr, t, vol=0.16):
    seq = [("C5", 0.09), ("E5", 0.09), ("G5", 0.09), ("C6", 0.18), ("G5", 0.09), ("C6", 0.4)]
    tt = t
    for n, d in seq:
        tr.note(tt, d * 0.95, n, "pulse", vol, 0.25, vib=0.006)
        tr.note(tt, d * 0.95, midi(n) - 12, "tri", 0.3)
        tt += d


def sfx_pop(tr, t, k, vol=0.07):
    tr.note(t, 0.04, 72 + (k % 24), "pulse", vol, 0.125, a=0.0005, d=0.03, s=0.2)


# ------------------------------------------------------------------ mix
def lowpass(x, cutoff=9000):
    taps = 31
    fc = cutoff / SR
    n = np.arange(taps) - (taps - 1) / 2
    h = np.sinc(2 * fc * n) * np.hamming(taps)
    h /= h.sum()
    return np.convolve(x, h, mode="same")


def mixdown(music, sfx, seconds, music_gain=0.55, duck=None, path="out.wav"):
    n = int(seconds * SR)
    m = np.zeros(n)
    s = np.zeros(n)
    m[: min(n, len(music))] = music[:n]
    s[: min(n, len(sfx))] = sfx[:n]
    if duck is not None:
        m *= duck[:n]
    mix = lowpass(m * music_gain + s)
    # fade in/out a touch to avoid clicks at loop points
    f = int(0.02 * SR)
    mix[:f] *= np.linspace(0, 1, f)
    mix[-f:] *= np.linspace(1, 0, f)
    ref = np.percentile(np.abs(mix), 99.7) or 1
    mix = np.tanh(mix / ref * 0.85) * 0.95  # loud but soft-limited
    stereo = np.stack([mix, mix], 1)
    pcm = (stereo * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return path


def duck_curve(seconds, windows, depth=0.15, fade=0.08):
    """windows: list of (t0, t1) where music drops to `depth`."""
    n = int(seconds * SR)
    g = np.ones(n)
    tt = np.arange(n) / SR
    for t0, t1 in windows:
        a = np.clip((tt - (t0 - fade)) / fade, 0, 1) * np.clip(((t1 + fade) - tt) / fade, 0, 1)
        g = np.minimum(g, 1 - (1 - depth) * a)
    return g
