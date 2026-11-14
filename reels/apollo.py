"""Concept reel 1 (yes/no format): Could MrBeast buy the Apollo program?

v2 after review: 12s seamless loop, price rolls from 0.2s, answer by 3.2s, count then stamp then title.
"""
import math

from pixelshop import audio as A
from pixelshop import sprites as S
from pixelshop import ui
from pixelshop.gfx import background, ease_in, ease_io, ease_out, seg

NET_WORTH = 2.6e9        # Fortune estimate, Jan 2026
APOLLO = 309e9           # Planetary Society: $25.8B (1960-73) = ~$309B in 2025 dollars
PAID_FRAC = NET_WORTH / APOLLO          # 0.84%
NEEDED = math.ceil(APOLLO / NET_WORTH)  # 119

FACTS = [
    "Apollo program (all 6 Moon landings): $25.8B (1960-1973), about $309B in 2025 dollars - The Planetary Society, planetary.org/space-policy/cost-of-apollo",
    "MrBeast net worth: about $2.6B - Fortune estimate (Jan 2026), mostly his Beast Industries stake",
    f"$309B / $2.6B = {APOLLO / NET_WORTH:.1f} -> {NEEDED} MrBeasts; $2.6B / $309B = {PAID_FRAC * 100:.2f}%",
]

SECONDS = 12.0          # 8 bars of the theme at 160 bpm -> music loops seamlessly
T_ROLL, T_PRICE = 0.2, 1.5
T_PAY, T_PAY_END = 1.85, 3.3
T_FAIL = 3.35
T_PAID = 4.3
T_COUNT, T_LAND = 5.5, 8.7
T_REWIND = 10.0

CX = 118  # centre of the lower zone (keeps clear of the Shorts button rail)


def wallet_value(t):
    drain = seg(t, T_PAY, T_PAY_END)
    refill = ease_io(seg(t, T_REWIND + 0.3, SECONDS - 0.15))
    return NET_WORTH * (1 - drain) if t < T_REWIND else NET_WORTH * refill


def bags_at(t):
    if t < T_COUNT:
        return 0
    if t < T_REWIND:
        return max(1, int(min(NEEDED, NEEDED * ease_in(seg(t, T_COUNT, T_LAND - 0.15) ** 0.55))))
    return int(NEEDED * (1 - seg(t, T_REWIND, T_REWIND + 0.9)))


class Reel:
    name = "apollo"
    seconds = SECONDS
    music_gain = 0.6

    def draw(self, cv, t, hook=False):
        ui.shake(cv, t, [(T_FAIL, T_FAIL + 0.4), (T_LAND, T_LAND + 0.25)], amp=4)
        background(cv, t, seed=7)
        landed = T_LAND <= t < T_REWIND + 1.0
        if landed:
            ui.title(cv, ["HE'D NEED", f"{NEEDED} MRBEASTS."], y=28, fill="red_d", accent={1: "gold"})
        else:
            ui.title(cv, ["COULD MRBEAST BUY", "THE APOLLO PROGRAM?"], y=28, accent={1: "gold"})

        counting = T_COUNT <= t < T_REWIND + 0.9
        # ---------------------------------------------------------- stage (full width)
        if not counting:
            bob = int(round(math.sin(t * 2.618) * 2))  # 5 cycles per loop
            cv.blit(S.MOON, 150, 98 + bob, scale=2)
            lift = int(ease_in(seg(t, T_PAY, T_FAIL)) * 14)
            if T_FAIL <= t:
                lift = int(14 * (1 - ease_out(seg(t, T_FAIL, T_FAIL + 0.4))))
            rumble = int(math.sin(t * 60)) if T_PAY <= t < T_FAIL else 0
            cv.blit(S.ROCKET, 52 + rumble, 100 - lift, scale=4)
            if T_PAY <= t < T_FAIL:
                cv.blit(S.FLAME[int(t * 14) % 2], 52 + rumble, 192 - lift, scale=4)
        else:
            k = bags_at(t)
            cols, dx, dy = 15, 17, 13
            x0 = (cv.w - (cols - 1) * dx - 16) // 2
            for i in range(k):  # a crowd of 119 of him
                r, c = divmod(i, cols)
                hop = int(round(2 * max(0.0, math.sin(t * 9 - c * 0.6)))) if landed else 0
                cv.blit(S.HEAD, x0 + c * dx, 98 + r * dy - hop, scale=2)

        # ---------------------------------------------------------- lower zone
        if not counting:
            cv.text(CX, 220, "PRICE", "cream", scale=2, align="center")
            if t < T_ROLL or t >= SECONDS - 0.35:
                price, col = "$???", "gold"
            else:
                p = seg(t, T_ROLL, T_PRICE)
                price = ui.fmt_money(APOLLO * ease_out(p))
                col = "white" if T_PRICE <= t < T_PRICE + 0.08 else "gold"
            cv.text(CX, 240, price, col, scale=5, align="center")
            broke = T_FAIL <= t < T_REWIND
            hop = int(6 * math.sin(math.pi * seg(t, 1.55, 1.8)))
            cv.blit(S.shopper("hoodie", sweat=broke), 16, 290 - hop, scale=3)
            cv.text(56, 296, "MRBEAST", "white", scale=2)
            v = 0 if broke else wallet_value(t)
            cv.text(56, 316, ui.fmt_money(v), "red" if broke else "gold", scale=4)
        else:
            k = bags_at(t)
            pulse = 1 if T_LAND <= t < T_LAND + 0.15 else 0  # one pop, then hold
            cv.text(CX, 236, f"x{k}", "gold", scale=6 + pulse, align="center")
            cv.text(CX, 292, "MRBEASTS", "white", scale=2, align="center")

        # coins: wallet -> price
        if T_PAY <= t < T_PAY_END + 0.5:
            ui.coin_stream(cv, t, T_PAY, T_PAY_END, (70, 322), (CX + 30, 250), rate=26, flight=0.42, arc=40)

        # ---------------------------------------------------------- stamps
        ui.stamp(cv, "NOT ENOUGH", t, T_FAIL, color="red", scale=3, y=118, dur=T_PAID - T_FAIL)
        ui.stamp(cv, "GOLD!", t, T_FAIL + 0.1, color="red", scale=4, y=146, dur=T_PAID - T_FAIL - 0.1)
        if T_PAID <= t < T_COUNT:
            pct = PAID_FRAC * 100 * ease_out(seg(t, T_PAID, T_PAID + 0.45))
            ui.stamp(cv, f"{pct:.1f}% PAID", t, T_PAID, color="gold", scale=4, y=130)
        cv.ox = cv.oy = 0

    # ------------------------------------------------------------ audio
    def music(self):
        return A.render_song(A.MOUNTAIN_KING, SECONDS, 160, layers_at=(0, 0, 0),
                             sections=[0, 7])

    def duck_windows(self):
        return [(T_FAIL, T_FAIL + 0.45)]

    def sfx(self, tr):
        for i in range(16):
            A.sfx_tick(tr, T_ROLL + (T_PRICE - T_ROLL) * ease_out(i / 16) * 0.97, 0.06, pitch=76 + i)
        A.sfx_thud(tr, T_PRICE, 0.4)
        A.sfx_select(tr, 1.55)
        t = T_PAY + 0.35
        while t < T_PAY_END + 0.4:
            A.sfx_coin(tr, t, 0.07)
            t += 0.13
        A.sfx_buzz(tr, T_FAIL, 0.3)
        A.sfx_thud(tr, T_FAIL, 0.5)
        for i in range(8):
            A.sfx_tick(tr, T_PAID + i * 0.055, 0.06, pitch=84 + i)
        A.sfx_thud(tr, T_PAID + 0.45, 0.3)
        prev = 0
        for i in range(int((T_LAND - T_COUNT) * 60)):
            tt = T_COUNT + i / 60
            k = bags_at(tt)
            if k > prev:
                A.sfx_pop(tr, tt, k)
                prev = k
        A.sfx_kaching(tr, T_LAND, 0.13)
        A.sfx_fanfare(tr, T_LAND + 0.15, 0.13)
        for i in range(4):
            A.sfx_coin(tr, T_LAND + 0.7 + i * 0.2, 0.04)
        A.sfx_whoosh(tr, T_REWIND, 0.8, 0.09)
        for i in range(12):
            A.sfx_tick(tr, T_REWIND + 0.1 + i * 0.12, 0.05, pitch=90 - i * 2)


REEL = Reel()
