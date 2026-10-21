#!/usr/bin/env python3
"""Relative pin difficulty + round-score distribution for a tournament page.

Reads a built tournament page (e.g. 3m-open-2026/index.html) and answers two
questions the pages themselves do not:

  1. Is each of this round's pins in a TOUGHER or EASIER location than a
     typical placement on that same hole?  The pages publish absolute
     projections (hole 9 is hard), which conflates the hole with the pin.
     This scores pin-vs-hole, which is the part a setup can actually change.

  2. What round-score distribution do those pins imply, and what does an
     under at a given line need to be worth?

Both sections of the page are parsed out of the HTML rather than re-entered by
hand, so a refreshed page re-runs without edits.

Usage
-----
    python3 tools/pin_difficulty.py 3m-open-2026/index.html
    python3 tools/pin_difficulty.py 3m-open-2026/index.html --par 71 --sims 40000
    python3 tools/pin_difficulty.py 3m-open-2026/index.html --tee-hole 16

Caveats
-------
* The archive is whatever the page carries. Check how many placements per hole
  came back ("archive: N placements/hole") before trusting a zone read -- some
  pages carry one edition (4/hole), some carry six (24/hole), and the on-page
  caveat text is not reliable about which. See notes/known-data-issues.md.
* Zone labels are coarse (front/mid/back x left/right). A pin many paces from
  the nearer edge is treated as CENTRE and scored against its depth band only,
  because "9 paces from the left edge" is not a left pin.
* Shrinkage (--k) pulls thin zone samples toward the band, then the hole. With
  n=1 placements a raw zone mean is noise; do not read a single hole's delta
  as signal, only the distribution across 18.
"""

import argparse
import html
import random
import re
import statistics
import sys
from collections import Counter

ND = statistics.NormalDist()


def _inv(p):
    return ND.inv_cdf(min(max(p, 1e-6), 1 - 1e-6))


# ---------------------------------------------------------------- parsing

def _strip(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def parse_archive(doc):
    """Per-hole historical placements from the 'Greens, Hole by Hole' cards.

    Returns {hole: {"par": int, "rows": [{rnd, zone, pp, b, bg, y}, ...]}}.
    """
    holes = {}
    for card in re.split(r'<div class="pcard">', doc)[1:]:
        m = re.search(r'hc-num">(\d+)<.*?hc-par">Par (\d+)\s*(?:&middot;|·)\s*([\d]+)y', card, re.S)
        if not m:
            continue
        hole, par = int(m.group(1)), int(m.group(2))
        rows = []
        for tr in re.findall(r"<tr>(?:(?!</tr>).)*</tr>", card, re.S):
            if "<th" in tr:
                continue
            tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
            if len(tds) < 6:
                continue
            cells = [_strip(t) for t in tds]
            if not re.fullmatch(r"R\d", cells[0]):
                continue
            try:
                rows.append(
                    {
                        "rnd": cells[0],
                        "zone": cells[1],
                        "pp": float(cells[2].replace("+", "")),
                        "b": int(re.sub(r"\D", "", cells[3])),
                        "bg": int(re.sub(r"\D", "", cells[4])),
                        "y": int(re.sub(r"\D", "", cells[5])),
                    }
                )
            except ValueError:
                continue
        if rows:
            holes[hole] = {"par": par, "rows": rows}
    return holes


def parse_pin_sheet(doc):
    """This round's 18 pins from the pin-sheet table (class 'pintbl')."""
    m = re.search(r'<table class="[^"]*pintbl[^"]*">.*?<tbody>(.*?)</tbody>', doc, re.S)
    if not m:
        return []
    pins = []
    for tr in re.findall(r"<tr>(.*?)</tr>", m.group(1), re.S):
        cells = [_strip(t) for t in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(cells) < 8:
            continue
        depth = re.match(r"(\d+)\s*/\s*(\d+)", cells[2])
        side = re.match(r"(\d+)\s*([LR])", cells[4])
        if not (depth and side):
            continue
        pins.append(
            {
                "hole": int(cells[0]),
                "par": int(re.sub(r"\D", "", cells[1])),
                "depth": int(depth.group(1)),
                "total": int(depth.group(2)),
                "band": cells[3],
                "paces": int(side.group(1)),
                "side": side.group(2),
                "b": int(re.sub(r"\D", "", cells[6])),
                "bg": int(re.sub(r"\D", "", cells[7])),
            }
        )
    return pins


# ------------------------------------------------------- relative difficulty

BAND = {"front": "front", "middle": "mid", "back": "back"}


def relative_difficulty(pins, archive, k=6.0, centre_paces=8):
    """Score each pin against a typical placement on its own hole.

    Shrinks zone -> band -> hole mean, so a zone seen once does not dominate.
    Positive delta = this location plays tougher than that hole's average pin.
    """
    out = []
    for pin in pins:
        hole = archive.get(pin["hole"])
        if not hole:
            continue
        rows = hole["rows"]
        band = BAND.get(pin["band"], pin["band"])
        centre = pin["paces"] >= centre_paces
        side = None if centre else ("left" if pin["side"] == "L" else "right")

        hole_mu = statistics.mean(r["pp"] for r in rows)
        hole_b = statistics.mean(r["b"] for r in rows)
        hole_bg = statistics.mean(r["bg"] for r in rows)

        band_rows = [r for r in rows if r["zone"].startswith(band)]
        if band_rows:
            band_mu = statistics.mean(r["pp"] for r in band_rows)
            band_est = (len(band_rows) * band_mu + k * hole_mu) / (len(band_rows) + k)
        else:
            band_est = hole_mu

        zone_rows = [r for r in rows if r["zone"] == f"{band}-{side}"] if side else []
        if zone_rows:
            zone_mu = statistics.mean(r["pp"] for r in zone_rows)
            est = (len(zone_rows) * zone_mu + k * band_est) / (len(zone_rows) + k)
            basis = f"zone n={len(zone_rows)}"
        else:
            est = band_est
            basis = f"band n={len(band_rows)}"

        out.append(
            {
                **pin,
                "zone": f"{band}-{side or 'CENTRE'}",
                "est": est,
                "hole_mu": hole_mu,
                "delta": est - hole_mu,
                "hole_b": hole_b,
                "hole_bg": hole_bg,
                "depth_pct": 100.0 * pin["depth"] / pin["total"],
                "basis": basis,
            }
        )
    return out


def tee_move_posterior(archive, hole, pin, fwd_max=320):
    """Bayesian read on whether a hole's tee moves up, given this round's pin band.

    Some venues move a drivable par 4 forward on the weekend. The archive shows
    how often, AND which pin bands travel with each tee -- so the published pin
    is itself evidence about the tee. Returns None if the hole has no tee split.
    """
    rows = archive.get(hole, {}).get("rows", [])
    fwd = [r for r in rows if r["y"] <= fwd_max]
    if not fwd or len(fwd) == len(rows):
        return None
    weekend_back = [r for r in rows if r["y"] > fwd_max and r["rnd"] in ("R3", "R4")]
    if not weekend_back:
        return None

    band = BAND.get(pin["band"], pin["band"])
    # Laplace-smoothed likelihood of seeing this band under each tee.
    p_fwd = (sum(1 for r in fwd if r["zone"].startswith(band)) + 1) / (len(fwd) + 2)
    p_back = (sum(1 for r in weekend_back if r["zone"].startswith(band)) + 1) / (len(weekend_back) + 2)

    weekend = [r for r in rows if r["rnd"] in ("R3", "R4")]
    years = len({r["y"] for r in weekend}) or 1
    n_fwd_weekend = len([r for r in weekend if r["y"] <= fwd_max])
    prior = max(n_fwd_weekend, 1) / max(len(weekend) - n_fwd_weekend, 1)

    odds = prior * (p_fwd / p_back)
    return {
        "hole": hole,
        "band": band,
        "prior": prior / (1 + prior),
        "lr": p_fwd / p_back,
        "posterior": odds / (1 + odds),
        "fwd": {
            "n": len(fwd),
            "pp": statistics.mean(r["pp"] for r in fwd),
            "b": statistics.mean(r["b"] for r in fwd),
            "bg": statistics.mean(r["bg"] for r in fwd),
        },
        "back": {
            "n": len(rows) - len(fwd),
            "pp": statistics.mean(r["pp"] for r in rows if r["y"] > fwd_max),
            "b": statistics.mean(r["b"] for r in rows if r["y"] > fwd_max),
            "bg": statistics.mean(r["bg"] for r in rows if r["y"] > fwd_max),
        },
        "years": years,
    }


# ------------------------------------------------------------- simulation

def simulate(pins, par, sims, delta=0.0, day_sd=0.16, bias=0.0,
             tee=None, tee_p=0.0, rng=None):
    """Round-score distribution from the page's own per-pin birdie/bogey rates.

    Each hole gets a latent normal thresholded at the projected birdie-or-better
    and bogey-or-worse rates. `delta` shifts a player off field average (negative
    = better), `bias` shifts the whole day, `day_sd` is shared setup/weather
    uncertainty. `tee`/`tee_p` optionally swaps one hole to its forward-tee rates.
    """
    rng = rng or random.Random(0)
    thresh = [
        (p["hole"], p["par"], _inv(p["b"] / 100), _inv(1 - p["bg"] / 100))
        for p in pins
    ]
    fwd_t = (_inv(tee["fwd"]["b"] / 100), _inv(1 - tee["fwd"]["bg"] / 100)) if tee else None

    scores = []
    for _ in range(sims):
        day = rng.gauss(0, day_sd) + bias
        forward = tee is not None and rng.random() < tee_p
        total = 0
        for hole, hole_par, t_b, t_bg in thresh:
            if forward and hole == tee["hole"]:
                t_b, t_bg = fwd_t
            z = rng.gauss(0, 1) + delta + day
            if z < t_b:
                eagle = 0.06 if hole_par == 5 else (0.05 if forward and hole == tee["hole"] else 0.004)
                total += -2 if rng.random() < eagle else -1
            elif z > t_bg:
                total += 2 if rng.random() < 0.16 else 1
        scores.append(par + total)
    return scores


def solve_delta(target, pins, par, **kw):
    """Find the skill shift that lands expected score on `target`."""
    lo, hi = -1.2, 0.8
    for _ in range(14):
        mid = (lo + hi) / 2
        if statistics.mean(simulate(pins, par, 9000, delta=mid, **kw)) > target:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


# ----------------------------------------------------------------- report

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page", help="path to a tournament index.html")
    ap.add_argument("--par", type=int, default=None, help="course par (default: sum of pin-sheet pars)")
    ap.add_argument("--sims", type=int, default=40000)
    ap.add_argument("--k", type=float, default=6.0, help="shrinkage weight toward band/hole")
    ap.add_argument("--tee-hole", type=int, default=None,
                    help="hole to test for a weekend tee move (e.g. 16 at TPC Twin Cities)")
    ap.add_argument("--lines", default="67.5,68.5,69.5,70.5",
                    help="round-score lines to price")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args(argv)

    doc = open(args.page, encoding="utf-8").read()
    archive = parse_archive(doc)
    pins = parse_pin_sheet(doc)

    if not archive:
        sys.exit("no pin-zone archive found on this page (no 'pcard' hole cards)")
    if not pins:
        sys.exit("no pin sheet found on this page (no 'pintbl' table)")

    per_hole = Counter(len(v["rows"]) for v in archive.values())
    par = args.par or sum(p["par"] for p in pins)
    spread = ", ".join(f"{n} placements x {holes} holes" for n, holes in sorted(per_hole.items()))
    print(f"page   : {args.page}")
    print(f"archive: {spread}")
    print(f"pins   : {len(pins)} on the sheet · par {par}")
    # 4 placements/hole is one edition; 24 is six. The on-page caveat text is
    # not reliable about which -- see notes/known-data-issues.md.
    if per_hole and max(per_hole) >= 8:
        editions = max(per_hole) // 4
        print(f"         -> ~{editions} editions of history "
              f"(a one-year page carries 4/hole; check the page's caveat matches)")
    print()

    rows = relative_difficulty(pins, archive, k=args.k)

    print("RELATIVE PIN DIFFICULTY (pin vs a typical placement on that same hole)")
    print(f"{'H':>3} {'par':>4} {'zone':>16} {'depth':>6} {'edge':>5} "
          f"{'est':>7} {'hole':>7} {'delta':>7}  basis")
    for r in sorted(rows, key=lambda x: x["hole"]):
        print(f"{r['hole']:>3} {r['par']:>4} {r['zone']:>16} {r['depth_pct']:>5.0f}% "
              f"{r['paces']:>4}p {r['est']:>+7.3f} {r['hole_mu']:>+7.3f} {r['delta']:>+7.3f}  {r['basis']}")

    tough = [r for r in rows if r["delta"] > 0.02]
    easy = [r for r in rows if r["delta"] < -0.02]
    flat = [r for r in rows if abs(r["delta"]) <= 0.02]
    net = sum(r["delta"] for r in rows)
    print(f"\n  tougher ({len(tough):>2}): " + ", ".join(f"#{r['hole']} {r['delta']:+.2f}"
          for r in sorted(tough, key=lambda x: -x["delta"])))
    print(f"  easier  ({len(easy):>2}): " + ", ".join(f"#{r['hole']} {r['delta']:+.2f}"
          for r in sorted(easy, key=lambda x: x["delta"])))
    print(f"  neutral ({len(flat):>2}): " + ", ".join(f"#{r['hole']}" for r in flat))
    print(f"  NET: {net:+.2f} strokes vs an average pin set "
          f"({'tougher' if net > 0 else 'easier'}; under ~0.25 is noise)")

    tucked = [r for r in rows if r["paces"] <= 4]
    deep = [r for r in rows if r["depth_pct"] >= 80]
    bands = Counter(BAND.get(p["band"], p["band"]) for p in pins)
    print(f"\n  bands: " + " / ".join(f"{v} {k}" for k, v in bands.most_common()))
    print(f"  tucked within 4 paces of an edge ({len(tucked)}): "
          + ", ".join(f"#{r['hole']}" for r in tucked))
    print(f"  deepest fifth of the green ({len(deep)}): "
          + ", ".join(f"#{r['hole']}" for r in deep))

    sat_b = sum(p["b"] for p in pins) / 100
    hist_b = sum(r["hole_b"] for r in rows) / 100
    sat_bg = sum(p["bg"] for p in pins) / 100
    hist_bg = sum(r["hole_bg"] for r in rows) / 100
    print(f"\n  page projects {sat_b:.2f} birdies/rd vs {hist_b:.2f} historical on the same holes "
          f"({sat_b - hist_b:+.2f})")
    print(f"  page projects {sat_bg:.2f} bogey+/rd  vs {hist_bg:.2f} historical "
          f"({sat_bg - hist_bg:+.2f})")
    if sat_b - hist_b < -0.2:
        print("  NOTE: page is projecting fewer birdies than history on these holes. If the")
        print("        weather read is benign, something is pulling the projection down --")
        print("        check tee yardages before trusting it (see --tee-hole).")

    tee = tee_move_posterior(archive, args.tee_hole, next(
        (p for p in pins if p["hole"] == args.tee_hole), {"band": "middle"})) if args.tee_hole else None
    if args.tee_hole and not tee:
        print(f"\n  hole {args.tee_hole}: no forward/back tee split in the archive")
    if tee:
        print(f"\nTEE-MOVE CHECK · hole {tee['hole']}")
        print(f"  forward tee: n={tee['fwd']['n']:>2}  {tee['fwd']['pp']:+.3f} to par, "
              f"{tee['fwd']['b']:.0f}% birdie, {tee['fwd']['bg']:.0f}% bogey+")
        print(f"  back tee   : n={tee['back']['n']:>2}  {tee['back']['pp']:+.3f} to par, "
              f"{tee['back']['b']:.0f}% birdie, {tee['back']['bg']:.0f}% bogey+")
        print(f"  prior P(forward) from weekend history : {tee['prior']:.0%}")
        print(f"  this round's pin band is '{tee['band']}' -> likelihood ratio {tee['lr']:.3f}")
        print(f"  POSTERIOR P(forward tee)             : {tee['posterior']:.0%}")
        print("  (the published pin band is evidence about the tee -- a band that only ever")
        print("   appears with one tee should move your prior a long way)")

    lines = [float(x) for x in args.lines.split(",")]
    for label, kw in (
        ("as published", {}),
        (f"+ P(tee move)={tee['posterior']:.0%} on #{tee['hole']}" if tee else None,
         {"tee": tee, "tee_p": tee["posterior"]} if tee else None),
    ):
        if label is None:
            continue
        rng = random.Random(args.seed)
        field = statistics.mean(simulate(pins, par, args.sims, rng=rng, **kw))
        print(f"\nROUND-SCORE DISTRIBUTION · {label} · field avg {field:.2f} "
              f"({field - par:+.2f} to par)")
        print(f"{'edge vs field':>16} {'E[score]':>9} | "
              + " ".join(f"U{l:>5.1f}" for l in lines))
        for edge in (0.0, 0.5, 1.1, 1.5):
            d = solve_delta(field - edge, pins, par, **kw)
            rng = random.Random(args.seed + 1)
            s = simulate(pins, par, args.sims, delta=d, rng=rng, **kw)
            n = len(s)
            print(f"{-edge:>+16.1f} {statistics.mean(s):>9.2f} | "
                  + " ".join(f"{sum(1 for x in s if x < l) / n * 100:>5.1f}%" for l in lines))
        print("  break-even on a -120 two-way price is 54.5%; -110 is 52.4%")

    return 0


if __name__ == "__main__":
    sys.exit(main())
