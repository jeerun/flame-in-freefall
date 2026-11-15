"""Build data/clean/flex_clean.csv from the raw PSI-69 FLEX experimental table.

Run from the repo root:  python data/clean/build_clean.py
Nothing in data/raw is modified.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "psi69_flex_experimental_table.tsv"
OUT = ROOT / "data" / "clean" / "flex_clean.csv"

BAD = "�"  # replacement character the PSI page shows in some cells


def num(text, flags, name):
    """Parse a number. Blank or unreadable cells become None, with a flag."""
    text = text.strip()
    if text == "":
        return None
    if BAD in text:
        flags.append(f"{name} unreadable in source")
        return None
    return float(text)


def main():
    rows = list(csv.reader(RAW.open(encoding="utf-8"), delimiter="\t"))
    body = [r for r in rows[1:] if r and r[0].strip()]  # drop the empty last row

    out = []
    for r in body:
        flags = []
        test, flex_id, date, gmt, fuel = r[0], r[1], r[2], r[3], r[4]
        p_mmhg = num(r[5], flags, "pressure")
        if p_mmhg is not None and p_mmhg <= 0:
            flags.append("pressure recorded as 0 in source")
            p_mmhg = None
        o2, n2, co2, he = (num(r[i], flags, n) for i, n in ((6, "o2"), (7, "n2"), (8, "co2"), (9, "he")))
        d0 = num(r[10], flags, "droplet diameter")
        dext = num(r[11], flags, "extinction diameter")
        k = num(r[12], flags, "burning rate")
        tb_text = r[13].strip()
        approx = tb_text.startswith("~")
        if approx:
            flags.append("burn time approximate in source")
        tburn = num(tb_text.lstrip("~"), flags, "burn time")

        pct = lambda x: None if x is None else round(x * 100, 2)
        out.append({
            "test": int(test),
            "flex_id": flex_id,
            "date": date,
            "gmt": gmt,
            "fuel": fuel.strip().lower(),
            "pressure_atm": None if p_mmhg is None else round(p_mmhg / 760.0, 4),
            "o2_pct": pct(o2),
            "n2_pct": pct(n2),
            "co2_pct": pct(co2),
            "he_pct": pct(he),
            "d0_mm": d0,
            "ext_diameter_mm": dext,
            "burn_rate_mm2_s": k,
            "burn_time_s": tburn,
            "test_end": r[14].strip(),
            "flags": "; ".join(flags),
        })

    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        for row in out:
            w.writerow({k: ("" if v is None else v) for k, v in row.items()})
    print(f"wrote {OUT.relative_to(ROOT)}: {len(out)} tests")


if __name__ == "__main__":
    main()
