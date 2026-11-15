"""Draw docs/flex_outcomes.png: how the in-scope FLEX tests ended, by oxygen and droplet size.

Run from the repo root:  python docs/make_chart.py
Needs: pandas, matplotlib. Reads data/clean/flex_clean.csv, changes no data.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean" / "flex_clean.csv"
OUT = ROOT / "docs" / "flex_outcomes.png"

SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
# outcome: (label, colour, marker, sideways nudge in % oxygen so repeats at one oxygen level stay visible)
OUTCOMES = {
    "Extinction": ("Went out before the fuel was gone", "#2a78d6", "o", -0.3),
    "Completion": ("Burned until the fuel was gone", "#eb6834", "D", 0.3),
    "Disruption": ("Disruption (no clear outcome)", MUTED, "x", 0.0),
}


def main():
    df = pd.read_csv(CLEAN)
    scope = df[df["pressure_atm"].notna() & (df["pressure_atm"] <= 1.1) & df["d0_mm"].notna()]

    plt.rcParams.update({"font.family": ["Segoe UI", "DejaVu Sans"], "font.size": 10})
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.9), sharex=True, sharey=True, facecolor=SURFACE)
    for ax, fuel in zip(axes, ["heptane", "methanol"]):
        part = scope[scope["fuel"] == fuel]
        ax.set_facecolor(SURFACE)
        ax.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for end in ["Disruption", "Extinction", "Completion"]:      # draw the rare outcome last, on top
            label, colour, marker, nudge = OUTCOMES[end]
            g = part[part["test_end"] == end]
            if marker == "x":
                ax.scatter(g["o2_pct"] + nudge, g["d0_mm"], s=30, marker="x", color=colour, linewidths=1.2, label=label)
            else:
                ax.scatter(g["o2_pct"] + nudge, g["d0_mm"], s=46, marker=marker, color=colour,
                           edgecolors=SURFACE, linewidths=1.0, label=label)
        done = int((part["test_end"] == "Completion").sum())
        clear = int(part["test_end"].isin(["Extinction", "Completion"]).sum())
        ax.set_title(f"{fuel.capitalize()}: {done} of {clear} burned until the fuel was gone",
                     loc="left", fontsize=10.5, color=INK2, pad=8)
        ax.set_xlabel("Oxygen in the chamber, %", color=INK2)
        ax.tick_params(colors=MUTED, length=0)
        for side in ["top", "right", "left"]:
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(AXIS)
    axes[0].set_ylabel("Droplet diameter at ignition, mm", color=INK2)
    axes[0].set_ylim(0.5, 5.0)

    handles, labels = axes[0].get_legend_handles_labels()
    order = [labels.index(OUTCOMES[k][0]) for k in ["Extinction", "Completion", "Disruption"]]
    fig.legend([handles[i] for i in order], [labels[i] for i in order], loc="upper left", bbox_to_anchor=(0.05, 0.925),
               ncol=3, frameon=False, labelcolor=INK2, handletextpad=0.3, columnspacing=1.8)
    went_out = int((scope["test_end"] == "Extinction").sum())
    clear_all = int(scope["test_end"].isin(["Extinction", "Completion"]).sum())
    fig.suptitle(f"Most FLEX droplet flames went out before the fuel was gone: {went_out} of {clear_all}",
                 x=0.062, y=0.975, ha="left", fontsize=13.5, fontweight="bold", color=INK)
    fig.text(0.062, 0.015,
             f"Each mark is one of the {len(scope)} FLEX tests the console uses (NASA PSI-69, at or below 1.1 atm, including tests "
             "with CO2 or helium added).\nCounts leave out disruptions. "
             "Marks are nudged sideways by outcome so repeats at one oxygen level stay visible.",
             fontsize=8.5, color=MUTED, ha="left", va="bottom", linespacing=1.4)
    fig.subplots_adjust(left=0.062, right=0.985, top=0.77, bottom=0.215, wspace=0.06)
    fig.savefig(OUT, dpi=200, facecolor=SURFACE)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
