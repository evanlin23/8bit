"""Concept reel 2 (shopping-spree format): Elon Musk goes shopping until he's broke."""
from pixelshop import audio as A
from pixelshop import sprites as S
from pixelshop import ui
from pixelshop.gfx import background, back_out, ease_in, ease_io, ease_out, seg

NET_WORTH = 889e9      # Forbes real-time, Nov 13 2026
MEDIAN_PAY = 1232 * 52  # BLS median weekly earnings, full-time, Q3 2026 -> $64,064/yr

ITEMS = [  # (label, price, sprite, scale)
    ("EVERY NFL TEAM", 304e9, S.FOOTBALL, 1),
    ("MCDONALD'S", 195e9, S.BURGER, 1),
    ("APOLLO PROGRAM", 309e9, S.ROCKET, 1),
    ("TWITTER (AGAIN)", 44e9, S.BIRD, 1),
    ("DISNEY", 190e9, S.CASTLE, 1),
]
LEFT = NET_WORTH - sum(p for _, p, _, _ in ITEMS[:4])   # $37B
YEARS = LEFT / MEDIAN_PAY                                # ~577,000

FACTS = [
    "Elon Musk net worth: $889.3B - Forbes Real-Time Billionaires, Nov 13 2026",
    "All 32 NFL teams: ~$304B (Forbes 2026 average $9.5B x 32)",
    "McDonald's market cap: ~$195B (Nov 2026; quotes ranged $193-199B)",
    "Apollo program: ~$309B in 2025 dollars - The Planetary Society",
    "Twitter: $44B (2022 purchase price)",
    "Disney market cap: ~$190B (late Oct/Nov 2026 quotes ranged $183-197B)",
    f"Leftover {ui.fmt_money(LEFT)} / $64,064 (BLS median full-time pay, Q3 2026: $1,232/wk) = {YEARS:,.0f} years",
]

T_HELLO = 1.3
BUYS = [3.4, 6.6, 9.3, 11.6]   # accelerating purchases
T_DENY = 13.8
T_LEFT = 16.0
T_YEARS = 17.0
T_END = 22.2
SECONDS = 25.0
PAY_DUR = [1.5, 1.3, 1.2, 0.8]

TXT_HELLO = "WELCOME, MR. MUSK. WHAT'LL IT BE?"
TXT_BUY = ["32 TEAMS. ONE OWNER.", "EVERY SINGLE LOCATION.", "ALL 6 MOON LANDINGS.", "AGAIN. WHY NOT."]
TXT_DENY = f"DISNEY IS $190B. YOU HAVE {ui.fmt_money(LEFT)}."
TXT_YEARS = "THAT'S ONE AVERAGE U.S. PAYCHECK... FOR ABOUT 577,000 YEARS."
TXT_END = "NEXT CUSTOMER? COMMENT WHO SHOULD SHOP NEXT."

ROW_Y0, ROW_H = 146, 27
SLOT_Y = 292


def wallet_at(t):
    v = NET_WORTH
    for i, tb in enumerate(BUYS):
        v -= ITEMS[i][1] * ease_io(seg(t, tb, tb + PAY_DUR[i]))
    return v


class Reel:
    name = "elon"
    seconds = SECONDS
    music_gain = 0.55

    def cursor_row(self, t):
        row = 0
        for i, tb in enumerate(BUYS + [T_DENY]):
            if t >= tb - 0.45:
                row = i
        return row

    def draw(self, cv, t, hook=False):
        if hook:
            t_eff = 0.0
        else:
            t_eff = t
        t = t_eff
        ui.shake(cv, t, [(T_DENY, T_DENY + 0.45)], amp=4)
        background(cv, t, seed=11)
        ui.hud(cv, t, "002")
        if t < T_LEFT:
            ui.title(cv, ["ELON MUSK HAS $889B.", "LET'S GO SHOPPING."], accent={1: "gold"})
        else:
            ui.title(cv, ["LEFTOVER:", ui.fmt_money(LEFT)], fill="green_d", accent={1: "gold"})

        v = wallet_at(t)
        ui.wallet(cv, 86, "ELON MUSK", "FORBES, NOV 13 2026", v, v / NET_WORTH, h=46, warn=T_DENY <= t < T_LEFT)

        # ---- shop list
        cv.window(8, 136, cv.w - 16, 5 * ROW_H + 12, fill="navy")
        cur = self.cursor_row(t)
        for i, (label, price, spr, sc) in enumerate(ITEMS):
            y = ROW_Y0 + i * ROW_H
            bought = i < 4 and t >= BUYS[i] + PAY_DUR[i]
            selected = i == cur and t >= T_HELLO
            if selected:
                cv.rect(14, y - 3, cv.w - 28, ROW_H - 3, "navy_d")
            # icon (fits a 22x22 box), hidden once it flies to the bag
            if not (i < 4 and t >= BUYS[i] + PAY_DUR[i] * 0.6):
                h, w = spr.shape[:2]
                cv.blit(spr, 34 - w // 2, y + 10 - h // 2 if h <= 22 else y - 1, scale=1)
            col = "gray_d" if bought else ("red" if i == 4 and t >= T_DENY else "white")
            cv.text(56, y + 3, label, col)
            cv.text(cv.w - 18, y + 3, ui.fmt_money(price), "gray_d" if bought else "gold", align="right")
            if selected and int(t * 4) % 2 == 0 and not bought:
                cv.text(16, y + 3, ">", "gold", shadow=None)
            if bought:
                cv.rect(56, y + 6, ui.text_w(label), 1, "red")
                p = seg(t, BUYS[i] + PAY_DUR[i], BUYS[i] + PAY_DUR[i] + 0.15)
                sc2 = 1 + int(round((1 - back_out(p)) * 2))
                cv.text(cv.w - 70, y + 12, "SOLD", "red", scale=sc2, align="center")

        # ---- bag (inventory)
        cv.window(8, SLOT_Y - 6, cv.w - 16, 40, fill="navy_d", border="gold")
        cv.text(16, SLOT_Y + 8, "BAG", "gold")
        for k in range(5):
            sx = 44 + k * 42
            cv.rect(sx, SLOT_Y - 1, 36, 30, "ink")
            cv.rect(sx + 1, SLOT_Y, 34, 28, "navy")
        for i in range(4):
            tb, dur = BUYS[i], PAY_DUR[i]
            t0, t1 = tb + dur * 0.6, tb + dur * 0.6 + 0.45
            if t < t0:
                continue
            spr = ITEMS[i][2]
            h, w = spr.shape[:2]
            sx, sy = 44 + i * 42 + 18 - w // 2, SLOT_Y + 14 - min(h, 26) // 2
            p = ease_in(seg(t, t0, t1))
            fx, fy = 34 - w // 2, ROW_Y0 + i * ROW_H + 10 - min(h, 22) // 2
            x = fx + (sx - fx) * p
            y = fy + (sy - fy) * p - 30 * (1 - (2 * p - 1) ** 2)
            cv.blit(spr if h <= 26 else spr[:26], x, y)

        # ---- coins from wallet to the row being bought
        for i, tb in enumerate(BUYS):
            ui.coin_stream(cv, t, tb, tb + PAY_DUR[i] * 0.8, (24, 100), (cv.w - 50, ROW_Y0 + i * ROW_H + 6),
                           rate=18 + 6 * i, flight=0.45, arc=30, seed=i + 3)

        # ---- dialog
        if t < T_HELLO:
            ui.dialog(cv, "", 0, 1)
        elif t < BUYS[0]:
            ui.dialog(cv, TXT_HELLO, t, T_HELLO, speaker="SHOPKEEP")
        elif t < T_DENY:
            i = max(k for k, tb in enumerate(BUYS) if t >= tb)
            ui.dialog(cv, TXT_BUY[i], t, BUYS[i], speaker=f"BOUGHT: {ITEMS[i][0]}")
        elif t < T_YEARS:
            ui.dialog(cv, TXT_DENY, t, T_DENY + 0.4, speaker="SHOPKEEP", color="cream")
        elif t < T_END:
            ui.dialog(cv, TXT_YEARS, t, T_YEARS, color="white")
        else:
            ui.dialog(cv, TXT_END, t, T_END, color="gold")

        # ---- big moments
        ui.stamp(cv, "NOT ENOUGH", t, T_DENY, color="red", scale=3, y=190, dur=T_LEFT - T_DENY)
        ui.stamp(cv, "GOLD!", t, T_DENY + 0.12, color="red", scale=4, y=218, dur=T_LEFT - T_DENY - 0.12)
        if T_YEARS <= t:
            p = seg(t, T_YEARS, T_YEARS + 2.6)
            yrs = round(YEARS) if p >= 1 else int(YEARS * ease_out(p))
            cv.window(30, 160, cv.w - 60, 74, fill="ink", border="gold")
            cv.text(cv.w // 2, 172, f"{yrs:,}", "gold", scale=4, align="center")
            cv.text(cv.w // 2, 210, "YEARS OF WORK", "white", scale=2, align="center")
        if t >= T_END + 0.3:
            ui.sources(cv, ["SOURCES: FORBES, PLANETARY SOCIETY,", "MARKET CAPS NOV 2026, BLS Q3 2026"])
        if not hook:
            ui.loop_wipe(cv, t, SECONDS - 0.55, SECONDS - 0.05, lambda c: self.draw(c, 0.0, hook=True))
        cv.ox = cv.oy = 0

    # ------------------------------------------------------------ audio
    def music(self):
        def bpm(t):
            return 92 + 26 * seg(t, BUYS[0], T_DENY)
        a = A.render_song(A.ENTERTAINER, SECONDS, bpm, layers_at=(0, BUYS[0], BUYS[1]), end_at=T_DENY)
        b = A.render_song(A.ENTERTAINER, SECONDS, 88, layers_at=(0, 99, 99), gain=0.8)
        i = int((T_YEARS - 0.1) * A.SR)
        a[i:] += b[: len(a) - i]
        return a

    def duck_windows(self):
        return [(T_DENY, T_DENY + 0.6)]

    def sfx(self, tr):
        for tt in ui.type_times(TXT_HELLO, T_HELLO):
            A.sfx_blip(tr, tt)
        for i, tb in enumerate(BUYS):
            A.sfx_blip(tr, tb - 0.45, "C6", 0.08)
            A.sfx_select(tr, tb)
            n = int(PAY_DUR[i] / 0.07)
            for k in range(n):
                A.sfx_tick(tr, tb + 0.1 + k * 0.07, 0.04, pitch=84 - (k % 8))
            A.sfx_kaching(tr, tb + PAY_DUR[i], 0.12)
            A.sfx_thud(tr, tb + PAY_DUR[i] * 0.6 + 0.45, 0.3)
            for tt in ui.type_times(TXT_BUY[i], tb + 0.05):
                A.sfx_blip(tr, tt, "E5", 0.04)
        A.sfx_blip(tr, T_DENY - 0.45, "C6", 0.08)
        A.sfx_buzz(tr, T_DENY, 0.3)
        A.sfx_thud(tr, T_DENY, 0.5)
        for tt in ui.type_times(TXT_DENY, T_DENY + 0.4):
            A.sfx_blip(tr, tt, "E5", 0.04)
        for k in range(26):
            A.sfx_tick(tr, T_YEARS + 2.6 * ease_out(k / 26) * 0.98, 0.06, pitch=72 + k)
        A.sfx_fanfare(tr, T_YEARS + 2.7, 0.12)
        for tt in ui.type_times(TXT_END, T_END):
            A.sfx_blip(tr, tt, "C6", 0.04)
        A.sfx_whoosh(tr, SECONDS - 0.6, 0.5)


REEL = Reel()
