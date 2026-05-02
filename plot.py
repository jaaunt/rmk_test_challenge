"""
plot.py — visualise Estonian crime and reference-event probabilities as a lollipop chart.

Reads processed probabilities from data/processed.json and produces one chart per year,
saved to the output/ directory.  For 2021 the chart also includes anchor events (everyday
reference points that span a wider probability range) so readers can develop intuition
about scale.

Crime events are shown as blue circles; reference/anchor events as grey diamonds.

Run after fetch_data.py and process.py:
    python plot.py
"""

import json
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D


def load_all_years(path: str) -> dict:
    """Load processed crime probabilities (and anchor events) for all years from JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def plot_probability_scale(events: list[dict], year: str, out_path: str):
    """
    Draw a horizontal lollipop chart of annual probabilities on a log scale.

    Each row is one event. Crime events (blue circles) come from Statistics Estonia
    crime data. Anchor events (grey diamonds) are everyday reference points included
    to give readers a sense of scale across several orders of magnitude.

    Parameters
    ----------
    events   : list of dicts with keys 'label', 'probability', 'category'
               category is either 'crime' or 'anchor'
    year     : string label used in the chart title
    out_path : file path for the saved PNG
    """
    CRIME_COLOR       = "#1f6e8c"
    ANCHOR_COLOR      = "#888888"
    STEM_COLOR_CRIME  = "#aac4d4"
    STEM_COLOR_ANCHOR = "#cccccc"

    # Sort all events by probability ascending so rarest appears at the bottom
    events_sorted = sorted(events, key=lambda e: e["probability"])
    labels = [e["label"] for e in events_sorted]
    probs  = [e["probability"] for e in events_sorted]
    cats   = [e.get("category", "crime") for e in events_sorted]

    n = len(events_sorted)
    fig, ax = plt.subplots(figsize=(14, max(7, n * 0.7)))
    fig.patch.set_facecolor("#f9f9f7")
    ax.set_facecolor("#f9f9f7")

    for i, (prob, label, cat) in enumerate(zip(probs, labels, cats)):
        is_anchor  = cat == "anchor"
        stem_color = STEM_COLOR_ANCHOR if is_anchor else STEM_COLOR_CRIME
        dot_color  = ANCHOR_COLOR      if is_anchor else CRIME_COLOR
        marker     = "D"               if is_anchor else "o"   # diamond vs circle
        dot_size   = 70                if is_anchor else 90

        ax.hlines(i, 5e-7, prob, colors=stem_color, linewidth=1.5,
                  linestyle="--", alpha=0.6)
        ax.scatter(prob, i, color=dot_color, s=dot_size, marker=marker, zorder=3)
        ax.annotate(
            f"1 in {round(1 / prob):,}\n{prob:.2e}" if prob < 1e-4 else f"1 in {round(1 / prob):,}\n{prob:.4f}".replace(",", "\u202f"),
            xy=(prob, i),
            xytext=(0, 9),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color=dot_color,
        )

    ax.set_xscale("log")
    ax.set_xlim(5e-7, 5e-2)
    ax.set_ylim(-0.8, n - 0.2)
    ax.set_yticks(range(n))
    ax.set_yticklabels(labels, fontsize=10)
    ax.xaxis.set_major_locator(ticker.LogLocator(base=10, numticks=10))
    ax.xaxis.set_minor_locator(ticker.NullLocator())
    ax.xaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, _: f"1 in {round(1/x):,}".replace(",", "\u202f"))
    )

    ax.set_xlabel("Annual probability per resident", fontsize=11)
    ax.set_title(
        f"Probability of events in Estonia ({year})",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )

    # Legend distinguishing the two series
    legend_elements = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=CRIME_COLOR,
               markersize=9, label="Crime (Statistics Estonia JS009)"),
        Line2D([0], [0], marker="D", color="w", markerfacecolor=ANCHOR_COLOR,
               markersize=8, label="Reference event"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=9,
              framealpha=0.7, edgecolor="#cccccc")

    ax.annotate(
        "Sources: Statistics Estonia JS009 · RV0240 · RV0222 · RV0251 · LS004; "
        "National Weather Service",
        xy=(0.5, -0.08),
        xycoords="axes fraction",
        ha="center",
        fontsize=8,
        color="#888888",
    )

    ax.grid(axis="x", which="major", alpha=0.25, color="#aaaaaa")
    ax.spines[["top", "right", "left"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved to {out_path}")


def plot_all_years(data: dict, out_dir: str):
    """Generate one lollipop chart per year and save to out_dir."""
    for year, events in data.items():
        out_path = os.path.join(out_dir, f"probability_scale_{year}.png")
        plot_probability_scale(events, year, out_path)


if __name__ == "__main__":
    data = load_all_years("data/processed.json")
    plot_all_years(data, "output")
