"""Concept reel 1 (yes/no format): Could MrBeast buy the Moon landing?"""
import math

from pixelshop import audio as A
from pixelshop import sprites as S
from pixelshop import ui
from pixelshop.gfx import background, ease_in, ease_out, seg

# Facts (see FACTS for sources)
NET_WORTH = 2.6e9        # Fortune estimate, Jan 2026
APOLLO = 309e9           # Planetary Society: $25.8B (1960-73) = ~$309B in 2025 dollars
PAID_FRAC = NET_WORTH / APOLLO          # 0.84%
NEEDED = math.ceil(APOLLO / NET_WORTH)  # 119

FACTS = [
    "Apollo program: $25.8B (1960-1973), about $309B in 2025 dollars - The Planetary Society, planetary.org/space-policy/cost-of-apollo",
    "MrBeast net worth: about $2.6B - Fortune estimate (Jan 2026), mostly his Beast Industries stake",
    f"$309B / $2.6B = {APOLLO / NET_WORTH:.1f} -> {NEEDED} MrBeasts; $2.6B / $309B = {PAID_FRAC * 100:.2f}%",
]

T_INTRO_TXT = 1.4
T_PRICE = 3.7
T_PRICE_END = 5.4
T_ASK = 5.7
T_YES = 7.0
T_PAY = 7.3
T_PAY_END = 11.2
T_FAIL = 11.35
T_OWED = 12.6
T_NEED = 15.0
T_END = 18.9
SECONDS = 21.0

TXT_INTRO = "THE WHOLE APOLLO PROGRAM. 6 MOON LANDINGS. PRICED IN TODAY'S MONEY."
TXT_ASK = "BUY IT?        > YES      NO"
TXT_OWED = f"PAID: {PAID_FRAC * 100:.1f}%.  STILL OWED: {ui.fmt_money(APOLLO - NET_WORTH)}."
TXT_NEED = f"TO AFFORD ONE MOON PROGRAM, YOU'D NEED {NEEDED} MRBEASTS."
TXT_END = "NEXT CUSTOMER? COMMENT WHO SHOULD SHOP NEXT."


class Reel:
    name = "apollo"
    seconds = SECONDS
    music_gain = 0.6

    # ------------------------------------------------------------ visuals
    def wallet_value(self, t):
        return NET_WORTH * (1 - ease_in(seg(t, T_PAY, T_PAY_END)))

    def draw_hook(self, cv, t=0.0):
        self.draw(cv, 0.0, hook=True)

    def draw(self, cv, t, hook=False):
        ui.shake(cv, t, [(T_FAIL, T_FAIL + 0.45)], amp=4)
        background(cv, t, seed=7)
        ui.hud(cv, t, "001")
        if t < T_NEED or hook:
            ui.title(cv, ["COULD MRBEAST BUY", "THE MOON LANDING?"], accent={1: "gold"})
        else:
            ui.title(cv, [f"HE'D NEED {NEEDED}", "MRBEASTS."], fill="red_d", accent={0: "gold"})

        # ---- stage
        if t < T_NEED or hook:
            bob = int(round(math.sin(t * 1.6) * 2))
            cv.blit(S.MOON, 142, 92 + bob, scale=2)
            lift = 0 if t < T_PAY else int(ease_in(seg(t, T_PAY, T_FAIL)) * 18)
            if T_FAIL <= t < T_NEED:
                lift = int(18 * (1 - ease_out(seg(t, T_FAIL, T_FAIL + 0.6))))  # rocket sinks back
            cv.blit(S.ROCKET, 50, 128 - lift, scale=4)
            if T_PAY <= t < T_FAIL:
                cv.blit(S.FLAME[int(t * 14) % 2], 50, 128 - lift + 88, scale=4)
        else:
            self.draw_bags(cv, t)

        # ---- item / price window
        cv.window(8, 226, cv.w - 16, 48, fill="navy")
        cv.text(cv.w // 2, 234, "ITEM: APOLLO PROGRAM 1960-73", "cream", align="center")
        if t < T_PRICE and not hook or hook:
            price = "$???"
        else:
            p = seg(t, T_PRICE, T_PRICE_END)
            price = ui.fmt_money(APOLLO * ease_out(p)) if p < 1 else ui.fmt_money(APOLLO)
        cv.text(cv.w // 2, 247, "PRICE " + price, "gold", scale=2, align="center")
        if t >= T_PAY and not hook:
            paid = PAID_FRAC * ease_in(seg(t, T_PAY, T_PAY_END))
            cv.bar(20, 266, cv.w - 40, 5, paid, fg="green", hi="white")

        # ---- wallet
        broke = t >= T_FAIL and not hook
        ui.wallet(cv, 280, "MRBEAST", "EST. NET WORTH, 2026", 0 if broke else self.wallet_value(t),
                  self.wallet_value(t) / NET_WORTH if not hook else 1.0, warn=broke)

        # ---- coins
        if not hook and T_PAY <= t < T_PAY_END + 0.6:
            rate = 8 + 22 * seg(t, T_PAY, T_PAY_END)
            ui.coin_stream(cv, t, T_PAY, T_PAY_END, (24, 290), (68, 200), rate=rate, arc=60)

        # ---- dialog
        if hook:
            ui.dialog(cv, "", 0, 1)
        elif t < T_ASK:
            ui.dialog(cv, TXT_INTRO, t, T_INTRO_TXT, speaker="SHOPKEEP")
        elif t < T_FAIL:
            n = ui.dialog(cv, "BUY IT?", t, T_ASK, speaker="SHOPKEEP")
            if n >= 7:
                yes_sel = t >= T_YES
                blink = int(t * 4) % 2 == 0 or yes_sel
                cv.text(40, 366, ">" if blink else " ", "gold")
                cv.text(52, 366, "YES", "green" if yes_sel else "white", scale=1)
                cv.text(120, 366, "NO", "white")
        elif t < T_NEED:
            ui.dialog(cv, TXT_OWED, t, T_OWED, color="cream")
        elif t < T_END:
            ui.dialog(cv, TXT_NEED, t, T_NEED + 0.3, color="white")
        else:
            ui.dialog(cv, TXT_END, t, T_END, color="gold")

        if not hook:
            ui.stamp(cv, "NOT ENOUGH", t, T_FAIL, color="red", scale=3, y=150, dur=T_NEED - T_FAIL)
            ui.stamp(cv, "GOLD!", t, T_FAIL + 0.12, color="red", scale=4, y=178, dur=T_NEED - T_FAIL - 0.12)
            if t >= T_END + 0.3:
                ui.sources(cv, ["SOURCES: PLANETARY SOCIETY (2025 $),", "FORTUNE EST. (2026)"])
            ui.loop_wipe(cv, t, SECONDS - 0.55, SECONDS - 0.05, lambda c: self.draw(c, 0.0, hook=True))
        cv.ox = cv.oy = 0

    def bags_shown(self, t):
        return int(min(NEEDED, NEEDED * ease_in(seg(t, T_NEED + 0.2, T_NEED + 3.0) ** 0.6)))

    def draw_bags(self, cv, t):
        k = self.bags_shown(t)
        cols, dx, dy = 15, 16, 12
        x0 = (cv.w - (cols - 1) * dx - 14) // 2
        for i in range(k):
            r, c = divmod(i, cols)
            cv.blit(S.MONEYBAG, x0 + c * dx, 92 + r * dy)
        if k:
            cv.text(cv.w - 14, 210, f"x{k}", "gold", scale=2, align="right")

    # ------------------------------------------------------------ audio
    def music(self):
        def bpm(t):
            return 112 + 88 * seg(t, 1.0, T_FAIL) ** 1.6
        a = A.render_song(A.MOUNTAIN_KING, SECONDS, bpm, layers_at=(T_PRICE, T_PAY, T_ASK),
                          end_at=T_FAIL)
        b = A.render_song(A.MOUNTAIN_KING, SECONDS, 104, layers_at=(99, 99, 99), gain=0.9)
        out = a.copy()
        i = int((T_OWED - 0.2) * A.SR)
        out[i:] += b[: len(out) - i]
        return out

    def duck_windows(self):
        return [(T_FAIL, T_FAIL + 0.6)]

    def sfx(self, tr):
        for tt in ui.type_times(TXT_INTRO, T_INTRO_TXT):
            A.sfx_blip(tr, tt)
        steps = 22
        for i in range(steps):
            A.sfx_tick(tr, T_PRICE + (T_PRICE_END - T_PRICE) * ease_out(i / steps) * 0.98, pitch=76 + i % 12)
        A.sfx_thud(tr, T_PRICE_END)
        A.sfx_kaching(tr, T_PRICE_END + 0.02, 0.1)
        for tt in ui.type_times("BUY IT?", T_ASK):
            A.sfx_blip(tr, tt)
        A.sfx_select(tr, T_YES)
        # payment coins, getting denser
        t = T_PAY + 0.5
        while t < T_PAY_END + 0.5:
            A.sfx_coin(tr, t, 0.07)
            t += 0.24 - 0.17 * seg(t, T_PAY, T_PAY_END)
        A.sfx_buzz(tr, T_FAIL, 0.28)
        A.sfx_thud(tr, T_FAIL, 0.5)
        for tt in ui.type_times(TXT_OWED, T_OWED):
            A.sfx_blip(tr, tt, "E5")
        prev = 0
        for i in range(int((T_NEED + 3.2 - T_NEED) * 30)):
            tt = T_NEED + i / 30
            k = self.bags_shown(tt)
            if k > prev:
                A.sfx_pop(tr, tt, k)
                prev = k
        A.sfx_fanfare(tr, T_NEED + 3.1, 0.12)
        for tt in ui.type_times(TXT_END, T_END):
            A.sfx_blip(tr, tt, "C6", 0.04)
        A.sfx_whoosh(tr, SECONDS - 0.6, 0.5)


REEL = Reel()
