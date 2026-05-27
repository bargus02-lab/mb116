# Nano Banana (Gemini 2.5 Flash Image) Prompts

The user generates these images via the Gemini app (free), saves them to `assets/gallery/`, and re-runs the post generator.

**Style suffix to append to every prompt** (keeps results brand-consistent):

```
Warm natural morning light, slight film grain, cream and dark red and gold color palette, neighborhood bakery atmosphere in Southern California, shallow depth of field, no people, no text, no logos, no brand names visible. Square 1080x1080 or vertical 1080x1350. Photorealistic, not illustrated.
```

---

## Bakery interior

> A small Mexican neighborhood bakery counter at 5:30 AM, soft morning light coming through a window, pastry trays visible on the back wall, wooden counter top, no people. **+ style suffix**

> Interior of a Mexican panadería at sunrise, glass pastry case full of conchas and pan dulce, warm cream walls, no people, golden hour light. **+ style suffix**

## Pan dulce / pastries

> Close-up of conchas with red, yellow, and white sugar topping arranged on a wooden tray, soft natural light, no plate. **+ style suffix**

> Macro photograph of a single fresh concha, steam rising slightly, on a brown paper bakery liner, slightly out of focus background. **+ style suffix**

> A baker's hand placing a tray of fresh pan dulce on a cream colored counter, no face visible, just hand and tray, morning light. **+ style suffix**

## Burritos

> Breakfast burrito wrapped half in foil, half in white parchment, salsa cup beside it, on a brown paper bag, morning light from a side window. **+ style suffix**

> Hand holding a foil-wrapped breakfast burrito above a cream wood counter, no face, motion blur, like someone is picking it up to go. **+ style suffix**

## Coffee

> Two cups of black coffee in white ceramic mugs on a cream counter, steam rising, concha on a small plate beside one of them, morning sunlight angled across. **+ style suffix**

> Overhead shot of a coffee cup with crema on top, a concha torn in half on a brown napkin next to it. **+ style suffix**

## Storefront / neighborhood

> Quiet Santa Ana street at dawn, small bakery storefront with windmill logo visible above the door, terra-cotta and cream painted exterior, neon "open" sign just turned on. **+ style suffix**

> The cracked sidewalk in front of a Mexican bakery, brown paper bag with the windmill logo on it placed on the curb, soft early morning light. **+ style suffix** *(replace logo description with windmill mark if Gemini struggles)*

## Detail / craft shots

> A baker's hand sprinkling colored sugar on rows of unbaked conchas on a parchment-lined tray, top-down view, no face. **+ style suffix**

> Single torta on butcher paper, neatly cut in half so the egg, ham, and cheese are visible, glass of orange juice in the corner. **+ style suffix**

> Pile of orange peels on a wooden cutting board beside a glass of fresh orange juice, juicing in process. **+ style suffix**

---

## Calendar-aligned prompts (active queue)

These four prompts replace typography posts in the current calendar with photo
backgrounds. Save each as the filename listed, then ask Claude to swap.

### conchas-warm.jpg — for Week 1 Post 05 "Still warm"

> Close-up macro photograph of freshly baked conchas with red, yellow, and white colored sugar topping, faint steam rising, on a brown paper bakery liner. Golden warm morning light coming from the left. Very shallow depth of field. Photorealistic, vertical 1080×1350 aspect. Warm cream and dark red and gold color palette, neighborhood Mexican panadería atmosphere in Southern California. No people, no text, no logos visible.

### storefront-dawn.jpg — for Week 2 Post 01 "Off MacArthur"

> Exterior of a small Mexican bakery on a quiet Santa Ana street at 5:30 AM. Terra-cotta and cream colored building, warm interior light glowing through the front window, sidewalk visible, no cars, no people. Peaceful pre-dawn atmosphere with hints of orange sky. Photorealistic, vertical 1080×1350 aspect. Warm cream and dark red and gold color palette. No text, no logos visible on the building.

### bakery-interior.jpg — for Week 2 Post 03 "Same windmill. Since day one."

> Interior of an established old-school Mexican panadería at dawn. Wooden counters worn smooth from years of use, glass pastry case full of pan dulce, vintage framed photos on the wall. Warm morning light through a side window. Timeless, established feeling. Photorealistic, vertical 1080×1350 aspect. Warm cream and dark red and gold color palette, Southern California neighborhood bakery atmosphere. No people, no text, no logos visible.

### baker-dough.jpg — for Week 2 Post 06 "Dough at 4. Doors at 5."

> Hands of a baker placing a tray of unbaked conchas on a wooden counter at 4 AM, only hands and tray visible — no face. Golden warm light from a single overhead lamp, dark surrounding the lit area. Intimate atmospheric pre-dawn shot of bakery preparation. Photorealistic, vertical 1080×1350 aspect. Warm cream and dark red and gold color palette. No face shown, no text, no logos visible.

---

## Usage tip

Generate **3 variations** of any prompt and keep the strongest one. Nano banana is fast — iteration is free.

## What NOT to ask for

- People with detailed faces (Gemini struggles, results uncanny)
- Text overlays (Gemini text is unreliable — render text in our Python post generator instead)
- Specific named items not on the menu
- Logos beyond the windmill mark (it can't recreate the brand exactly)
