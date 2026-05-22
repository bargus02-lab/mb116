# Mill Bakery — Marketing Skill (User Guide)

This is a skill that lives in this repo and lets Claude generate Instagram posts for Mill Bakery on demand. The point: keep a steady cadence of on-brand posts going without taking new photos every week.

## How to invoke

In a new Claude Code session in this repo, say one of:

- "Generate this week's posts"
- "Make 5 new Instagram posts about [topic]"
- "Use the mill-bakery-marketing skill to draft week 3"
- "Replace post 04 with a hours-card showing Saturday hours"

Claude will:
1. Read `brand-guide.md`, `content-pillars.md`, and the existing calendar files
2. Draft a JSON calendar for the requested week if it doesn't exist
3. Run `post-generator.py` to render 1080×1350 PNG mockups
4. Write captions + hashtags to `output/week-N/captions.md`

## Where to find the output

```
.claude/skills/mill-bakery-marketing/
├── calendar/
│   └── week-N.json          ← Post definitions (Claude writes these)
└── output/
    └── week-N/
        ├── post-01-*.png    ← Ready-to-upload Instagram posts
        ├── post-02-*.png
        ├── ...
        └── captions.md      ← Caption + hashtags for each post
```

## Your workflow

1. Tell Claude what you want (week of content, specific posts, etc.)
2. Open the `output/week-N/` folder in Finder
3. Open `captions.md` alongside, copy each caption
4. Open Instagram on your phone, upload each PNG, paste the matching caption
5. Once a week is fully posted, delete that `output/week-N/` folder (the PNGs aren't tracked in git)

## Generating new photos with nano banana (Gemini 2.5 Flash Image)

When you want fresh imagery without setting up a photo shoot:

1. Open `nano-banana-prompts.md` in this folder
2. Pick a prompt that matches what you want (interior, pan dulce, burrito, etc.)
3. Paste it into the **Gemini app** (gemini.google.com or the iOS/Android app)
4. Save the best result to `assets/gallery/` with a descriptive filename
5. Ask Claude to "regenerate post-04 using my new pan-dulce photo"

## Updating templates / brand

- **Brand colors / voice changed?** → edit `brand-guide.md`
- **New post format you want repeatedly?** → ask Claude to add a new template to `post-generator.py`
- **Want more posts per week?** → edit `content-pillars.md` cadence section, then ask Claude

## Running the generator manually (optional)

If you ever want to run it yourself without Claude:

```bash
# From repo root:
python3 -m venv /tmp/mb-pil && /tmp/mb-pil/bin/pip install Pillow

/tmp/mb-pil/bin/python .claude/skills/mill-bakery-marketing/post-generator.py \
    .claude/skills/mill-bakery-marketing/calendar/week-1.json \
    .claude/skills/mill-bakery-marketing/output/week-1/
```

Requires Python 3 + Pillow. Uses macOS system fonts (Georgia, Helvetica, Menlo) — no font installation needed.
