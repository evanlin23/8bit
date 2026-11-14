# 8bit

Tooling for 8-bit style short videos.

## Item Shop (concept reels)

A retro RPG shop where famous people try to buy absurdly expensive things.
Three formats, one per concept reel in `concepts/`:

| Reel | Format | Song (public domain, chip arrangement) |
|---|---|---|
| `apollo.mp4` - Could MrBeast buy the Apollo program? | yes/no: price reveal, payment, "NOT ENOUGH GOLD!", count | In the Hall of the Mountain King (Grieg) |
| `elon.mp4` - Can Elon buy all 5 of these? | spree: buy items one by one until broke | The Entertainer (Joplin) |
| `bugatti.mp4` - How long to buy a Bugatti? | grind: age ticks up past life expectancy until you can afford it | Morning Mood (Grieg) |

Each reel's numbers and sources are in `concepts/<name>_sources.txt` (also in `FACTS` in `reels/<name>.py`).

Render:

    pip install numpy pillow
    python3 make_reels.py                 # all reels -> out/
    python3 make_reels.py elon            # one reel
    python3 make_reels.py elon --sheet    # fast contact-sheet preview
    python3 make_reels.py --lint          # pacing check: dead air > 0.7s, silence, loop seam

Requires `ffmpeg` on PATH. Output is 1080x1920, 30 fps, AAC audio, 12s seamless loops.

House rules (from the independent review): something moves by 0.3s; one focal element at a time;
text at 2x minimum and key numbers 5-6x, centred; nothing in the bottom 20% or under the right-hand
button rail (x > 228 below y 215 in canvas pixels); reveal = count, then stamp, then title; no dead
air over 0.7s; the last frame must match frame 0.

Code layout:
- `pixelshop/gfx.py` - 270x480 pixel canvas (upscaled 4x), bitmap font, RPG windows, CRT post-process
- `pixelshop/sprites.py` - original pixel sprites
- `pixelshop/audio.py` - NES-style chiptune synth (pulse/triangle/noise), song arrangements, SFX
- `pixelshop/ui.py` - shared shop widgets (wallet, dialog typewriter, stamps, coin streams, loop wipe)
- `reels/*.py` - one file per reel: timeline, visuals, sound cues, facts

## data/
- `countries-50m.json` - world country shapes (TopoJSON) from [world-atlas](https://github.com/topojson/world-atlas) (Natural Earth, public domain).
- `states-10m.json` - US state shapes from [us-atlas](https://github.com/topojson/us-atlas).
- `flags/*.png` - country flags rasterized from [flag-icons](https://github.com/lipis/flag-icons) (MIT, see `flags/LICENSE-flag-icons.txt`) with `tools/rasterize_flags.js`.
