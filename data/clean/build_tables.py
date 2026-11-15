"""Read the PSI Experimental Tables in data/raw/psi_tables and pull out one thing they share: the oxygen level
(and, where the table has it, the pressure) of each test. Writes console/tables.js for the dashboard's oxygen map
and data/clean/psi_tables_summary.json for the local AI.

    py data/clean/build_tables.py

Nothing is estimated or filled in. A row whose oxygen cell cannot be read as a number is counted but not plotted.
What each table's oxygen column means is written in SOURCES below, because it is not the same thing everywhere:
for an "inverse" gas flame the oxygen flows out of the burner into fuel, so its value is not a cabin atmosphere.
"""
import csv
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "psi_tables"
MOON_O2, MOON_PSI = 30.0, 10.2                 # from the challenge brief: 30 % oxygen or more, 10.2 psi or less
MOON_ATM = MOON_PSI / 14.696
NEAR_PSI = 10.5                                # chamber pressures aimed at 10.2 psi were measured a little above it
NEAR_ATM = NEAR_PSI / 14.696
BAR, MMHG = 1.01325, 760.0

# file, short name, what burned, oxygen column, how to read it, pressure column, pressure unit, what the oxygen value is
SOURCES = [
    ("PSI-69_Experimental table_FLEX.csv", "FLEX", "liquid droplets", "O initial ambient", "fraction", "Ambient pressure", "mmHg", "ambient"),
    ("PSI-39_Experimental table_CFI.csv", "CFI", "liquid droplets", "Oxygen", "fraction", "Pressure", "atm", "ambient"),
    ("PSI-159_Experimental table_CFI-G_Normal Flames.csv", "CFI-G, normal flames", "gas flames", "XO2 before test", "fraction", "approx p (bar)", "bar", "ambient"),
    ("PSI-10_Experimental table_Flame Design_Normal Flame.csv", "Flame Design, normal flames", "gas flames", "XO2 (init)", "fraction", "pinit (atm)", "atm", "ambient"),
    ("PSI-25_Experimental table_BASS-II.csv", "BASS-II", "solid materials", "initial O2 % by vol", "percent", None, None, "ambient"),
    ("PSI-99_Experimental table_SAFFIRE-2.csv", "Saffire-II", "solid materials", "Percent O2", "percent", None, None, "ambient"),
    ("PSI-98_Experimental table_SAFFIRE-1.csv", "Saffire-I", "solid materials", "Percent O2", "percent", None, None, "ambient"),
    ("PSI-159_Experimental table_CFI-G_Inverse Flames.csv", "CFI-G, inverse flames", "gas flames", "XO2", "fraction", "approx p (bar)", "bar", "burner"),
    ("PSI-10_Experimental table_Flame Design_Inverse Flame.csv", "Flame Design, inverse flames", "gas flames", "XO2", "fraction", "pinit (atm)", "atm", "burner"),
]


def numbers(cell):
    return [float(x) for x in re.findall(r"\d+(?:\.\d+)?", cell.replace(",", ""))]


def read(name):
    raw = (RAW / name).read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    rows = [r for r in csv.reader(io.StringIO(text)) if any(c.strip() for c in r)]
    return [c.strip() for c in rows[0]], rows[1:]


def column(head, want):
    hits = [i for i, c in enumerate(head) if c.lower().startswith(want.lower()) or want.lower() in c.lower()]
    exact = [i for i, c in enumerate(head) if c.lower() == want.lower()]
    if not hits:
        raise SystemExit(f"column {want!r} not found in {head}")
    return (exact or hits)[0]


def main():
    manifest = json.loads((RAW / "MANIFEST.json").read_text(encoding="utf-8"))
    out, summary = [], {}
    for name, short, what, o2_col, o2_kind, p_col, p_unit, meaning in SOURCES:
        head, rows = read(name)
        info = manifest[name]
        io2, ip = column(head, o2_col), column(head, p_col) if p_col else None
        pts, unread = [], 0
        for r in rows:
            vals = numbers(r[io2]) if io2 < len(r) else []
            if not vals:
                unread += 1
                continue
            o2 = sum(vals) / len(vals)                       # a cell such as "21.5 - 21.7" is read as its middle
            o2 = o2 * 100 if o2_kind == "fraction" else o2
            p = None
            if ip is not None and ip < len(r) and numbers(r[ip]):
                p = numbers(r[ip])[0] / {"mmHg": MMHG, "bar": BAR, "atm": 1.0}[p_unit]
                p = p if p > 0 else None                     # FLEX test 114 has pressure 0 in the table: not a pressure
            if not 0 < o2 <= 100:
                unread += 1
                continue
            pts.append([round(o2, 1), None if p is None else round(p, 3)])
        with_p = [pt for pt in pts if pt[1] is not None]
        rich = sum(1 for pt in pts if pt[0] >= MOON_O2)
        with_p = [pt for pt in pts if pt[1] is not None]
        zone = sum(1 for pt in with_p if pt[0] >= MOON_O2 and pt[1] <= MOON_ATM + 1e-9)
        near = sum(1 for pt in with_p if pt[0] >= MOON_O2 and MOON_ATM + 1e-9 < pt[1] <= NEAR_ATM + 1e-9)
        row = {"id": info["investigation"], "name": short, "what": what, "oxygen_is": meaning, "file": name, "version": info["psi_version"], "doi": info["doi"],
               "licence": info["licence"], "rows": len(rows), "unread": unread, "has_pressure": bool(with_p), "pts": pts}
        out.append(row)
        o2s, ps = [pt[0] for pt in pts], [pt[1] for pt in with_p]
        line = (f"{short} [{info['investigation']}]: {len(rows)} rows in its PSI Experimental Table, {len(pts)} with a readable oxygen value. "
                + ("Oxygen in the burner flow (inverse flame, not a cabin atmosphere): " if meaning == "burner" else "Oxygen in the surrounding gas: ")
                + f"{min(o2s):g} to {max(o2s):g} percent. "
                + (f"Pressure: {min(ps):.2f} to {max(ps):.2f} atm. " if ps else "The table gives no pressure. ")
                + f"Rows at 30 percent oxygen or more: {rich}."
                + (f" Rows at 30 percent oxygen or more AND 10.2 psi or less (Moon Base air): {zone}."
                   f" Rows at 30 percent oxygen or more just above that pressure, 10.2 to 10.5 psi: {near}." if ps and meaning == "ambient" else ""))
        summary.setdefault(info["investigation"], []).append(line)
        print(line)
    ambient = [r for r in out if r["oxygen_is"] == "ambient"]
    both = [pt for r in ambient for pt in r["pts"] if pt[1] is not None]
    zone = [pt for pt in both if pt[0] >= MOON_O2 and pt[1] <= MOON_ATM + 1e-9]
    near = [pt for pt in both if pt[0] >= MOON_O2 and MOON_ATM + 1e-9 < pt[1] <= NEAR_ATM + 1e-9]
    meta = {"moon_o2_pct": MOON_O2, "moon_psi": MOON_PSI, "moon_atm": round(MOON_ATM, 4), "near_psi": NEAR_PSI, "near_atm": round(NEAR_ATM, 4),
            "near_moon_zone": len(near), "fetched": max(v["fetched"] for v in manifest.values()),
            "ambient_tests": sum(len(r["pts"]) for r in ambient), "ambient_with_pressure": len(both), "in_moon_zone": len(zone)}
    print(f"\nambient-oxygen rows: {meta['ambient_tests']}, with pressure too: {len(both)}, inside the Moon Base zone: {len(zone)}, just above its pressure line: {len(near)}")
    js = "// Built by data/clean/build_tables.py from the NASA PSI Experimental Tables in data/raw/psi_tables. Do not edit by hand.\n"
    js += "window.FLAME_TABLES = " + json.dumps({"meta": meta, "rows": out}, separators=(",", ":")) + ";\n"
    (ROOT / "console" / "tables.js").write_text(js, encoding="utf-8", newline="\n")
    (ROOT / "data" / "clean" / "psi_tables_summary.json").write_text(json.dumps({"meta": meta, "lines": summary}, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote console/tables.js ({len(js)} bytes) and data/clean/psi_tables_summary.json")


if __name__ == "__main__":
    main()
