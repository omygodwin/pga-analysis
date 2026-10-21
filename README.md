# StimpDeck — PGA Analysis

Static, self-contained tournament previews and recaps for PGA Tour events:
strokes-gained leaderboards, course history, pin-zone reads, and weather-aware
scoring projections. Published as a GitHub Pages site (`.nojekyll`, no build
step, no dependencies).

## Layout

```
index.html                  hub: hand-maintained cards linking each tournament
docs.json                   tournament metadata index (see note below)
manifest.json               PWA manifest — app name "StimpDeck"
logo-badge-*.png            PWA icons
apple-touch-icon.png
<event>-<year>/index.html   one self-contained page per tournament
<event>-<year>/babe.png     section art for "Babe's Babes"
tools/                      analysis scripts that read the built pages
notes/                      findings and known issues that outlive a session
```

Current events: `memorial-2026`, `rbc-canadian-open-2026`,
`isco-championship-2026`, `3m-open-2026`, `rocket-classic-2026`.

## Conventions

**One file per tournament.** Each `<event>-<year>/index.html` is a single
standalone document — CSS, JS, data and base64 images all inline. They run
0.8–1.2 MB. There is no bundler, no package manifest and no CI; editing the
page is editing the deliverable. Grep by class name or section id to navigate
rather than reading top to bottom.

**Tabs.** Pages accrete a tab per round as the week goes. Panel ids are stable:

| id | contents |
|---|---|
| `tab-preview` | pre-tournament: course, archetype, comps, field, fit |
| `tab-holes` | hole-by-hole cards with wind exposure |
| `tab-pins` | pin-zone tendencies + per-hole green cards |
| `tab-r2` | R1 recap / R2 preview |
| `tab-r3` | R2 recap / R3 preview |
| `tab-final` | 72-hole wrap (Memorial only so far) |

Within a tab, sections are `<section class="csec" id="...">` with ids namespaced
by round (`r3-board`, `r3-pins`, `r3-preview`, …). Tables are `.rs-tbl`; the pin
sheet is `.pintbl`; per-hole green cards are `.pcard` containing a `.pztable`.

**`docs.json`** carries event/course/location/dates/path/blurb per tournament.
No page in this repo fetches it — the hub hardcodes its links — so it appears to
exist for an external consumer (likely the app the commit history calls "the
app"). It is maintained by hand and must be updated alongside the hub when an
event is added. Verify who reads it before relying on or restructuring it.

## Glossary

Terms the pages use without defining in every section.

- **Toll** — hole-aware conditions index: wind decomposed against each hole's
  compass bearing, plus temperature and moisture, averaged over a player's
  projected play window. Canonical bands at 9.5 and 17.25 (calm / moderate /
  hostile). TPC Twin Cities' six-year average play-window Toll is 13.7.
- **Field-adjusted SG** — each strokes-gained category re-centred on that
  round's field mean versus a typical Tour round, so a soft course that has the
  whole field gaining raw strokes does not inflate everyone. This is the `ADJ`
  default.
- **BS** — ball-striking, i.e. OTT + APP. The sticky part of a round; ARG and
  PUTT regress hard between rounds.
- **Give / gain** — volatile putting + short-game SG, sign-flipped into an
  expectation. Negative means the player rode a hot short game and carries
  regression risk; positive means they left strokes on the greens.
- **Pin zone** — a green divided into depth band (front / mid / back) x side
  (left / right), scored by `±par`, birdie % and bogey-plus % across archived
  placements. `B−` is birdie-or-better, `Bg+` is bogey-or-worse.
- **Babe's Babes** — the worst-putting section: three-putts, burned edges, the
  short ones that got away.

## Tools

`tools/pin_difficulty.py` — scores a round's pin sheet against each hole's own
archived placements (tougher or easier *location*, as distinct from a hard
*hole*), then turns the per-pin rates into a round-score distribution and prices
round-score unders. Reads a built page directly; no dependencies.

```sh
python3 tools/pin_difficulty.py 3m-open-2026/index.html --tee-hole 16
```

## Before trusting a page's own numbers

The pages carry their own projections and caveats, and some of those caveats are
template text that did not get updated per event. `notes/known-data-issues.md`
lists what has been verified wrong, with the search strings to find it. Read it
before building on a page's pin-zone or weather-projection output.
