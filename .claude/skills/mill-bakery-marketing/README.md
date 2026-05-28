# Mill Bakery — Marketing Skill (User Guide)

This is a skill that lives in this repo and lets Claude generate Instagram posts for Mill Bakery on demand. The point: keep a steady cadence of on-brand posts going without taking new photos every week.

## How to invoke

In a new Claude Code session in this repo, say one of:

- "Generate some new posts"
- "Make 5 new Instagram posts about [topic]"
- "Add a few posts to the calendar"
- "Replace post 04 with a hours-card showing Saturday hours"

Claude will:
1. Read `brand-guide.md`, `content-pillars.md`, and the existing `calendar/posts.json`
2. Append the new posts to `calendar/posts.json` (one growing list — no weekly split)
3. Run `post-generator.py` to render every post as a 1080×1350 PNG mockup
4. Write captions + hashtags to `output/posts/captions.md`

## Where to find the output

```
.claude/skills/mill-bakery-marketing/
├── calendar/
│   └── posts.json           ← Every post definition (one growing list)
└── output/
    └── posts/
        ├── post-01-*.png    ← Ready-to-upload Instagram posts
        ├── post-02-*.png
        ├── ...
        ├── captions.md      ← Caption + hashtags for each post
        └── preview.html     ← Visual grid of all posts
```

## Your workflow

1. Tell Claude what you want (new posts, specific edits, etc.)
2. Open `output/posts/preview.html` in a browser to scan everything — or open the `output/posts/` folder in Finder
3. Open `captions.md` alongside, copy each caption
4. Open Instagram on your phone, upload each PNG, paste the matching caption
5. The PNGs aren't tracked in git and regenerate any time from `posts.json`, so you can delete the `output/posts/` folder whenever

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
- **Want a different cadence?** → edit `content-pillars.md`, then ask Claude

## Running the generator manually (optional)

If you ever want to run it yourself without Claude:

```bash
# From repo root:
python3 -m venv /tmp/mb-pil && /tmp/mb-pil/bin/pip install Pillow

/tmp/mb-pil/bin/python .claude/skills/mill-bakery-marketing/post-generator.py \
    .claude/skills/mill-bakery-marketing/calendar/posts.json \
    .claude/skills/mill-bakery-marketing/output/posts/
```

Requires Python 3 + Pillow. Uses macOS system fonts (Georgia, Helvetica, Menlo) — no font installation needed.
