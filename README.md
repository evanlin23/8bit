# 8bit

Tooling for 8-bit style short videos.

## Item Shop (concept reels)

A retro RPG shop where famous people try to buy absurdly expensive things.
Three formats, one per concept reel in `concepts/`:

| Reel | Format | Song (public domain, chip arrangement) |
|---|---|---|
| `apollo.mp4` - Could MrBeast buy the Moon landing? | yes/no: price reveal, payment, "NOT ENOUGH GOLD!" | In the Hall of the Mountain King (Grieg) |
| `elon.mp4` - Elon has $889B, let's go shopping | spree: buy down a shop list until broke | The Entertainer (Joplin) |
| `bugatti.mp4` - How long to buy a Bugatti on an average paycheck? | grind: years tick by until you can afford it | Morning Mood (Grieg) |

Each reel's numbers and sources are in `concepts/<name>_sources.txt` (also in `FACTS` in `reels/<name>.py`).

Render:

    pip install numpy pillow
    python3 make_reels.py                 # all reels -> out/
    python3 make_reels.py elon            # one reel
    python3 make_reels.py elon --sheet    # fast contact-sheet preview

Requires `ffmpeg` on PATH. Output is 1080x1920, 30 fps, AAC audio.

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
