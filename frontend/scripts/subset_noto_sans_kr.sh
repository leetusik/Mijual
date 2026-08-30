#!/usr/bin/env bash
# Subset Noto Sans KR Variable for 주주의관제탑, replacing the 2,057,688-byte Pretendard Variable
# that R1 vendored. Adopted from ~/projects/personal/changple_web/scripts/subset_noto_sans_kr.sh at
# the operator's instruction ("research changple_web's case for the korean font. use same with it"),
# with ONE deliberate adaptation — the Hangul coverage below.
#
# Source : Noto Sans KR variable TTF from google/fonts (OFL-1.1), pinned to a commit SHA for
#          reproducibility. Downloaded to a gitignored cache on first run (dev-only; the committed
#          subset woff2 is what ships). Same pin changple_web uses.
# Output : app/fonts/NotoSansKR.subset.woff2  (consumed by app/fonts.ts via next/font/local)
#
# Requirements (dev-only, never a runtime dep): pyftsubset (fonttools) + brotli + curl.
#   On this machine: /opt/homebrew/bin/pyftsubset, whose interpreter already has brotli.
#
# ── THE ADAPTATION, AND THE NUMBERS BEHIND IT ────────────────────────────────────────────────────
# changple_web subsets to *rendered* glyphs only (98,076 B) and lets dynamic database copy fall back
# to the OS face. Mijual cannot do that: it renders **DART company names** on the board, on every
# event page and throughout /ask, plus agent answers and quoted filing text — all dynamic. A
# rendered-glyph subset would put half of what the reader actually looks at in a different typeface
# from the UI around it.
#
# Measured on this repo and this corpus (P10.S7, 2026-08-31), same source TTF and same ranges:
#
#   (a) auto-extracted app glyphs alone (509 chars)   ->    94,604 B   — fails: dynamic Korean falls back
#   (b) + KS X 1001 wansung set (2,350 syllables)     ->   291,072 B   — ADOPTED
#   (c) + the full 11,172-syllable Hangul block       -> 1,022,828 B   — covers everything by construction
#
#   Today's Pretendard Variable, for scale: 2,057,688 B. So (b) is a 7.1x reduction and (c) a 2.0x one.
#
# Why (b) is the smallest that works, measured rather than assumed: across **every** Korean string
# stored in the local corpus — 654 distinct syllables spanning 614 company names, agent answers,
# extraction summaries and quoted DART filing text — KS X 1001 misses exactly **one**: 쳥, and that
# one is a typo inside a filing (「쳥약」 for 「청약」). All 360 company-name syllables are covered.
# A repo-wide sweep of 1,933 files finds no other real miss. The residue therefore degrades one
# syllable at a time, and — because of the jamo rule below — degrades *composed*.
#
# To take option (c) instead, set HANGUL_COVERAGE=full. Nothing else changes.
# ─────────────────────────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# Pinned google/fonts commit for NotoSansKR[wght].ttf. Bump deliberately to upgrade the typeface.
SRC_SHA="4efc2774c63917927efe769ca845def6bd6debae"
SRC_URL="https://raw.githubusercontent.com/google/fonts/${SRC_SHA}/ofl/notosanskr/NotoSansKR%5Bwght%5D.ttf"
LICENSE_URL="https://raw.githubusercontent.com/google/fonts/${SRC_SHA}/ofl/notosanskr/OFL.txt"
CACHE_DIR="$ROOT/node_modules/.cache/mijual-fonts"
SRC="$CACHE_DIR/NotoSansKR-wght-${SRC_SHA}.ttf"
OUT_DIR="$ROOT/app/fonts"
OUT="$OUT_DIR/NotoSansKR.subset.woff2"
LICENSE_OUT="$OUT_DIR/NotoSansKR-OFL.txt"
CHARSET="$ROOT/scripts/korean-charset.txt"
EXTRA="$CACHE_DIR/hangul-coverage.txt"

# ksx1001 (adopted) | full — see the header.
HANGUL_COVERAGE="${HANGUL_COVERAGE:-ksx1001}"

mkdir -p "$CACHE_DIR" "$OUT_DIR"

if [ ! -f "$SRC" ]; then
  echo "downloading Noto Sans KR variable TTF (google/fonts @ ${SRC_SHA:0:10})..."
  curl -fsSL -o "$SRC" "$SRC_URL"
fi
if [ ! -f "$LICENSE_OUT" ]; then
  curl -fsSL -o "$LICENSE_OUT" "$LICENSE_URL"
fi

# Always regenerate the charset from the rendered source first, so it can never go stale and drop
# syllables the app shows (changple_web P5: a stale charset dropped 박/닙/함/께/면 → the browser
# decomposed those NFC syllables and rendered them split apart, 자모 분리).
node "$ROOT/scripts/gen-korean-charset.mjs"

# The Hangul coverage the adaptation above buys. Derived, never a checked-in data file: the KS X 1001
# wansung area is exactly the syllables whose EUC-KR encoding falls in lead 0xB0-0xC8 / trail
# 0xA1-0xFE, so python reproduces the 2,350 deterministically with no table to maintain.
python3 - "$HANGUL_COVERAGE" "$EXTRA" <<'PY'
import sys
mode, out = sys.argv[1], sys.argv[2]
if mode == "full":
    chars = [chr(c) for c in range(0xAC00, 0xD7A4)]
elif mode == "ksx1001":
    chars = []
    for c in range(0xAC00, 0xD7A4):
        b = chr(c).encode("euc_kr")
        if len(b) == 2 and 0xB0 <= b[0] <= 0xC8 and 0xA1 <= b[1] <= 0xFE:
            chars.append(chr(c))
else:
    sys.exit(f"unknown HANGUL_COVERAGE: {mode!r} (expected ksx1001 or full)")
open(out, "w", encoding="utf8").write("".join(chars))
print(f"hangul coverage '{mode}': {len(chars):,} syllables")
PY

# No --no-hinting / --desubroutinize: glyf (not CFF) + unhinted source, so both are inert. Keep the
# full wght 100-900 axis (app/fonts.ts declares weight "100 900") and do NOT instance it — measured
# on this font, narrowing the axis to 400-700 changes nothing (1,053,156 B vs 1,022,828 B; it is
# very slightly *larger*, because the instancer bakes deltas). The axis is free; the glyphs are not.
#
# --unicodes deliberately OMITS the conjoining-jamo block U+1100-11FF: the app text is NFC, and
# including those jamo lets the browser decompose-and-split any missing syllable. Without them, an
# unknown/dynamic syllable falls back to the system font *composed* instead. That is what makes the
# measured residue above acceptable rather than ugly.
pyftsubset "$SRC" \
  --output-file="$OUT" \
  --flavor=woff2 \
  --text-file="$CHARSET" \
  --text-file="$EXTRA" \
  --unicodes="U+0020-007E,U+00A0-00FF,U+3130-318F,U+3000-303F,U+2010-2027,U+2030-205E,U+20A9,U+20AC" \
  --layout-features="kern,liga,calt,case" \
  --name-IDs=""

SIZE=$(wc -c < "$OUT")
echo "wrote $OUT"
awk -v s="$SIZE" 'BEGIN { printf "size: %d bytes (%.1f KB)\n", s, s / 1024 }'
