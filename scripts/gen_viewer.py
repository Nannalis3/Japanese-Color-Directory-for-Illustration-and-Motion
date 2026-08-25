"""Single-file viewer: index.html with embedded data. No build tools, no fetch."""
import json, os
REPO = os.path.expanduser('~/CLAUDE_PROJECTS/sanzo-wada-swatches')
colors = json.load(open(f'{REPO}/data/colors.json'))['colors']
combos = json.load(open(f'{REPO}/data/combinations.json'))['combinations']
slim_colors = [{"i": c["index"], "n": c["name"], "h": c["hex"], "r": c["rgb"]} for c in colors]
slim_combos = [{"id": c["id"], "c": c["colors"]} for c in combos]
DATA = json.dumps({"colors": slim_colors, "combos": slim_combos}, separators=(',', ':'))

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sanzo Wada — A Dictionary of Color Combinations</title>
<style>
  :root { --bg:#f4f1ea; --ink:#1e1c1a; --muted:#8a8478; --card:#fffdf8; }
  * { box-sizing:border-box; margin:0; }
  body { background:var(--bg); color:var(--ink);
         font:16px/1.5 "Avenir Next","Helvetica Neue",Helvetica,Arial,sans-serif; }
  header { padding:40px 48px 8px; }
  h1 { font-size:26px; font-weight:600; letter-spacing:.02em; }
  h1 span { color:var(--muted); font-weight:400; }
  .sub { color:var(--muted); font-size:14px; margin-top:4px; }
  nav { display:flex; flex-wrap:wrap; gap:10px; padding:20px 48px 28px; align-items:center; }
  button.tab, button.pill { border:1px solid #d8d2c4; background:transparent; color:var(--ink);
    border-radius:999px; padding:7px 18px; font-size:14px; cursor:pointer; }
  button.active { background:var(--ink); color:var(--bg); border-color:var(--ink); }
  input#q { border:1px solid #d8d2c4; background:var(--card); border-radius:999px;
    padding:7px 18px; font-size:14px; width:230px; outline:none; }
  main { padding:0 48px 80px; }
  .grid { display:grid; gap:22px; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); }
  .combo { background:var(--card); border-radius:10px; overflow:hidden;
    box-shadow:0 1px 3px rgba(30,28,26,.09); }
  .combo .stripes { display:flex; height:150px; }
  .combo .stripe { flex:1; cursor:pointer; transition:flex .18s ease; position:relative; }
  .combo .stripe:hover { flex:1.7; }
  .combo .meta { padding:10px 14px; font-size:12.5px; color:var(--muted);
    display:flex; justify-content:space-between; }
  .swatch { background:var(--card); border-radius:10px; overflow:hidden; cursor:pointer;
    box-shadow:0 1px 3px rgba(30,28,26,.09); }
  .swatch .chip { height:110px; }
  .swatch .meta { padding:10px 14px; font-size:13px; }
  .swatch .meta b { display:block; font-weight:600; font-size:13.5px; }
  .swatch .meta span { color:var(--muted); font-size:12px; }
  #toast { position:fixed; left:50%; bottom:34px; transform:translateX(-50%) translateY(80px);
    background:var(--ink); color:var(--bg); padding:10px 22px; border-radius:999px;
    font-size:14px; transition:transform .25s ease; pointer-events:none; }
  #toast.show { transform:translateX(-50%) translateY(0); }
  footer { padding:0 48px 48px; color:var(--muted); font-size:13px; }
  footer a { color:inherit; }
</style>
</head>
<body>
<header>
  <h1>Sanzo Wada <span>— A Dictionary of Color Combinations</span></h1>
  <div class="sub">159 colors · 348 combinations · click any color to copy its hex</div>
</header>
<nav>
  <button class="tab active" data-view="combos">Combinations</button>
  <button class="tab" data-view="colors">Colors</button>
  <span id="sizeFilters">
    <button class="pill" data-size="all">All</button>
    <button class="pill" data-size="2">2-color</button>
    <button class="pill" data-size="3">3-color</button>
    <button class="pill" data-size="4">4-color</button>
  </span>
  <input id="q" type="search" placeholder="Search color name…">
</nav>
<main><div class="grid" id="grid"></div></main>
<footer>
  Colors converted from the book's CMYK via Japan Color 2001 Coated → sRGB.
  Data & swatch files: see the <a href="https://github.com/">repository</a>.
</footer>
<div id="toast">copied</div>
<script>
var DATA = __DATA__;
var byIdx = {}; DATA.colors.forEach(function(c){ byIdx[c.i] = c; });
var view = 'combos', size = 'all', query = '';
var grid = document.getElementById('grid');

function textColor(rgb){
  var l = (0.2126*rgb[0] + 0.7152*rgb[1] + 0.0722*rgb[2]) / 255;
  return l > 0.45 ? '#1e1c1a' : '#f4f1ea';
}
function copyHex(hex){
  (navigator.clipboard ? navigator.clipboard.writeText(hex) : Promise.reject()).catch(function(){
    var t = document.createElement('textarea'); t.value = hex;
    document.body.appendChild(t); t.select(); document.execCommand('copy'); t.remove();
  });
  var toast = document.getElementById('toast');
  toast.textContent = hex.toUpperCase() + ' copied';
  toast.classList.add('show');
  clearTimeout(toast._t); toast._t = setTimeout(function(){ toast.classList.remove('show'); }, 1400);
}
function render(){
  grid.innerHTML = '';
  var frag = document.createDocumentFragment();
  if (view === 'combos') {
    DATA.combos.forEach(function(cb){
      var members = cb.c.map(function(i){ return byIdx[i]; });
      if (size !== 'all' && members.length !== +size) return;
      if (query && !members.some(function(m){ return m.n.toLowerCase().indexOf(query) > -1; })) return;
      var card = document.createElement('div'); card.className = 'combo';
      var stripes = document.createElement('div'); stripes.className = 'stripes';
      members.forEach(function(m){
        var s = document.createElement('div'); s.className = 'stripe';
        s.style.background = m.h; s.title = m.n + ' ' + m.h.toUpperCase();
        s.onclick = function(){ copyHex(m.h); };
        stripes.appendChild(s);
      });
      var meta = document.createElement('div'); meta.className = 'meta';
      meta.innerHTML = '<span>No. ' + cb.id + '</span><span>' +
        members.map(function(m){ return m.n; }).join(' · ') + '</span>';
      card.appendChild(stripes); card.appendChild(meta); frag.appendChild(card);
    });
  } else {
    DATA.colors.forEach(function(c){
      if (query && c.n.toLowerCase().indexOf(query) === -1) return;
      var card = document.createElement('div'); card.className = 'swatch';
      card.onclick = function(){ copyHex(c.h); };
      var chip = document.createElement('div'); chip.className = 'chip';
      chip.style.background = c.h;
      var meta = document.createElement('div'); meta.className = 'meta';
      meta.innerHTML = '<b>' + c.n + '</b><span>' + c.h.toUpperCase() + '</span>';
      card.appendChild(chip); card.appendChild(meta); frag.appendChild(card);
    });
  }
  grid.appendChild(frag);
}
document.querySelectorAll('.tab').forEach(function(b){
  b.onclick = function(){
    document.querySelectorAll('.tab').forEach(function(x){ x.classList.remove('active'); });
    b.classList.add('active'); view = b.dataset.view;
    document.getElementById('sizeFilters').style.display = view === 'combos' ? '' : 'none';
    render();
  };
});
document.querySelectorAll('.pill').forEach(function(b){
  b.onclick = function(){
    document.querySelectorAll('.pill').forEach(function(x){ x.classList.remove('active'); });
    b.classList.add('active'); size = b.dataset.size; render();
  };
});
document.querySelector('.pill[data-size="all"]').classList.add('active');
document.getElementById('q').oninput = function(e){ query = e.target.value.toLowerCase(); render(); };
render();
</script>
</body>
</html>
"""
open(f'{REPO}/index.html', 'w').write(HTML.replace('__DATA__', DATA))
print('index.html written:', os.path.getsize(f'{REPO}/index.html'), 'bytes')
