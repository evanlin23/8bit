"""Concept reel 3 (grind format): how long to afford a Bugatti on a median paycheck?"""
import math

import numpy as np

from pixelshop import audio as A
from pixelshop import sprites as S
from pixelshop import ui
from pixelshop.gfx import background, ease_out, seg

PRICE = 4.1e6            # Bugatti Tourbillon base price EUR 3.8M ~= $4.1M
PAY = 1232 * 52          # BLS median weekly earnings, full-time, Q3 2026 -> $64,064/yr
YEARS = math.ceil(PRICE / PAY)   # 64
START_AGE = 22
BUILT = 250              # Tourbillon production run
ELON = 889e9
ELON_PCT = BUILT * PRICE / ELON * 100   # ~0.12%

FACTS = [
    "Bugatti Tourbillon base price: EUR 3.8M (~$4.1M) - Bugatti via press coverage; 250 to be built",
    "Median full-time pay: $1,232/week (BLS, Q3 2026) = $64,064/yr",
    f"$4.1M / $64,064 = {PRICE / PAY:.2f} -> {YEARS} years; start at {START_AGE}, done at {START_AGE + YEARS}",
    f"All 250 cars = ${BUILT * PRICE / 1e9:.3f}B = {ELON_PCT:.2f}% of Elon Musk's $889B (Forbes, Nov 13 2026)",
]

T_RULES = 1.3
T_START = 4.6
T_GRIND = 4.9
T_DONE = 15.6
T_DELIV = 16.6
T_ELON = 20.2
T_END = 23.0
SECONDS = 25.5

TXT_RULES = "RULES: SAVE EVERY CENT OF A MEDIAN U.S. FULL-TIME PAYCHECK. NO RENT. NO FOOD."
TXT_DELIV = f"DELIVERED AT AGE {START_AGE + YEARS}. ONLY {BUILT} WILL EVER BE BUILT."
TXT_END = "NEXT CUSTOMER? COMMENT WHAT YOU'D GRIND FOR."

MINI_CAR = S.ascii_sprite([
    "...kkkk...",
    "..kBccBk..",
    ".kbbbbbbk.",
    "kbbbbbbbbk",
    ".kGk..kGk.",
])


def years_at(t):
    p = seg(t, T_GRIND, T_DONE)
    return YEARS * (p ** 1.7)


class Reel:
    name = "bugatti"
    seconds = SECONDS
    music_gain = 0.55

    def draw(self, cv, t, hook=False):
        if hook:
            t = 0.0
        ui.shake(cv, t, [(T_DONE, T_DONE + 0.3)], amp=3)
        background(cv, t, seed=23)
        ui.hud(cv, t, "003")
        if t < T_ELON:
            ui.title(cv, ["HOW LONG TO BUY A", "BUGATTI ON AN", "AVERAGE PAYCHECK?"], accent={1: "gold"})
        else:
            ui.title(cv, ["ELON COULD BUY ALL", f"{BUILT} WITH {ELON_PCT:.2f}%", "OF HIS FORTUNE."],
                     fill="red_d", accent={1: "gold"})
        y_years = years_at(t)
        yrs = int(y_years)
        age_frac = y_years / YEARS

        # ---- stage: sky orbit, car on a pedestal, worker at a desk
        if t < T_ELON:
            ang = y_years / 8 * 2 * math.pi
            cx, cy, r = 135, 182, 74
            sx, sy = cx - r * math.cos(ang), cy - r * abs(math.sin(ang)) * 0.9
            day = (int(y_years / 4) % 2) == 0
            cv.blit(S.SUN if day else S.MOON_SMALL, sx - 5, sy - 5)
            bob = int(round(math.sin(t * 2) * 1.5))
            cv.blit(S.CAR, 71, 106 + bob, scale=4)
            cv.rect(62, 156, 146, 4, "gray_d")
            cv.rect(62, 156, 146, 1, "gray")
            if t >= T_DONE:
                for k in range(6):  # sparkles
                    a = t * 3 + k
                    cv.blit(S.SPARK, 135 + 60 * math.cos(a) - 2, 140 + 22 * math.sin(a * 1.3) - 2)
            cv.text(cv.w // 2, 165, "PRICE " + ui.fmt_money(PRICE), "gold", scale=2, align="center")
            frame = int(t * 6) % 2 if T_GRIND <= t < T_DONE else 0
            cv.blit(S.worker(age_frac, frame), 78, 186, scale=3)
            cv.blit(S.DESK, 112, 204, scale=2)
            cv.blit(S.CALENDAR, 18, 112)
            cv.text(25, 128, str(yrs), "white", align="center")
        else:
            k = int(min(BUILT, BUILT * seg(t, T_ELON + 0.2, T_ELON + 2.2) ** 0.7))
            for i in range(k):
                r, c = divmod(i, 20)
                cv.blit(MINI_CAR, 16 + c * 12, 110 + r * 10)
            cv.text(cv.w - 14, 240, f"x{k}", "gold", scale=2, align="right")

        # ---- stats panel
        cv.window(8, 262, cv.w - 16, 66, fill="navy_d", border="gold")
        cv.text(16, 270, f"YEAR {yrs}", "white", scale=2)
        cv.text(cv.w - 16, 270, f"AGE {START_AGE + yrs}", "cream" if age_frac < 0.75 else "red", scale=2,
                align="right")
        saved = min(PRICE, y_years * PAY)
        cv.text(16, 294, f"SAVED {ui.fmt_money(saved) if saved >= 1e6 else f'${saved:,.0f}'}", "gold")
        cv.text(cv.w - 16, 294, f"+${PAY:,}/YR", "green", align="right")
        cv.bar(16, 307, cv.w - 32, 12, saved / PRICE, fg="green", hi="white")

        # ---- dialog
        if t < T_RULES:
            ui.dialog(cv, "", 0, 1)
        elif t < T_GRIND:
            ui.dialog(cv, TXT_RULES, t, T_RULES, speaker="SHOPKEEP")
        elif t < T_DONE:
            ui.dialog(cv, "...", t, T_GRIND, speaker="GRINDING", cps=3)
        elif t < T_END:
            ui.dialog(cv, TXT_DELIV, t, T_DELIV, color="white")
        else:
            ui.dialog(cv, TXT_END, t, T_END, color="gold")

        ui.stamp(cv, "START!", t, T_START, color="green", scale=3, y=226, dur=0.6)
        ui.stamp(cv, "PURCHASED!", t, T_DONE, color="green", scale=3, y=226, dur=T_ELON - T_DONE)
        if t >= T_END + 0.3:
            ui.sources(cv, ["SOURCES: BLS Q3 2026 MEDIAN PAY,", "BUGATTI EUR3.8M BASE, FORBES"])
        if not hook:
            ui.loop_wipe(cv, t, SECONDS - 0.55, SECONDS - 0.05, lambda c: self.draw(c, 0.0, hook=True))
        cv.ox = cv.oy = 0

    # ------------------------------------------------------------ audio
    def music(self):
        def bpm(t):
            return 84 + 70 * seg(t, T_GRIND, T_DONE) ** 1.5
        a = A.render_song(A.MORNING_MOOD, SECONDS, bpm, layers_at=(0, T_GRIND, T_GRIND + 3), end_at=T_DONE)
        b = A.render_song(A.MORNING_MOOD, SECONDS, 84, layers_at=(0, 99, 99), gain=0.8)
        i = int((T_DELIV + 0.4) * A.SR)
        a[i:] += b[: len(a) - i]
        return a

    def duck_windows(self):
        return [(T_DONE, T_DONE + 1.0)]

    def sfx(self, tr):
        for tt in ui.type_times(TXT_RULES, T_RULES):
            A.sfx_blip(tr, tt)
        A.sfx_select(tr, T_START)
        last = -1.0
        prev = 0
        for i in range(int((T_DONE - T_GRIND) * 60)):
            tt = T_GRIND + i / 60
            y = int(years_at(tt))
            if y > prev:
                if tt - last > 0.09:
                    A.sfx_coin(tr, tt, 0.06)
                    last = tt
                prev = y
        A.sfx_kaching(tr, T_DONE, 0.14)
        A.sfx_fanfare(tr, T_DONE + 0.25, 0.14)
        for tt in ui.type_times(TXT_DELIV, T_DELIV):
            A.sfx_blip(tr, tt, "E5", 0.04)
        prev = 0
        for i in range(int(2.4 * 40)):
            tt = T_ELON + 0.2 + i / 40
            k = int(min(BUILT, BUILT * seg(tt, T_ELON + 0.2, T_ELON + 2.2) ** 0.7))
            if k - prev >= 6:
                A.sfx_pop(tr, tt, k // 6)
                prev = k
        for tt in ui.type_times(TXT_END, T_END):
            A.sfx_blip(tr, tt, "C6", 0.04)
        A.sfx_whoosh(tr, SECONDS - 0.6, 0.5)


REEL = Reel()
