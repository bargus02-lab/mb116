---
name: mill-bakery-marketing
description: Generate Instagram post mockups, captions, and content calendars for Mill Bakery (Santa Ana). Use when the user asks for social media posts, weekly content, marketing ideas, captions, or new bakery photos. Posts land in .claude/skills/mill-bakery-marketing/output/ as 1080x1350 PNGs ready to upload to Instagram.
---

# Mill Bakery — Marketing Skill

The bakery doesn't have many photos. This skill is designed to keep a steady cadence of Instagram posts going **without** depending on new photography, by leaning on three sources:

1. **Typography-driven posts** — chunky Bree Serif headlines on brand-color backgrounds
2. **Repurposed gallery photos** — the existing 8 images in `assets/gallery/`, cropped and overlaid different ways for variety
3. **Nano banana (Gemini 2.5 Flash Image) prompts** — written for the user to paste into Gemini themselves to generate new bakery imagery on demand

## Files in this skill

- `brand-guide.md` — palette, fonts, voice
- `content-pillars.md` — the 6 categories every post falls into
- `nano-banana-prompts.md` — image-generation prompts to paste into Gemini for fresh visuals
- `post-generator.py` — Pillow-based Python script that renders Instagram posts from a list of post definitions
- `calendar/week-1.md` etc. — content calendars; each row is one post
- `output/` — generated PNG mockups (do not commit large batches; the user uploads then can delete)

## Workflow (how to use this skill)

When the user says "generate this week's posts" or similar:

1. Read `brand-guide.md` and `content-pillars.md` so the work stays on-brand
2. Read the most recent `calendar/week-N.md` to see what's been planned
3. If no calendar exists for the requested week, draft one first using a mix from each content pillar (target 5–7 posts/week)
4. Run `post-generator.py` to render the posts as 1080x1350 PNGs into `output/week-N/`
5. List the files for the user; remind them to upload via Instagram app, then delete the output folder once posted
6. For posts that need a new photo, write the **nano banana prompt** in the calendar entry and tell the user to generate it via Gemini and drop the result in `assets/gallery/` — then rerun the generator

## Constraints

- **Do not invent prices, hours, or menu items.** Pull everything from `data/site-content.json` in this repo. If anything is missing or stale, ask the user.
- **Do not fabricate testimonials or reviews.**
- The Instagram handle is `@millbakery.oc` — always use this exact handle in captions.
- Captions should be short and warm, 1–3 sentences, lowercase informal tone. Use emojis sparingly (max 1 per caption).
- Always include a windmill mark watermark (light, bottom corner) so reposts/screenshots are traceable.
- 1080x1350 (4:5 portrait) is the default size — gets maximum feed real estate.

## Outputs

- PNG files named `output/week-NN/post-NN-{slug}.png` plus a `captions.md` with the caption + hashtags for each post
- All assets ready for the user to upload through the Instagram app manually

## How to add a new content pillar / template

Edit `content-pillars.md`, add an entry to `post-generator.py` as a new template type, and document the prompt requirements in the calendar.
