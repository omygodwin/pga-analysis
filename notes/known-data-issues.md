# Known data issues

Verified defects in the published pages, with the strings to find them. Each was
confirmed against the file, not inferred. Last checked 2026-10-21.

---

## 1. 3M Open pin-zone archive is mislabelled as one year (open)

**File:** `3m-open-2026/index.html`
**Find:** `reads are built from 2025's 4 placements per hole` and `4 pins · 2025`

The `tab-pins` section tells the reader its pin-zone reads come from a single
edition:

> One-year note: reads are built from 2025's 4 placements per hole, so they're
> early — they sharpen as more years are played here.

and every one of the 18 hole cards is headed `4 pins · 2025`. Both are wrong.
The page actually carries **24 placements per hole spanning six editions**:

- Each hole card has 24 `R1`–`R4` rows, six per round label — not four.
- Hole 1's six `R1` rows carry six different yardages (407, 391, 402, 395, 421,
  407), which cannot happen within one tournament.
- The "toughest pins" table cites `n=845` shots for hole 2 front-left. That zone
  appears in 7 of the 24 archived placements; 845 shots over 7 placements is
  ~121 players each, consistent with a ~145-man field across six editions and
  impossible within one.

**Why it matters:** the caveat understates the data. Anyone reading it discounts
a six-year sample as a one-year sample, which is the opposite of the correction
needed. Zone reads here are more trustworthy than the page claims.

**Cause:** template text. `rbc-canadian-open-2026/index.html` carries the
identical sentence and there it is *correct* — that page genuinely has 4
placements per hole. The line was copied forward without being re-checked.

**Fix:** update the 3M caveat to say six editions / 24 placements per hole, and
change the card headers from `4 pins · 2025` to the real span. Then audit any
future page that reuses the sentence — `tools/pin_difficulty.py` reports the
real archive depth on its second line (`archive: 24 placements x 18 holes`,
plus an estimated edition count), which is the quick check.

---

## 2. 3M Saturday pin sheet carries an unverifiable provenance claim (open)

**File:** `3m-open-2026/index.html`
**Find:** `Sheet stamped Friday 8:55`

The `r3-pins` section (Saturday's pin sheet) closes with:

> Sheet stamped Friday 8:55 AM. Green depths cross-check exactly against the R2
> sheet, which is the read-accuracy check on a vector PDF whose text is outlined
> rather than selectable.

Two problems:

1. **The stated check cannot verify what it claims.** Green total depth is a
   property of the green, identical on every round's sheet. Matching depths
   against the R2 sheet confirms the OCR read the numbers correctly; it says
   nothing about *which round's* hole locations were read. The one thing that
   would distinguish Saturday's sheet from Friday's — the pin coordinates — is
   not what was cross-checked.
2. **A Friday-morning timestamp on a Saturday sheet is unexplained.** It may be
   legitimate (tours sometimes publish multi-day sheets), but nothing on the
   page reconciles it.

There is weak corroborating evidence that the sheet may be the wrong round:
hole 16's pin is in the **front** band, and in the six-edition archive the front
band appears with the *back* tee, while all 9 forward-tee weekend placements are
**mid** band — yet the forward tee is used on 9 of 12 archived weekend rounds.
See `notes/2026-07-3m-open-r3-pins-and-round-score-unders.md` for the full read.
This is suggestive, not conclusive.

**Fix:** re-verify the sheet against the source PDF's round label, and replace
the depth cross-check with one that actually discriminates rounds (compare pin
coordinates against the R2 sheet and confirm they differ).

---

## 3. The Toll wave projection was inverted for 3M R2 (open — methodology)

**File:** `3m-open-2026/index.html`
**Find:** `the morning half into the teeth of it` and `the good half`

The R2 preview projected the morning wave as the harder half (Toll 14.2 AM vs
13.2 PM). The recap records the opposite outcome: AM averaged **−1.48** and PM
**−0.72**, with 26 of the 43 rounds of −3-or-better coming before noon. The
weather ledger shows the PM actually got both more wind (13/19 vs 10/18) and
more heat (79° vs 71°).

So the forecast inputs, not the Toll formula, pointed the wrong way — but the
published wave edge was wrong by ~0.76 strokes in direction and magnitude.

**Why it matters:** the R3 preview then leaned on the same machinery to claim a
3.2-Toll-unit edge to the late wave ("the leaders go out last, into the calmest
hours"). That claim inherits the error mode and should not be treated as
established. Any bet or read that depends on a wave split needs the forecast
re-checked at tee time, not the projection trusted.

**Related:** the model also runs conservative on absolute scoring. It projected
R2 at **−0.29**; the round played **−1.10**. R1 played −0.93. The R3 projection
of −0.67 was therefore likely understated.
