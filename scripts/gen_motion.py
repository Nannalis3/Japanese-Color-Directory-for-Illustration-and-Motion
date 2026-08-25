"""Motion kit: ae-colors.json (expression-friendly), colors.csv, and an AE .jsx
that builds a color-control palette layer for any combination (or all colors)."""
import json, csv, os

REPO = os.path.expanduser('~/CLAUDE_PROJECTS/sanzo-wada-swatches')
colors = json.load(open(f'{REPO}/data/colors.json'))['colors']
combos = json.load(open(f'{REPO}/data/combinations.json'))['combinations']
by_idx = {c['index']: c for c in colors}

# --- ae-colors.json: slug-keyed, rgb as 0-1 floats ready for expressions ---
ae = {c['slug']: {"name": c['name'], "hex": c['hex'],
                  "rgb01": [round(v/255, 6) for v in c['rgb']]} for c in colors}
json.dump({"colors": ae,
           "combinations": {str(cb['id']): [by_idx[i]['slug'] for i in cb['colors']] for cb in combos}},
          open(f'{REPO}/motion/ae-colors.json', 'w'), indent=2)

# --- colors.csv ---
with open(f'{REPO}/motion/colors.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['index', 'name', 'hex', 'r', 'g', 'b', 'c', 'm', 'y', 'k', 'combinations'])
    for c in colors:
        w.writerow([c['index'], c['name'], c['hex'], *c['rgb'], *c['cmyk'],
                    ' '.join(map(str, c['combinations']))])

# --- AE .jsx ---
compact_colors = [[c['name'], [round(v/255, 4) for v in c['rgb']]] for c in colors]
compact_combos = {str(cb['id']): cb['colors'] for cb in combos}

jsx = """// Sanzo Wada Palette Builder — After Effects
// Creates a guide-layer null named "SANZO No. <id>" (or "SANZO ALL COLORS") holding one
// Color Control per color. Reference from any property with an expression like:
//   thisComp.layer("SANZO No. 048").effect("Eosine Pink")("Color")
// Data: 159 colors / 348 combinations, Japan Color 2001 Coated -> sRGB.
// Usage: File > Scripts > Run Script File... with a comp active.

(function () {
    var COLORS = __COLORS__;
    var COMBOS = __COMBOS__;

    var comp = app.project.activeItem;
    if (!(comp && comp instanceof CompItem)) {
        alert("Open a composition first, then run this script.");
        return;
    }

    var input = prompt("Combination number (1-348), or leave empty to load ALL 159 colors:", "");
    if (input === null) return; // cancelled

    var picks, layerName;
    input = input.replace(/^\\s+|\\s+$/g, "");
    if (input === "") {
        picks = [];
        for (var i = 0; i < COLORS.length; i++) picks.push(i + 1);
        layerName = "SANZO ALL COLORS";
    } else {
        if (!COMBOS[input]) {
            alert("No combination \\"" + input + "\\". Enter a number from 1 to 348.");
            return;
        }
        picks = COMBOS[input];
        layerName = "SANZO No. " + (input.length < 3 ? ("00" + input).slice(-3) : input);
    }

    app.beginUndoGroup("Sanzo Wada Palette");
    var layer = comp.layers.addNull(comp.duration);
    layer.name = layerName;
    layer.guideLayer = true;
    layer.enabled = false;
    for (var p = 0; p < picks.length; p++) {
        var c = COLORS[picks[p] - 1];
        var fx = layer.property("ADBE Effect Parade").addProperty("ADBE Color Control");
        fx.name = c[0];
        fx.property("ADBE Color Control-0001").setValue(c[1]);
    }
    app.endUndoGroup();
    alert(layerName + " created with " + picks.length + " color control(s).\\n\\n" +
          "Expression example:\\nthisComp.layer(\\"" + layerName + "\\").effect(\\"" +
          COLORS[picks[0] - 1][0] + "\\")(\\"Color\\")");
})();
"""
jsx = jsx.replace('__COLORS__', json.dumps(compact_colors, separators=(',', ':')))
jsx = jsx.replace('__COMBOS__', json.dumps(compact_combos, separators=(',', ':')))
open(f'{REPO}/motion/sanzo-wada-palette.jsx', 'w').write(jsx)
print('motion kit written:', [f for f in os.listdir(f"{REPO}/motion")])
