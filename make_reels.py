"""Render the Item Shop concept reels.

usage:
  python3 make_reels.py                 # render all reels to out/
  python3 make_reels.py apollo          # render one
  python3 make_reels.py apollo --sheet  # contact sheet of stills (fast preview)
"""
import importlib
import os
import sys

from pixelshop.render import contact_sheet, render

REELS = ["apollo", "elon", "bugatti"]


def main(argv):
    names = [a for a in argv if not a.startswith("--")] or REELS
    os.makedirs("out", exist_ok=True)
    for name in names:
        reel = importlib.import_module(f"reels.{name}").REEL
        if "--sheet" in argv:
            n = 24
            times = [i * reel.seconds / n for i in range(n)]
            print(contact_sheet(reel, times, f"out/{name}_sheet.png", scale=1, cols=8))
            continue
        out = render(reel, f"out/{name}.mp4")
        with open(f"out/{name}_sources.txt", "w") as f:
            f.write("\n".join(reel_facts(name)) + "\n")
        print(out)


def reel_facts(name):
    return importlib.import_module(f"reels.{name}").FACTS


if __name__ == "__main__":
    main(sys.argv[1:])
