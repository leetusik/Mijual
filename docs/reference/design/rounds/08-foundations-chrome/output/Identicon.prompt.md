# Identicon — 계정 아이디콘 (R8)

The account slot's generated mark. Introduced in R8 to replace the 축약 이메일 as the slot's
identity: the reader sees their **full email** plus a mark that is theirs and nobody else's.

## Algorithm (implement exactly — the mark must match across web and any later surface)

1. `key = seed.trim().toLowerCase()`
2. `h = fnv1a32(key)` → `hue = [--r1, --r2, --r3, --live][h % 4]`
3. `bits = fnv1a32(key + ':cells')`
4. For each row `r` in 0..4, take bits `r*3 + 0..2` as the left half; row = `[b0, b1, b2, b1, b0]`
   (column 2 is the mirror axis). A set bit paints the cell in `hue`; an unset cell stays transparent
   over the frame's `rgba(255,255,255,.06)`.

`fnv1a32`: `h = 0x811c9dc5`; per char `h ^= code; h = (h * 0x01000193) >>> 0` (use `Math.imul`).

## Rules

- **Square cells, square frame** (`--radius-0`), 1px `--border-soft`. No radii, no gradients, no shadow.
- Only the four data hues — never `--alert` (red is reserved for 소멸/기한) and never `--brand`.
- Sizes: **20px** (nav frame) · **28px** (mobile sheet) · **40px** (account surface). Cell = size/5, so
  every size lands on whole pixels.
- It is decoration for recognition, not data: `role="img"` with a label, and it never replaces the email.
- Seed source (hashed email vs stored per-account seed) is an apply-time data decision — the visual is
  identical either way, so nothing here depends on it.
