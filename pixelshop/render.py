"""Render a reel (frames + chiptune audio) to an MP4 with ffmpeg."""
import os
import subprocess
import tempfile

from PIL import Image

from . import audio
from .gfx import Canvas, to_output, VW, VH, SCALE

FPS = 30


def render(reel, out_path, crf=18):
    secs = reel.seconds
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="pixelshop_")
    wav = os.path.join(tmp, "audio.wav")

    music = reel.music()
    sfx = audio.Track(secs)
    reel.sfx(sfx)
    duck = audio.duck_curve(secs, reel.duck_windows()) if reel.duck_windows() else None
    audio.mixdown(music, sfx.buf, secs, music_gain=reel.music_gain, duck=duck, path=wav)

    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{VW * SCALE}x{VH * SCALE}", "-r", str(FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    cv = Canvas()
    for i in range(int(secs * FPS)):
        t = i / FPS
        reel.draw(cv, t)
        proc.stdin.write(to_output(cv).tobytes())
    proc.stdin.close()
    proc.wait()
    if proc.returncode:
        raise RuntimeError("ffmpeg failed")
    return out_path


def still(reel, t, path, scale=1):
    cv = Canvas()
    reel.draw(cv, t)
    img = Image.fromarray(to_output(cv) if scale == 4 else cv.a)
    if scale not in (1, 4):
        img = img.resize((VW * scale, VH * scale), Image.NEAREST)
    img.save(path)
    return path


def contact_sheet(reel, times, path, scale=1, cols=6):
    ims = []
    for t in times:
        cv = Canvas()
        reel.draw(cv, t)
        ims.append(Image.fromarray(cv.a).resize((VW * scale, VH * scale), Image.NEAREST))
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (VW * scale * cols, VH * scale * rows))
    for k, im in enumerate(ims):
        sheet.paste(im, ((k % cols) * VW * scale, (k // cols) * VH * scale))
    sheet.save(path)
    return path
