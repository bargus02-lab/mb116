# Mill Bakery — Brand Guide

Quick reference for posts. The site itself (`styles.css`) is the source of truth — match these tokens exactly.

## Palette

| Role | Hex | Where to use |
|------|-----|--------------|
| Cream (background) | `#f8f2e6` | Default post background |
| Cream deep | `#efe3cc` | Secondary bg, accent panels |
| Red (primary) | `#b6372e` | Headlines, accents, buttons |
| Red deep | `#8d241f` | Gradient companion, dark accents |
| Gold | `#e4ab24` | Wheat, accent lines, watermarks |
| Gold soft | `#f4d36d` | Highlight glow |
| Text | `#432b20` | Body text on cream |
| Muted | `#74584c` | Secondary text, eyebrows |

## Type

- **Display headlines**: Bree Serif at weight 900 with a 0.035em text-stroke (faux-bold, matches the wordmark on the site). For Pillow rendering use a system serif (Georgia / Times) at heavy weight since Bree Serif Bold doesn't exist as a TTF.
- **Body / labels**: Work Sans (system fallback: Helvetica / Arial).
- **Editorial labels**: DM Mono uppercase, tracked-out 0.18em (system fallback: Menlo / Courier New).

## Brand mark

- File: `assets/logo-windmill-mark-2026.png` (600x669, RGBA transparent)
- Always render at corner of post or as light watermark, never centered overpowering the message

## Voice

- **Tone**: warm, simple, local — a neighborhood bakery, not corporate
- **Capitalization**: normal grammar. Proper case, sentence-first capitalization, real punctuation. (We tried all-lowercase earlier; it felt stylized in a way that wasn't on-brand. Don't do that.)
- **POV**: first-person plural ("we", "our") or no subject ("Open daily 5 AM")
- **Length**: short. 1–3 sentences for captions. Headlines 2–6 words.
- **No corporate phrases**: avoid "delicious", "experience", "passionate", "artisanal", "curated"
- **Yes**: "fresh", "warm", "stop in", "from the case", "made this morning", "the usual"
- **Emojis**: max 1 per caption. Acceptable: 🍞 ☕ 🥐 🌅 ☀️. Don't use ❤️ or 🔥.
- **Hashtags**: see `hashtag-strategy.md` for the 2026 approach. Tiered mix.
  - Local: `#santaana`, `#santaanafood`, `#ocfoodie`, `#supportlocal`, `#downtownsantaana`
  - Topic: `#pandulce`, `#mexicanbakery`, `#breakfastburrito`, `#concha`, `#panaderia`

## Business facts (don't make these up — pull from `data/site-content.json`)

- Address: 116 W MacArthur Blvd, Santa Ana, CA 92707
- Phone: (714) 540-7278
- Hours: Daily 5 AM – 1 PM
- Instagram handle: `@millbakery.oc`
- Menu: see `data/site-content.json` for current items and prices

## Things to avoid

- **No stock-photo-feeling content** — Mill Bakery is a real neighborhood spot, not a brand video
- **No fabricated quotes/reviews** — if no real testimonial exists, skip that pillar this week
- **No price claims unless confirmed** — pull from JSON or ask user
- **No promises of new items** unless the user has told us they're launching
