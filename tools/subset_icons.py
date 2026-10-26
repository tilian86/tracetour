#!/usr/bin/env python3
"""Material-Symbols-Icon-Font auf die tatsaechlich genutzten Icons verkleinern.

Die volle Schrift (fonts/source/materialsymbolsoutlined-full.woff2) ist ~1,1 MB.
Dieses Skript sucht alle Icon-Namen in den HTML-Dateien und baut daraus
fonts/materialsymbols-subset.woff2 (wenige KB).

Nach jedem neuen Icon in index.html/app.html einfach neu ausfuehren:
    python3 -m venv /tmp/ft && /tmp/ft/bin/pip install fonttools brotli
    /tmp/ft/bin/python tools/subset_icons.py
Danach in fonts/fonts.css den ?v=-Parameter der Subset-URL hochzaehlen.
"""
import re
import sys
from pathlib import Path

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'fonts/source/materialsymbolsoutlined-full.woff2'
OUT = ROOT / 'fonts/materialsymbols-subset.woff2'
PAGES = ['index.html', 'app.html']

# Icons, die nur per JavaScript gesetzt werden (textContent=...), hier zusaetzlich auffuehren
EXTRA = ['play_arrow', 'pause', 'lock', 'cloud_done', 'cloud_download', 'assignment', 'map']


def used_icons():
    names = set(EXTRA)
    for page in PAGES:
        html = (ROOT / page).read_text(encoding='utf-8')
        names |= set(re.findall(r'material-symbols-outlined[^>]*>\s*([a-z0-9_]+)\s*<', html))
    return sorted(names)


def main():
    names = used_icons()
    font = TTFont(SRC)
    cmap = font.getBestCmap()
    glyph_to_char = {g: chr(c) for c, g in cmap.items()}
    gsub = font['GSUB'].table
    # Ligatur-Tabelle: ausgeschriebener Icon-Name -> Glyph (Aliase wie emoji_events -> trophy inklusive)
    lig_out = {}
    for lookup in gsub.LookupList.Lookup:
        for st in lookup.SubTable:
            t = st.ExtSubTable if lookup.LookupType == 7 else st
            for first, ligs in getattr(t, 'ligatures', {}).items():
                for lig in ligs:
                    seq = [first] + list(lig.Component)
                    if all(g in glyph_to_char for g in seq):
                        lig_out[''.join(glyph_to_char[g] for g in seq).lower()] = lig.LigGlyph
    order = set(font.getGlyphOrder())
    missing = [n for n in names if n not in lig_out]
    if missing:
        sys.exit('Unbekannte Icon-Namen: ' + ', '.join(missing))
    targets = {lig_out[n] for n in names}
    glyphs = targets | {g + '.fill' for g in targets if g + '.fill' in order}
    letters = {cmap[c] for c in cmap if chr(c).isalnum() or chr(c) in ' _'}
    glyphs |= letters

    opts = Options()
    opts.layout_closure = False
    opts.layout_features = ['*']
    opts.flavor = 'woff2'
    opts.name_IDs = ['*']
    opts.notdef_outline = True
    sub = Subsetter(opts)
    sub.populate(glyphs=sorted(glyphs))
    sub.subset(font)
    font.flavor = 'woff2'
    font.save(OUT)
    print(f'{len(names)} Icons -> {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB)')
    print(' '.join(names))


if __name__ == '__main__':
    main()
