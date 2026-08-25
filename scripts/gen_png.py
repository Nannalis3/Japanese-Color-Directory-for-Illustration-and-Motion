"""PNG reference sheets: one master contact sheet + one card per combination.
Cards are 1920x1080 (drop straight into Premiere/AE as a reference or matte source)."""
from PIL import Image, ImageDraw, ImageFont
import json, os

REPO = os.path.expanduser('~/CLAUDE_PROJECTS/sanzo-wada-swatches')
colors = {c['index']: c for c in json.load(open(f'{REPO}/data/colors.json'))['colors']}
combos = json.load(open(f'{REPO}/data/combinations.json'))['combinations']

def font(size):
    for p in ("/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/HelveticaNeue.ttc"):
        try: return ImageFont.truetype(p, size)
        except Exception: pass
    return ImageFont.load_default()

F_NAME, F_HEX, F_TITLE = font(34), font(28), font(40)

def text_color(rgb):
    r, g, b = [x/255 for x in rgb]
    lum = 0.2126*r + 0.7152*g + 0.0722*b
    return (20, 20, 20) if lum > 0.45 else (245, 245, 245)

# --- combination cards: 1920x1080, vertical stripes, labeled ---
W, H, FOOTER = 1920, 1080, 0
for combo in combos:
    members = [colors[i] for i in combo['colors']]
    im = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(im)
    n = len(members)
    for i, col in enumerate(members):
        x0, x1 = round(i*W/n), round((i+1)*W/n)
        d.rectangle([x0, 0, x1, H], fill=tuple(col['rgb']))
        tc = text_color(col['rgb'])
        d.text((x0+28, H-130), col['name'], font=F_NAME, fill=tc)
        d.text((x0+28, H-84), col['hex'].upper(), font=F_HEX, fill=tc)
    d.text((28, 28), f"Sanzo Wada — Combination {combo['id']}", font=F_NAME,
           fill=text_color(members[0]['rgb']))
    im.save(f"{REPO}/png/combinations/combination-{combo['id']:03d}.png")

# --- master contact sheet of all 159 colors ---
COLS, SW, SH, PAD, LABEL_H = 8, 300, 220, 0, 78
rows = -(-len(colors)//COLS)
sheet = Image.new('RGB', (COLS*SW, rows*(SH+LABEL_H) + 120), (247, 245, 240))
d = ImageDraw.Draw(sheet)
d.text((32, 30), "Sanzo Wada — A Dictionary of Color Combinations — 159 colors (Japan Color 2001 Coated → sRGB)",
       font=F_TITLE, fill=(30, 30, 30))
for i, col in enumerate(sorted(colors.values(), key=lambda c: c['index'])):
    r, c = divmod(i, COLS)
    x, y = c*SW, 120 + r*(SH+LABEL_H)
    d.rectangle([x, y, x+SW, y+SH], fill=tuple(col['rgb']))
    d.text((x+16, y+SH+8), f"{col['index']:03d}  {col['name']}", font=font(26), fill=(30, 30, 30))
    d.text((x+16, y+SH+42), col['hex'].upper(), font=font(24), fill=(110, 110, 110))
sheet.save(f"{REPO}/png/all-colors-sheet.png")
print("combination cards:", len(combos), "| sheet size:", sheet.size)
