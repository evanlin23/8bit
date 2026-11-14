"""Concept reel 2 (shopping-spree format): Can Elon buy all 5?

v2.1 after re-audit: opens on a big lineup of all five items, one item on stage at a time,
single pop on the payoff, no stamp leaking into the loop seam.
"""
import math

from pixelshop import audio as A
from pixelshop import sprites as S
from pixelshop import ui
from pixelshop.gfx import background, ease_in, ease_io, ease_out, seg

NET_WORTH = 889e9       # Forbes real-time, Nov 13 2026
MEDIAN_PAY = 1232 * 52  # BLS median weekly earnings, full-time, Q3 2026 -> $64,064/yr

ITEMS = [  # (label, price, sprite, scale on stage)
    ("EVERY NFL TEAM", 304e9, S.FOOTBALL, 4),
    ("MCDONALD'S", 195e9, S.BURGER, 4),
    ("APOLLO PROGRAM", 309e9, S.ROCKET, 3),
    ("TWITTER (AGAIN)", 44e9, S.BIRD, 4),
    ("DISNEY", 190e9, S.CASTLE, 3),
]
LEFT = NET_WORTH - sum(p for _, p, _, _ in ITEMS[:4])   # $37B
YEARS = round(LEFT / MEDIAN_PAY)                        # 577,547

FACTS = [
    "Elon Musk net worth: $889.3B - Forbes Real-Time Billionaires, Nov 13 2026",
    "All 32 NFL teams: ~$304B (Forbes 2026 average $9.5B x 32)",
    "McDonald's market cap: ~$195B (Nov 2026; quotes ranged $193-199B)",
    "Apollo program: ~$309B in 2025 dollars - The Planetary Society",
    "Twitter: $44B (2022 purchase price)",
    "Disney market cap: ~$190B (late Oct/Nov 2026 quotes ranged $183-197B)",
    f"Leftover {ui.fmt_money(LEFT)} / $64,064 (BLS median full-time pay, Q3 2026: $1,232/wk) = {YEARS:,} years",
]

SECONDS = 12.0          # 12 bars of the rag at 120 bpm -> seamless loop
STARTS = [0.6, 1.85, 3.0, 4.05, 5.0]
T_DENY = 5.3
T_SWAP = 6.15
T_COUNT, T_LAND = 6.35, 8.35
T_REWIND = 9.75
T_LINEUP_BACK = 11.0     # lineup drops back in for the loop
CX = 118


def paid(i, t):
    s = STARTS[i]
    return ease_io(seg(t, s + 0.2, s + 0.7))


def wallet_at(t):
    if t >= T_REWIND:
        return LEFT + (NET_WORTH - LEFT) * ease_io(seg(t, T_REWIND + 0.1, SECONDS - 0.4))
    return NET_WORTH - sum(ITEMS[i][1] * paid(i, t) for i in range(4))


def lineup_visible(t):
    return t < STARTS[0] + 0.15 or t >= T_LINEUP_BACK


def draw_lineup(cv, t):
    """All five items side by side with their prices (the hook)."""
    sc = 2
    widths = [spr.shape[1] * sc for _, _, spr, _ in ITEMS]
    gap = (cv.w - 16 - sum(widths)) // 6
    x = 8 + gap
    leaving = seg(t, STARTS[0], STARTS[0] + 0.15) if t < T_LINEUP_BACK else 0
    for k, (_, price, spr, _) in enumerate(ITEMS):
        w, h = spr.shape[1] * sc, spr.shape[0] * sc
        drop = 0
        if t >= T_LINEUP_BACK:  # pop in place, one by one (stays clear of the title)
            p_in = seg(t, T_LINEUP_BACK + k * 0.08, T_LINEUP_BACK + k * 0.08 + 0.2)
            if p_in <= 0:
                x += w + gap
                continue
            drop = -int(round(10 * math.sin(math.pi * p_in)))
        wave = int(round(2 * max(0.0, math.sin(t * 2.618 * 2 - k * 0.9))))
        y = 150 - h + drop - wave - int(leaving * 140)
        cv.blit(spr, x, y, scale=sc)
        if not leaving:
            cv.text(x + w // 2, 158, ui.fmt_money(price).replace("$", ""), "gold", align="center")
        x += w + gap


def current_item(t):
    return max(i for i, s in enumerate(STARTS) if t >= s) if t >= STARTS[0] else 0


class Reel:
    name = "elon"
    seconds = SECONDS
    music_gain = 0.55

    def draw(self, cv, t, hook=False):
        ui.shake(cv, t, [(T_DENY, T_DENY + 0.4), (T_LAND, T_LAND + 0.25)], amp=4)
        background(cv, t, seed=11)
        if T_SWAP <= t < T_REWIND + 0.8:
            ui.title(cv, ["HE GOT 4 OF 5.", f"CHANGE: {ui.fmt_money(LEFT)}"], y=28, fill="green_d",
                     accent={1: "gold"})
        else:
            ui.title(cv, ["CAN ELON BUY", "ALL 5 OF THESE?"], y=28, accent={1: "gold"})

        # ---------------------------------------------------------- stage
        counting = T_COUNT <= t < T_REWIND + 0.7
        if lineup_visible(t):
            draw_lineup(cv, t)
        if not counting and STARTS[0] <= t < T_REWIND:
            i = current_item(t)
            label, price, spr, sc = ITEMS[i]
            h, w = spr.shape[0] * sc, spr.shape[1] * sc
            slide = int((1 - ease_out(seg(t, STARTS[i], STARTS[i] + 0.15))) * 160)
            cv.blit(spr, 135 - w // 2 + slide, 160 - h, scale=sc)
            cv.text(135 + slide, 166, label, "white", scale=2, align="center")
            denied = i == 4 and t >= T_DENY
            cv.text(135 + slide, 186, ui.fmt_money(price), "red" if denied else "gold", scale=3, align="center")
            if i < 4 and t >= STARTS[i] + 0.7:
                ui.stamp(cv, "SOLD!", t, STARTS[i] + 0.7, color="green", scale=3, y=100)
        if counting:
            p = seg(t, T_COUNT, T_LAND - 0.1)
            yrs = YEARS if p >= 1 else int(YEARS * ease_out(p))
            if t >= T_REWIND:
                yrs = int(YEARS * (1 - seg(t, T_REWIND, T_REWIND + 0.7)))
            pop = 1 if T_LAND <= t < T_LAND + 0.15 else 0
            cv.text(135, 112, "THAT'S", "cream", scale=2, align="center")
            cv.text(135, 134, f"{yrs:,}", "gold", scale=5 + pop, align="center")
            cv.text(135, 178, "YEARS OF", "white", scale=2, align="center")
            cv.text(135, 198, "AVERAGE PAY", "white", scale=2, align="center")

        # ---------------------------------------------------------- lower zone
        broke = T_DENY <= t < T_REWIND
        hop = int(5 * abs(math.sin(math.pi * seg(t, T_LAND, T_LAND + 0.3))))
        cv.blit(S.shopper("suit", sweat=broke and t < T_SWAP), 16, 222 - hop, scale=3)
        cv.text(56, 226, "ELON MUSK", "white", scale=2)
        cv.text(56, 246, ui.fmt_money(wallet_at(t)), "red" if T_DENY <= t < T_SWAP else "gold", scale=4)

        for k, (_, _, spr, _) in enumerate(ITEMS):  # checklist
            x, y = 14 + k * 42, 290
            cv.rect(x, y, 40, 34, "ink")
            cv.rect(x + 1, y + 1, 38, 32, "navy")
            h, w = spr.shape[:2]
            if h > 28:
                spr, h = spr[:28], 28
            cv.blit(spr, x + 20 - w // 2, y + 17 - h // 2)
            if k < 4 and STARTS[k] + 0.75 <= t < T_REWIND + 0.25 * (4 - k):
                cv.blit(S.CHECK, x + 22, y + 16, scale=2)
            if k == 4 and T_DENY + 0.05 <= t < T_REWIND:
                cv.blit(S.XMARK, x + 12, y + 9, scale=2)

        for k in range(4):
            s = STARTS[k]
            ui.coin_stream(cv, t, s + 0.15, s + 0.55, (70, 250), (135, 150), rate=30, flight=0.35,
                           arc=30, seed=k + 3)

        ui.stamp(cv, "NOT ENOUGH", t, T_DENY, color="red", scale=3, y=98, dur=T_SWAP - T_DENY)
        ui.stamp(cv, "GOLD!", t, T_DENY + 0.1, color="red", scale=4, y=126, dur=T_SWAP - T_DENY - 0.1)
        cv.ox = cv.oy = 0

    # ------------------------------------------------------------ audio
    def music(self):
        return A.render_song(A.ENTERTAINER, SECONDS, 120, layers_at=(0, 0, 0), pickup=False)

    def duck_windows(self):
        return [(T_DENY, T_DENY + 0.45)]

    def sfx(self, tr):
        A.sfx_blip(tr, 0.25, "C6", 0.08)
        for i in range(4):
            s = STARTS[i]
            A.sfx_whoosh(tr, s, 0.15, 0.06)
            A.sfx_select(tr, s + 0.1)
            for k in range(7):
                A.sfx_tick(tr, s + 0.2 + k * 0.07, 0.045, pitch=84 - k)
            A.sfx_kaching(tr, s + 0.7, 0.12)
            A.sfx_thud(tr, s + 0.75, 0.25)
        A.sfx_whoosh(tr, STARTS[4], 0.15, 0.06)
        A.sfx_select(tr, STARTS[4] + 0.1)
        A.sfx_buzz(tr, T_DENY, 0.3)
        A.sfx_thud(tr, T_DENY, 0.5)
        A.sfx_thud(tr, T_SWAP, 0.35)
        for k in range(22):
            A.sfx_tick(tr, T_COUNT + (T_LAND - 0.1 - T_COUNT) * ease_out(k / 22), 0.06, pitch=72 + k)
        A.sfx_kaching(tr, T_LAND, 0.13)
        A.sfx_fanfare(tr, T_LAND + 0.15, 0.13)
        for i in range(3):
            A.sfx_coin(tr, T_LAND + 0.75 + i * 0.2, 0.04)
        A.sfx_whoosh(tr, T_REWIND, 0.7, 0.09)
        for i in range(8):
            A.sfx_tick(tr, T_REWIND + 0.1 + i * 0.12, 0.05, pitch=90 - i * 2)
        for k in range(5):
            A.sfx_pop(tr, T_LINEUP_BACK + k * 0.08 + 0.2, 12 + k * 3)


REEL = Reel()
