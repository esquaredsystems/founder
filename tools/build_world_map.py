#!/usr/bin/env python3
"""
Generate _includes/world-map.svg from Natural Earth country outlines.

The map is a plain, static SVG committed to the repo — no JavaScript library,
no runtime data fetch, no build step for the site itself. Each country path
carries its ISO 3166-1 alpha-2 code as an id and its English name as a <title>,
so CSS does the shading and the browser does the hover tooltip.

Run it only when you want to regenerate the map:

    npm pack world-atlas                     # once, to get the source data
    tar xzf world-atlas-*.tgz
    python3 tools/build_world_map.py package/countries-110m.json

Source data: Natural Earth via the `world-atlas` package, public domain.
"""

import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "_includes", "world-map.svg")

# Map is drawn in an equirectangular projection, then clipped below 60°S so
# Antarctica does not eat half the frame.
WIDTH = 1000.0
LAT_TOP = 84.0
LAT_BOTTOM = -60.0

# ISO 3166-1 numeric -> alpha-2, for the countries that appear in the dataset.
# Only the codes actually used for shading need to be right; the rest are
# cosmetic, so this table is generated from the dataset's own ids at runtime
# using a compact numeric->alpha2 lookup.
NUM_TO_A2 = {}


def load_numeric_lookup():
    """
    A minimal ISO 3166-1 numeric -> alpha-2 table. Kept inline so the script has
    no dependencies. Entries missing from here simply get no id and cannot be
    shaded — harmless for a decorative map.
    """
    pairs = """
004 AF|008 AL|012 DZ|024 AO|032 AR|051 AM|036 AU|040 AT|031 AZ|044 BS|050 BD|
112 BY|056 BE|084 BZ|204 BJ|064 BT|068 BO|070 BA|072 BW|076 BR|096 BN|100 BG|
854 BF|108 BI|116 KH|120 CM|124 CA|140 CF|148 TD|152 CL|156 CN|170 CO|178 CG|
180 CD|188 CR|384 CI|191 HR|192 CU|196 CY|203 CZ|208 DK|262 DJ|214 DO|218 EC|
818 EG|222 SV|226 GQ|232 ER|233 EE|231 ET|242 FJ|246 FI|250 FR|266 GA|270 GM|
268 GE|276 DE|288 GH|300 GR|304 GL|320 GT|324 GN|624 GW|328 GY|332 HT|340 HN|
348 HU|352 IS|356 IN|360 ID|364 IR|368 IQ|372 IE|376 IL|380 IT|388 JM|392 JP|
400 JO|398 KZ|404 KE|408 KP|410 KR|414 KW|417 KG|418 LA|428 LV|422 LB|426 LS|
430 LR|434 LY|440 LT|442 LU|450 MG|454 MW|458 MY|466 ML|478 MR|484 MX|498 MD|
496 MN|499 ME|504 MA|508 MZ|104 MM|516 NA|524 NP|528 NL|540 NC|554 NZ|558 NI|
562 NE|566 NG|578 NO|512 OM|586 PK|591 PA|598 PG|600 PY|604 PE|608 PH|616 PL|
620 PT|630 PR|634 QA|642 RO|643 RU|646 RW|682 SA|686 SN|688 RS|694 SL|702 SG|
703 SK|705 SI|090 SB|706 SO|710 ZA|728 SS|724 ES|144 LK|729 SD|740 SR|748 SZ|
752 SE|756 CH|760 SY|158 TW|762 TJ|834 TZ|764 TH|626 TL|768 TG|780 TT|788 TN|
792 TR|795 TM|800 UG|804 UA|784 AE|826 GB|840 US|858 UY|860 UZ|548 VU|862 VE|
704 VN|732 EH|887 YE|894 ZM|716 ZW|010 AQ|260 TF|238 FK|292 GI|833 IM|474 MQ
"""
    for chunk in pairs.replace("\n", "").split("|"):
        chunk = chunk.strip()
        if not chunk:
            continue
        num, a2 = chunk.split()
        NUM_TO_A2[str(int(num))] = a2


# --------------------------------------------------------------------------
# TopoJSON decoding (the format stores integer deltas, not coordinates)
# --------------------------------------------------------------------------

def decode_arcs(topology):
    scale = topology["transform"]["scale"]
    translate = topology["transform"]["translate"]
    decoded = []
    for arc in topology["arcs"]:
        x = y = 0
        points = []
        for dx, dy in arc:
            x += dx
            y += dy
            points.append((x * scale[0] + translate[0], y * scale[1] + translate[1]))
        decoded.append(points)
    return decoded


def arc_points(arcs, index):
    if index >= 0:
        return arcs[index]
    return list(reversed(arcs[~index]))


def project(lon, lat):
    """Equirectangular. Simple, honest about area, and cheap."""
    x = (lon + 180.0) / 360.0 * WIDTH
    height = WIDTH * (LAT_TOP - LAT_BOTTOM) / 360.0
    y = (LAT_TOP - lat) / (LAT_TOP - LAT_BOTTOM) * height
    return x, y


# Rings smaller than this many pixels across are dropped. At this map size they
# render as sub-pixel specks, and there are thousands of them.
MIN_RING_PX = 1.1


def ring_to_path(arcs, ring):
    coords = []
    for idx in ring:
        pts = arc_points(arcs, idx)
        if coords and pts and coords[-1] == pts[0]:
            pts = pts[1:]
        coords.extend(pts)
    if len(coords) < 3:
        return ""

    projected = [project(lon, max(min(lat, LAT_TOP), LAT_BOTTOM)) for lon, lat in coords]
    xs = [p[0] for p in projected]
    ys = [p[1] for p in projected]
    if (max(xs) - min(xs)) < MIN_RING_PX and (max(ys) - min(ys)) < MIN_RING_PX:
        return ""

    # Fiji and Russia straddle the antimeridian. In an equirectangular
    # projection a polygon that wraps from +180 to -180 is drawn as a stripe
    # across the entire map, so the ring is broken into subpaths at the seam.
    out = []
    last = None
    started = False
    for i, (x, y) in enumerate(projected):
        pt = (round(x, 1), round(y, 1))
        wrapped = last is not None and abs(pt[0] - last[0]) > WIDTH * 0.5
        if pt == last and i not in (0, len(projected) - 1):
            continue  # collapsed by rounding
        cmd = "M" if (not started or wrapped) else "L"
        if cmd == "M" and started:
            out.append("Z")
        out.append("%s%g %g" % (cmd, pt[0], pt[1]))
        started = True
        last = pt
    if len(out) < 3:
        return ""
    return "".join(out) + "Z"


def geometry_to_path(arcs, geom):
    kind = geom.get("type")
    parts = []
    if kind == "Polygon":
        for ring in geom["arcs"]:
            parts.append(ring_to_path(arcs, ring))
    elif kind == "MultiPolygon":
        for polygon in geom["arcs"]:
            for ring in polygon:
                parts.append(ring_to_path(arcs, ring))
    return "".join(p for p in parts if p)


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    load_numeric_lookup()
    topology = json.load(open(sys.argv[1], encoding="utf-8"))
    arcs = decode_arcs(topology)

    height = WIDTH * (LAT_TOP - LAT_BOTTOM) / 360.0
    rows = []
    for geom in topology["objects"]["countries"]["geometries"]:
        name = geom.get("properties", {}).get("name", "")
        a2 = NUM_TO_A2.get(str(geom.get("id", "")).lstrip("0") or "0", "")
        if a2 == "AQ":
            continue
        d = geometry_to_path(arcs, geom)
        if not d:
            continue
        attrs = ' d="%s"' % d
        if a2:
            attrs = ' id="c-%s"%s' % (a2, attrs)
        rows.append("  <path%s><title>%s</title></path>" % (attrs, esc(name)))

    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
        'class="worldmap" role="img" aria-label="World map highlighting countries '
        'worked in and visited">' % (WIDTH, round(height)),
        "  <g class=\"worldmap__countries\">",
    ]
    svg.extend(rows)
    svg.append("  </g>")
    svg.append("</svg>")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(svg) + "\n")

    sized = os.path.getsize(OUT) / 1024.0
    print("wrote %s (%d countries, %.0f KB)" % (
        os.path.relpath(OUT, REPO), len(rows), sized))
    return 0


if __name__ == "__main__":
    sys.exit(main())
