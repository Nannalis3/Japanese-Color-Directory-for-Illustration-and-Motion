"""Procreate .swatches: zip containing Swatches.json (minimal legacy schema, 30-swatch cap).
One palette per hue section, split when a section exceeds 30."""
import json, zipfile, colorsys, os

REPO = os.path.expanduser('~/CLAUDE_PROJECTS/sanzo-wada-swatches')
colors = json.load(open(f'{REPO}/data/colors.json'))['colors']

SECTIONS = {'a': 'Reds & Pinks', 'b': 'Yellows, Browns & Greens', 'c': 'Greens & Teals',
            'd': 'Blues', 'e': 'Violets & Purples', 'f': 'Neutrals & Blacks'}

def swatch(col):
    r, g, b = [v/255 for v in col['rgb']]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return {"hue": round(h, 6), "saturation": round(s, 6), "brightness": round(v, 6),
            "alpha": 1, "colorSpace": 0}

def write_palette(name, cols, fname):
    payload = {"name": name, "swatches": [swatch(c) for c in cols]}
    path = f'{REPO}/swatches/procreate/{fname}.swatches'
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('Swatches.json', json.dumps(payload))
    print(fname, len(cols), 'colors')

for s, title in SECTIONS.items():
    group = [c for c in colors if c['section'] == s]
    if len(group) <= 30:
        write_palette(f"Sanzo Wada — {title}", group, f"sanzo-wada-{title.split(' ')[0].lower().rstrip(',')}-{s}")
    else:
        for part in range((len(group) + 29) // 30):
            chunk = group[part*30:(part+1)*30]
            write_palette(f"Sanzo Wada — {title} ({part+1})", chunk,
                          f"sanzo-wada-{title.split(' ')[0].lower().rstrip(',')}-{s}{part+1}")
