# 3M Open 2026 R3 — pin placements and leader round-score unders

**Question asked:** conditions look benign on the weather, so is betting the
leaders *under* their R3 round score a good idea? Specifically: how many of
Saturday's pins are in tougher or easier relative locations?

**Answer:** the pin sheet does not support the thesis — it is average, not easy
— and "the leaders" is the wrong group to buy. A narrow version of the bet
survives. Full reasoning below.

Written 2026-07-25 (3M Open R3, TPC Twin Cities, par 71). Reproducible with:

```sh
python3 tools/pin_difficulty.py 3m-open-2026/index.html --tee-hole 16
```

---

## 1. The pin read: a wash

Counting Saturday's sheet (`r3-pins`): **6 front / 5 middle / 7 back**, 4 in the
deepest fifth of the green (3, 7, 10, 17), 5 cut within four paces of an edge
(5, 6, 10, 13, 14). That matches the page's own summary.

But raw position is not difficulty. A back pin on 10 is routine; a mid pin on 9
is murder. The useful question is *pin versus a typical placement on that same
hole*, which isolates the part a setup actually controls. Scoring each flag
against its archived zone (shrinkage-weighted — some zones have n=1):

| | Holes | Net |
|---|---|---|
| **Tougher** than typical for that hole | 16 (+0.09), 7 (+0.06), 13 (+0.05), 2 (+0.04), 5 (+0.04) | +0.28 |
| **Easier** than typical | 4 (−0.05), 18 (−0.05), 3 (−0.05), 6 (−0.03), 14 (−0.03), 8 (−0.02) | −0.19 |
| **Neutral** (±0.02) | 1, 9, 10, 11, 12, 15, 17 | — |

**Net +0.09 strokes/round versus an average TPC Twin Cities pin set.** That is
noise. The setup is neither helping nor hurting a low-scoring thesis.

Two things worth knowing inside the wash:

- **Hole 9 (mid-left)** is the single hardest pin zone on the property — +0.27
  to par, 8% birdie, 29% bogey-plus — sitting on the hardest hole on the course
  (498-yard par 4, +0.29 historically). It is not a *relative* toughening
  (Δ +0.00; that is just hole 9) but it is a leader-killer.
- The tucked pins are mostly on holes that are easy anyway (5, 6, 14).
  Cheap-looking difficulty.

## 2. The page's own projections disagree with its pins

The model projects **3.72 birdies/round** off these pins against **4.11** for
the same holes historically — i.e. it projects Saturday *stingier* than average
despite a benign weather read. The gap concentrates in three holes: **16, 12,
18** — the drivable par 4 and the two reachable par 5s. Exactly the holes a
leader needs to beat a round-score line.

On hole 16 the model looks wrong, and the reason is the tee:

| Hole 16 tee | n | ±par | birdie | bogey+ |
|---|---|---|---|---|
| Forward (≤320y) | 9 | **−0.58** | 60% | 4% |
| Back (>320y) | 15 | +0.03 | 16% | 17% |

The forward tee is used on **9 of 12 archived weekend rounds**. The model
projects 17% birdies for Saturday — i.e. it is assuming the back tee. If the tee
moves up, the published field projection of −0.67 is understated by roughly half
a stroke on this hole alone.

**But the pin sheet argues against the tee move.** All 9 forward-tee placements
in the archive are **mid** band; the **front** band appears with the back tee.
Saturday's pin on 16 is front. Treating the pin band as evidence:

- Prior P(forward tee) from weekend history: 9/12 → **75%**
- Likelihood ratio from seeing a front pin: **0.152**
- **Posterior P(forward tee): 31%**

(The original hand-run used the page's prose claim of "5 of the last 6 years" as
the prior, giving 83% → posterior 43%. The archive-derived 75% → 31% is the
better number; both leave the conclusion intact.)

So the single biggest upside driver for an under is probably *not* coming.

## 3. Round-score distribution

Simulating off the page's own per-pin birdie/bogey rates (the simulation
reproduces the page's published −0.67 field projection to within 0.06, so it is
calibrated to their model):

| Scenario | Field avg |
|---|---|
| As published (#16 back tee) | 70.41 |
| + P(tee move) = 31% on #16 | 70.21 |
| + half the model's demonstrated R2 conservatism (−0.40) | ~69.8 |

That last row matters: the model projected R2 at −0.29 and it played −1.10. It
has run conservative all week (see `known-data-issues.md` #3).

Under probabilities for a leader ~1.1 strokes better than the weekend field:

| Line | P(under) | Break-even at −120 |
|---|---|---|
| Under 68.5 | 40–49% | 54.5% — no |
| Under 69.5 | **54–62%** | 54.5% — thin |
| Under 70.5 | 66–73% | juice will eat it |

Round-score distributions are right-skewed: blow-ups are more available than
equivalent blitzes. That works against unders and is in the simulation.

## 4. Verdict

Directionally defensible, but the version as described is a bad bet, for three
reasons.

**The pins don't support it.** The thesis was looking for confirmation that the
setup was soft. It is average. The benign-weather read has to carry the bet
alone — and that read is public and already in the price.

**"The leaders" is the wrong bloc.** Backing out DataGolf baselines from the
page's own vs-baseline table (`r3-fit`: R2 field-adjusted SG total minus Δ-vs-base):

| Player | 36h | implied baseline SG/rd |
|---|---|---|
| Scottie Scheffler | −7 | **+2.78** |
| Brian Harman | −9 | +0.47 |
| Michael Kim | −14 | +0.35 |
| Zac Blair | −9 | +0.17 |
| Kevin Yu | −7 | −0.19 |
| Chandler Phillips | −11 | **−0.61** |
| Troy Merritt | −10 | **−1.16** |

Most of the top 12 are *below* the weekend field's talent level, riding form.
For that tier an under at 69.5 prices at 47–54% — dead money. Kim and Harman are
the only leaders whose unders clear the vig, and only at 69.5 or higher.
Scheffler is the genuinely mispriced under on talent, but at −7 he is seven back
and not a "leader", so the book will already have him low.

**The wave edge is unproven.** The "leaders go out last into the calmest hours"
claim rests on the Toll wave model, which got Friday exactly backwards —
projected AM harder, AM played 0.76 strokes easier. Same machinery, 24 hours
later.

**One more flag:** Kim shot 59 on Friday with +6.48 SG putting, and the page's
own variance table has him at **−6.8 give/gain**, the largest regression flag in
the field. The round after a 59 is historically a poor spot to buy low scoring.

**If taking the trade:** under 69.5 or higher, Kim or Harman only, small. Skip
Phillips, Grillo, Kohles, Merritt, Koivun, Blair entirely.

## 5. Method notes worth reusing

- Score pins **relative to their own hole**, not absolutely. The pages publish
  absolute projections, which conflate a hard hole with a hard pin and will
  mislead anyone asking a setup question.
- A published pin band is **evidence about tee position** at venues that move a
  tee. Running that as a likelihood ratio against the archive changed the key
  input here from 83% to 31%.
- Check a page's projected birdie rates against its own historical rates for the
  same holes. A benign weather read plus a below-history birdie projection means
  something unmodelled is in there — here, a tee assumption.
- Back out player baselines from the vs-season-baseline table rather than
  trusting leaderboard position. It separates talent from form, which is the
  whole bet.
