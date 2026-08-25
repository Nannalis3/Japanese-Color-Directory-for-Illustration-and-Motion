"""Web/design tokens: DTCG 2025.10 JSON (color objects w/ hex fallback), CSS custom
properties, SCSS variables. Combination groups alias the base color tokens."""
import json, os

REPO = os.path.expanduser('~/CLAUDE_PROJECTS/sanzo-wada-swatches')
colors = json.load(open(f'{REPO}/data/colors.json'))['colors']
combos = json.load(open(f'{REPO}/data/combinations.json'))['combinations']
by_idx = {c['index']: c for c in colors}

# --- DTCG tokens ---
tok_colors = {}
for c in colors:
    tok_colors[c['slug']] = {
        "$value": {
            "colorSpace": "srgb",
            "components": [round(v/255, 6) for v in c['rgb']],
            "alpha": 1,
            "hex": c['hex'],
        },
        "$description": f"Sanzo Wada color no. {c['index']} — {c['name']}",
    }
tok_combos = {}
for cb in combos:
    tok_combos[f"no-{cb['id']:03d}"] = {
        f"color-{n+1}": {"$value": f"{{sanzo.{by_idx[i]['slug']}}}"}
        for n, i in enumerate(cb['colors'])
    }
tokens = {
    "$schema": "https://www.designtokens.org/schemas/2025.10/format.json",
    "sanzo": {"$type": "color", **tok_colors},
    "sanzo-combinations": {"$type": "color", **tok_combos},
}
json.dump(tokens, open(f'{REPO}/tokens/sanzo-wada.tokens.json', 'w'), indent=2)

# --- CSS custom properties ---
lines = ["/* Sanzo Wada — A Dictionary of Color Combinations (159 colors) */",
         "/* CMYK -> sRGB via Japan Color 2001 Coated, rel. colorimetric + BPC */", ":root {"]
lines += [f"  --sanzo-{c['slug']}: {c['hex']};" for c in colors]
lines.append("}")
open(f'{REPO}/tokens/sanzo-wada.css', 'w').write("\n".join(lines) + "\n")

# --- SCSS ---
s = ["// Sanzo Wada — A Dictionary of Color Combinations (159 colors)"]
s += [f"$sanzo-{c['slug']}: {c['hex']};" for c in colors]
s.append("\n// Combinations as lists (e.g. nth($sanzo-combo-048, 1))")
for cb in combos:
    members = ", ".join(f"$sanzo-{by_idx[i]['slug']}" for i in cb['colors'])
    s.append(f"$sanzo-combo-{cb['id']:03d}: ({members});")
open(f'{REPO}/tokens/_sanzo-wada.scss', 'w').write("\n".join(s) + "\n")
print('tokens written:', os.listdir(f'{REPO}/tokens'))
