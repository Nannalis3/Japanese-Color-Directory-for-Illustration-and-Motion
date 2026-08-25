Ready-to-import swatch files for **motion graphics, graphic design, and illustration**, built from Sanzo Wada's *A Dictionary of Color Combinations* (配色総鑑, 1933–34): **159 colors** in **348 curated combinations** (120 two-color, 120 three-color, 108 four-color).

**[Browse the palette →](index.html)** — single-file viewer, works on GitHub Pages or opened locally. Click any color to copy its hex.

## About the Dictionary

This dictionary convert's Wada's CMYK colors to RGB for digital production. Most digital versions (including the popular sanzo-wada web app) convert them to RGB with naive math, which produces neon values the printed book never had (e.g. Hermosa Pink as `#FFB3F0`).

This library re-derives every RGB value with a proper ICC conversion:

> **CMYK → sRGB via Japan Color 2001 Coated** (the standard profile for Japanese sheet-fed offset on coated stock — appropriate for a book printed in Japan), rendering intent **relative colorimetric with black point compensation**.

Hermosa Pink becomes the soft `#F7C9D5` — much closer to the physical plates. The original CMYK values are preserved in the data so you can always re-convert with a different profile. This dataset also restores **Citrine** and **Chromium Green**, which the upstream web app's data silently dropped (157 → 159 colors), fixing 13 broken combinations.

## What's in here

| Path | For | Contents |
|---|---|---|
| `swatches/adobe-ase/` | Illustrator, Photoshop, InDesign, Affinity, AE (via Ray Dynamic Color) | `sanzo-wada-all-colors.ase` (159 colors grouped by hue section), `sanzo-wada-combinations.ase` (348 named groups), `sanzo-wada-all-colors.aco` (for Clip Studio Paint) |
| `swatches/procreate/` | Procreate (iPad) | 8 `.swatches` palettes grouped by hue, ≤30 colors each |
| `motion/` | After Effects, Premiere | `sanzo-wada-palette.jsx` (palette-builder script), `ae-colors.json` (hex + 0–1 RGB for expressions), `colors.csv` |
| `png/` | Any NLE, mood boards | 348 combination cards at 1920×1080 + a master contact sheet |
| `tokens/` | Web, Figma, design systems | `sanzo-wada.tokens.json` (W3C DTCG 2025.10), `sanzo-wada.css` (custom properties), `_sanzo-wada.scss` |
| `data/` | Everything else | `colors.json` (canonical: name, CMYK, RGB, hex, HSV, combination ids), `combinations.json` |
| `scripts/` | Rebuilding | Python generators for every file above (`pip install -r requirements.txt`, needs the Japan Color 2001 Coated profile installed with Adobe apps) |

## Usage by app

### After Effects
AE has no native swatch panel or `.ase` import. Two workflows:

1. **Script (recommended):** `File → Scripts → Run Script File…` → `motion/sanzo-wada-palette.jsx`. Enter a combination number (1–348) or leave blank for all 159 colors. It creates a disabled guide-layer null holding one **Color Control per color**. Reference from any property:
   ```js
   thisComp.layer("SANZO No. 048").effect("Eosine Pink")("Color")
   ```
   Change the control once, every linked layer updates.
2. **Ray Dynamic Color / goodboy Swatches:** import `swatches/adobe-ase/sanzo-wada-combinations.ase` directly.

**Color management note:** hex values are display-referred **sRGB**. In a default or sRGB-working-space project they paste correctly. In an ACES/OCIO project, interpret them as **sRGB — Texture** (not Rec.709) or mids and shadows will shift. Don't look for separate Rec.709 hex values — sRGB and Rec.709 share primaries and white point; only the transfer curve differs.

### Premiere Pro
Drop any `png/combinations/combination-XXX.png` into the project as a reference still, or eyedrop from it in Essential Graphics. Hex values can be pasted into any Premiere color picker.

### Illustrator / Photoshop / InDesign
Swatches panel → menu → **Open Swatch Library / Load Swatches → Other Library…** → pick an `.ase`. Combinations arrive as named folders ("No. 048 — Eosine Pink · …").

### Affinity Designer / Photo / Publisher
Swatches panel → **Import Palette** → `.ase`.

### Procreate
AirDrop or open any `swatches/procreate/*.swatches` file on the iPad — it lands in the Palettes panel.

### Clip Studio Paint
Color Set palette → **Import color set** → `sanzo-wada-all-colors.aco` (CSP reads `.aco`, not `.ase`).

### Figma
Use the [Palette Importer](https://www.figma.com/community/plugin/1067561134666722782/palette-importer) plugin with the `.ase`, or import `tokens/sanzo-wada.tokens.json` with any DTCG-compatible tokens plugin to get Variables.

### Web
```css
@import "tokens/sanzo-wada.css";
.hero { background: var(--sanzo-eosine-pink); }
```
SCSS users get combination lists too: `nth($sanzo-combo-048, 1)`.

## Data schema

`data/colors.json`:
```json
{
  "index": 9, "name": "Eosine Pink", "slug": "eosine-pink", "section": "a",
  "cmyk": [0, 63, 23, 0], "rgb": [246, 133, 148], "hex": "#f68594",
  "hsv": [352.0, 45.9, 96.5], "combinations": [34, 59, 90]
}
```
`data/combinations.json` maps each combination id to its member color indices. Sections `a`–`f` follow the book's hue ordering (reds → yellows/browns → greens → blues → violets → neutrals).

## Rebuilding

```bash
cd scripts
python3 -m venv venv && venv/bin/pip install -r requirements.txt
venv/bin/python gen_data.py      # CMYK → sRGB conversion (needs Japan Color 2001 Coated ICC)
venv/bin/python gen_adobe.py     # .ase + .aco
venv/bin/python gen_procreate.py
venv/bin/python gen_motion.py
venv/bin/python gen_tokens.py
venv/bin/python gen_png.py
venv/bin/python gen_viewer.py    # regenerates index.html with embedded data
```

## Attribution & license

- Original work: **Sanzo Wada** (和田三造, 1883–1967), *Haishoku Sōkan* (配色総鑑), 1933–34; reprinted by Seigensha as *A Dictionary of Color Combinations*. Wada's works are public domain in Japan (since 2018). The color values and names themselves are uncopyrightable facts; this repo deliberately contains **no scans of the book's plates**.
- CMYK source data: [dblodorn/sanzo-wada](https://github.com/dblodorn/sanzo-wada) (MIT), cross-checked against [mattdesl/dictionary-of-colour-combinations](https://github.com/mattdesl/dictionary-of-colour-combinations) (MIT, same 159/348 corrected structure; that project used U.S. Web Coated SWOP v2, so its hex values differ slightly from the Japan Color values here).
- Everything in this repository: **MIT** — see [LICENSE](LICENSE).
