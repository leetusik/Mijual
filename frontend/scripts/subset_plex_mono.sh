#!/usr/bin/env bash
# Subset IBM Plex Mono for 주주의관제탑, replacing the Google Fonts CDN stylesheet the R1 record
# reached for. Adopted from ~/projects/personal/changple_web/scripts/subset_plex_mono.sh.
#
# Why this font exists here: R1 makes mono **numeral-only** type — every figure, the account slot's
# abbreviated email, the ops chips — and `--font-mono` in foundations/tokens.css names it. Self-
# hosting it removes a third-party request from every page load; nothing about the design changes.
#
# Weights: 400, 500 **and 600** — the three the retired
# `https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600` asked for. changple_web
# ships two because its system uses two; taking only two here would silently drop a weight R1 signed,
# so the third is kept. No variable face exists for Plex Mono in google/fonts at this pin, so the set
# ships as three static subsets rather than one axis.
# Charset: Latin only — Korean lives in NotoSansKR.subset.woff2. `tnum`/`lnum` are kept because the
#          product's figures are tabular, `case` because some mono labels are uppercase.
# Output : app/fonts/IBMPlexMono-{Regular,Medium,SemiBold}.subset.woff2
#          (consumed by app/fonts.ts via next/font/local)
#
# Requirements (dev-only, never a runtime dep): pyftsubset (fonttools) + brotli + curl.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# Pinned google/fonts commit (same pin as subset_noto_sans_kr.sh). Bump deliberately to upgrade.
SRC_SHA="4efc2774c63917927efe769ca845def6bd6debae"
BASE_URL="https://raw.githubusercontent.com/google/fonts/${SRC_SHA}/ofl/ibmplexmono"
LICENSE_URL="${BASE_URL}/OFL.txt"
CACHE_DIR="$ROOT/node_modules/.cache/mijual-fonts"
OUT_DIR="$ROOT/app/fonts"
LICENSE_OUT="$OUT_DIR/IBMPlexMono-OFL.txt"

mkdir -p "$CACHE_DIR" "$OUT_DIR"

if [ ! -f "$LICENSE_OUT" ]; then
  curl -fsSL -o "$LICENSE_OUT" "$LICENSE_URL"
fi

TOTAL=0
for FACE in Regular Medium SemiBold; do
  SRC="$CACHE_DIR/IBMPlexMono-${FACE}-${SRC_SHA}.ttf"
  OUT="$OUT_DIR/IBMPlexMono-${FACE}.subset.woff2"
  if [ ! -f "$SRC" ]; then
    echo "downloading IBMPlexMono-${FACE}.ttf (google/fonts @ ${SRC_SHA:0:10})..."
    curl -fsSL -o "$SRC" "${BASE_URL}/IBMPlexMono-${FACE}.ttf"
  fi
  pyftsubset "$SRC" \
    --output-file="$OUT" \
    --flavor=woff2 \
    --unicodes="U+0020-007E,U+00A0-00FF,U+2010-2027,U+2030-205E,U+20A9,U+20AC" \
    --layout-features="kern,liga,calt,case,tnum,lnum,frac,ordn" \
    --name-IDs=""
  SIZE=$(wc -c < "$OUT")
  TOTAL=$((TOTAL + SIZE))
  echo "wrote $OUT"
  awk -v s="$SIZE" 'BEGIN { printf "size: %d bytes (%.1f KB)\n", s, s / 1024 }'
done

awk -v s="$TOTAL" 'BEGIN { printf "total: %d bytes (%.1f KB)\n", s, s / 1024 }'
