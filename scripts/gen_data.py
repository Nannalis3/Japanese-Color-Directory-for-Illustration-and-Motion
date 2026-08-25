"""Canonical dataset from the authoritative swatches_a-f files (159 colors, 348 combos).
CMYK -> sRGB via Japan Color 2001 Coated, perceptual intent."""
from PIL import Image, ImageCms
import json, colorsys, re

BASE = '/Users/akristensen/Downloads/sanzo-wada-master/apps/sanzo-wada-alpha'
PROFILE = "/Library/Application Support/Adobe/Color/Profiles/Recommended/JapanColor2001Coated.icc"
OUT = '/private/tmp/claude-504/-Users-akristensen-Downloads/5f074a5a-b19b-4a54-904e-aaa0d72767d4/scratchpad/build'

RENAME = {"Mars Brown Tobacco": "Mars Brown / Tobacco"}

xform = ImageCms.buildTransform(
    ImageCms.getOpenProfile(PROFILE), ImageCms.createProfile("sRGB"),
    "CMYK", "RGB", renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC, flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)

def cmyk_to_srgb(c, m, y, k):
    im = Image.new("CMYK", (1, 1), (round(c*2.55), round(m*2.55), round(y*2.55), round(k*2.55)))
    return ImageCms.applyTransform(im, xform).getpixel((0, 0))

def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

colors, combos = [], {}
idx = 0
for section in 'abcdef':
    entries = list(json.load(open(f'{BASE}/src/colors/swatches_{section}.json')).values())[0]
    for col in entries:
        idx += 1
        name = RENAME.get(col['name'], col['name'])
        c, m, y, k = col['cmyk']
        r, g, b = cmyk_to_srgb(c, m, y, k)
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        colors.append({
            "index": idx,
            "name": name,
            "slug": slugify(name),
            "section": section,
            "cmyk": [c, m, y, k],
            "rgb": [r, g, b],
            "hex": f"#{r:02x}{g:02x}{b:02x}",
            "hsv": [round(h*360, 1), round(s*100, 1), round(v*100, 1)],
            "combinations": col['combinations'],
        })
        for cid in col['combinations']:
            combos.setdefault(cid, []).append(idx)

combinations = [{"id": cid, "colors": idxs} for cid, idxs in sorted(combos.items())]

json.dump({"colors": colors}, open(f"{OUT}/colors.json", "w"), indent=2)
json.dump({"combinations": combinations}, open(f"{OUT}/combinations.json", "w"), indent=2)

sizes = {}
for combo in combinations:
    sizes[len(combo['colors'])] = sizes.get(len(combo['colors']), 0) + 1
slugs = [c['slug'] for c in colors]
print("colors:", len(colors), "| combos:", len(combinations), "| sizes:", dict(sorted(sizes.items())),
      "| dupe slugs:", [s for s in set(slugs) if slugs.count(s) > 1])
