"""Concept reel 3 (grind format): how long to buy a Bugatti on an average paycheck?

v2 after review: 12s seamless loop, grind starts at 0.3s, life-expectancy finish line
("will he make it?"), payoff is AGE 86 big and centred.
"""
import math

from pixelshop import audio as A
from pixelshop import sprites as S
from pixelshop import ui
from pixelshop.gfx import background, ease_io, ease_out, seg

PRICE = 4.1e6            # Bugatti Tourbillon base price EUR 3.8M ~= $4.1M
PAY = 1232 * 52          # BLS median weekly earnings, full-time, Q3 2026 -> $64,064/yr
YEARS = math.ceil(PRICE / PAY)   # 64
START_AGE = 22
END_AGE = START_AGE + YEARS      # 86
LIFE_EXP = 79                    # CDC NCHS: US life expectancy at birth, 2024 = 79.0

FACTS = [
    "Bugatti Tourbillon base price: EUR 3.8M (~$4.1M) - Bugatti via press coverage; 250 to be built",
    "Median full-time pay: $1,232/week (BLS, Q3 2026) = $64,064/yr",
    f"$4.1M / $64,064 = {PRICE / PAY:.2f} -> {YEARS} years; start at {START_AGE}, done at {END_AGE}",
    "US life expectancy at birth: 79.0 years in 2024 - CDC NCHS Data Brief 548 (Jan 2026)",
]

SECONDS = 12.0          # two passes of the theme at 100 bpm (6/8) -> seamless loop
T_GRIND, T_DONE = 0.3, 7.3
T_SWAP = 7.9
T_DRIVE = 8.9
T_REWIND = 10.4
CX = 118
BAR_X0, BAR_X1, BAR_Y = 16, 200, 330   # life bar, age 22 -> 88
AGE_MAX = 88
MINI_CAR = S.ascii_sprite(["...kkkk...", "..kBccBk..", ".kbbbbbbk.", "kbbbbbbbbk", ".kGk..kGk."])


def age_at(t):
    if t >= T_REWIND:
        return END_AGE - YEARS * ease_io(seg(t, T_REWIND + 0.2, SECONDS - 0.2))
    p = seg(t, T_GRIND, T_DONE)
    return START_AGE + YEARS * (1 - (1 - p) ** 2)   # fast early, slows near the finish


T_DEATH = T_GRIND + (T_DONE - T_GRIND) * (1 - math.sqrt(1 - (LIFE_EXP - START_AGE) / YEARS))  # ~5.0s


def bar_x(age):
    return int(BAR_X0 + (BAR_X1 - BAR_X0) * (age - START_AGE) / (AGE_MAX - START_AGE))


class Reel:
    name = "bugatti"
    seconds = SECONDS
    music_gain = 0.55

    def draw(self, cv, t, hook=False):
        ui.shake(cv, t, [(T_DEATH, T_DEATH + 0.3), (T_DONE, T_DONE + 0.3)], amp=3)
        background(cv, t, seed=23)
        if T_SWAP <= t < T_REWIND + 0.9:
            ui.title(cv, [f"DELIVERED AT {END_AGE}.", f"LIFE EXPECTANCY: {LIFE_EXP}."], y=28, fill="red_d",
                     accent={1: "gold"})
        else:
            ui.title(cv, ["HOW LONG TO BUY", "A BUGATTI?"], y=28, accent={1: "gold"})

        age = age_at(t)
        ghost = LIFE_EXP <= age and t < T_REWIND + 0.6

        # ---------------------------------------------------------- stage: the car
        drive = ease_io(seg(t, T_DRIVE, T_REWIND)) if t < T_REWIND else 0
        back = 1 - ease_out(seg(t, T_REWIND + 0.2, T_REWIND + 0.9)) if t >= T_REWIND else 0
        car_x = 63 + int(drive * 230) - int(back * 230)
        bob = int(round(math.sin(t * 2.618) * 1.5))  # 5 cycles per loop
        flash = T_DONE <= t < T_DONE + 0.12
        cv.blit(S.HYPERCAR, car_x, 104 + bob, scale=4, tint="white" if flash else None)
        if T_SWAP <= t < T_REWIND and drive > 0:
            cv.blit_ghost(S.worker(1.0), car_x + 64, 96 + bob, scale=2, phase=int(t * 8))
        cv.rect(56, 150, 158, 4, "gray_d")
        cv.rect(56, 150, 158, 1, "gray")
        if T_DONE <= t < T_DRIVE:
            for k in range(6):
                a = t * 3 + k
                cv.blit(S.SPARK, 135 + 70 * math.cos(a) - 2, 126 + 22 * math.sin(a * 1.3) - 2)
        cv.text(135, 158, ui.fmt_money(PRICE), "gold", scale=3, align="center")
        cv.text(135, 184, f"MEDIAN PAY: ${PAY // 1000}K/YR", "cream", scale=2, align="center")
        cv.text(135, 202, "SAVING 100% OF IT", "cream", scale=2, align="center")

        # ---------------------------------------------------------- lower zone: worker + age
        frame = int(t * 8) % 2 if T_GRIND <= t < T_DONE else 0
        wy = 222
        if ghost:
            float_y = int(round(math.sin(t * 4.1888) * 2)) - 3
            if not (T_SWAP <= t < T_REWIND and drive > 0):
                cv.blit_ghost(S.worker(1.0, frame), 16, wy + float_y, scale=4, phase=int(t * 8))
        else:
            cv.blit(S.worker((age - START_AGE) / YEARS, frame), 16, wy, scale=4)
        cv.text(66, 226, "AGE", "cream", scale=2)
        a_int = int(age)
        col = "red" if a_int >= LIFE_EXP else "white"
        if T_DONE <= t < T_SWAP:
            col = "gold"
        pop = 1 if T_DONE <= t < T_DONE + 0.2 else 0
        cv.text(66, 246 - pop * 4, str(a_int), col, scale=6 + pop)
        saved = min(PRICE, (age - START_AGE) * PAY)
        cv.text(CX + 56, 230, "SAVED", "cream", scale=2, align="center")
        cv.text(CX + 56, 250, ui.fmt_money(saved) if saved >= 1e6 else f"${saved / 1e3:,.0f}K",
                "gold", scale=2, align="center")

        # life bar 22 -> 90, finish lines at 79 (tomb) and 86 (car)
        cv.bar(BAR_X0, BAR_Y, BAR_X1 - BAR_X0, 12, (age - START_AGE) / (AGE_MAX - START_AGE),
               fg="red" if a_int >= LIFE_EXP else "green", hi="white")
        x79, x86 = bar_x(LIFE_EXP), bar_x(END_AGE)
        cv.rect(x79, BAR_Y - 4, 2, 20, "red")
        cv.blit(S.TOMB, x79 - 7, BAR_Y - 22, scale=2)
        cv.text(x79 - 2, BAR_Y + 18, str(LIFE_EXP), "red", scale=2, align="right")
        if T_DONE <= t < T_REWIND + 0.6:
            cv.rect(x86, BAR_Y - 4, 2, 20, "gold")
            cv.blit(MINI_CAR, x86 - 9, BAR_Y - 16, scale=2)
            cv.text(x86 + 4, BAR_Y + 18, str(END_AGE), "gold", scale=2)
        else:
            cv.text(BAR_X1 + 6, BAR_Y - 1, "?", "gold", scale=2)

        # ---------------------------------------------------------- stamps
        if T_DEATH <= t < T_DEATH + 1.0:
            ui.stamp(cv, "LIFE EXPECTANCY", t, T_DEATH, color="red", scale=2, y=112)
            ui.stamp(cv, "REACHED", t, T_DEATH + 0.08, color="red", scale=3, y=136)

        cv.ox = cv.oy = 0

    # ------------------------------------------------------------ audio
    def music(self):
        return A.render_song(A.MORNING_MOOD, SECONDS, 100, layers_at=(0, 0, 0))

    def duck_windows(self):
        return [(T_DEATH, T_DEATH + 0.4)]

    def sfx(self, tr):
        prev, last = START_AGE, -1.0
        for i in range(int((T_DONE - T_GRIND) * 60)):
            tt = T_GRIND + i / 60
            a = int(age_at(tt))
            if a > prev:
                if tt - last > 0.08:
                    A.sfx_coin(tr, tt, 0.05)
                    last = tt
                prev = a
        for k in range(3):  # alarm at the life-expectancy line
            A.sfx_blip(tr, T_DEATH + k * 0.16, "A5", 0.12)
            A.sfx_blip(tr, T_DEATH + k * 0.16 + 0.08, "E5", 0.12)
        A.sfx_thud(tr, T_DEATH, 0.45)
        A.sfx_kaching(tr, T_DONE, 0.14)
        A.sfx_fanfare(tr, T_DONE + 0.2, 0.14)
        A.sfx_thud(tr, T_SWAP, 0.35)
        for k in range(8):  # engine rev as the ghost drives off
            A.sfx_tick(tr, T_DRIVE + k * 0.18, 0.07, pitch=48 + k * 3)
        A.sfx_whoosh(tr, T_DRIVE + 0.8, 0.6, 0.08)
        A.sfx_whoosh(tr, T_REWIND, 0.8, 0.09)
        for i in range(12):
            A.sfx_tick(tr, T_REWIND + 0.1 + i * 0.12, 0.05, pitch=90 - i * 2)


REEL = Reel()
