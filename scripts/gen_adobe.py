"""Adobe swatch files: .ase (master by hue section + one grouped by combination) and .aco
(for Clip Studio Paint). ASE spec: big-endian, ASEF header, 0xC001/0xC002/0x0001 blocks,
UTF-16BE names, RGB float32 0-1, color type 2 (normal)."""
import json, struct, os

REPO = os.path.expanduser('~/CLAUDE_PROJECTS/sanzo-wada-swatches')
colors = json.load(open(f'{REPO}/data/colors.json'))['colors']
combos = json.load(open(f'{REPO}/data/combinations.json'))['combinations']
by_idx = {c['index']: c for c in colors}

def ase_str(s):
    enc = s.encode('utf-16-be') + b'\x00\x00'
    return struct.pack('>H', len(s) + 1) + enc

def color_block(col):
    data = ase_str(col['name']) + b'RGB ' + struct.pack('>fff', *[v/255 for v in col['rgb']]) + struct.pack('>H', 2)
    return struct.pack('>HI', 0x0001, len(data)) + data

def group_start(name):
    data = ase_str(name)
    return struct.pack('>HI', 0xC001, len(data)) + data

GROUP_END = struct.pack('>HI', 0xC002, 0)

def write_ase(path, groups):
    """groups: list of (group_name, [colors])"""
    blocks = []
    for gname, gcolors in groups:
        blocks.append(group_start(gname))
        blocks += [color_block(c) for c in gcolors]
        blocks.append(GROUP_END)
    with open(path, 'wb') as f:
        f.write(b'ASEF' + struct.pack('>HH', 1, 0) + struct.pack('>I', len(blocks)))
        f.writelines(blocks)

SECTIONS = {'a': 'I — Reds & Pinks', 'b': 'II — Yellows, Browns & Greens',
            'c': 'III — Greens & Teals', 'd': 'IV — Blues',
            'e': 'V — Violets & Purples', 'f': 'VI — Neutrals & Blacks'}
master_groups = [(f"Sanzo Wada {title}", [c for c in colors if c['section'] == s])
                 for s, title in SECTIONS.items()]
write_ase(f'{REPO}/swatches/adobe-ase/sanzo-wada-all-colors.ase', master_groups)

combo_groups = []
for cb in combos:
    members = [by_idx[i] for i in cb['colors']]
    combo_groups.append((f"No. {cb['id']:03d} — " + " · ".join(m['name'] for m in members), members))
write_ase(f'{REPO}/swatches/adobe-ase/sanzo-wada-combinations.ase', combo_groups)

# .aco — version 1 + version 2 sections, RGB color space (0), 16-bit channels
def aco_color_v1(col):
    r, g, b = col['rgb']
    return struct.pack('>HHHHH', 0, r*257, g*257, b*257, 0)

def aco_color_v2(col):
    name = col['name']
    return aco_color_v1(col) + struct.pack('>I', len(name) + 1) + name.encode('utf-16-be') + b'\x00\x00'

with open(f'{REPO}/swatches/adobe-ase/sanzo-wada-all-colors.aco', 'wb') as f:
    f.write(struct.pack('>HH', 1, len(colors)))
    f.writelines(aco_color_v1(c) for c in colors)
    f.write(struct.pack('>HH', 2, len(colors)))
    f.writelines(aco_color_v2(c) for c in colors)

for p in ('sanzo-wada-all-colors.ase', 'sanzo-wada-combinations.ase', 'sanzo-wada-all-colors.aco'):
    print(p, os.path.getsize(f'{REPO}/swatches/adobe-ase/{p}'), 'bytes')
