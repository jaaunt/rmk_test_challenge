"""
plot_trend.py — visualise how Estonian crime victim probabilities changed over time.

Reads processed probabilities from data/processed.json and produces a single
line chart with one line per crime type on a log-scaled y-axis.

Run after fetch_data.py and process.py:
    python plot_trend.py
"""

import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def load_all_years(path: str) -> dict:
    """Load processed crime probabilities for all years from JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def plot_trend(data: dict, out_path: str):
    """
    Draw a line chart showing how crime probabilities changed over 2015–2021.

    Each crime type is a separate line. Y-axis uses a log scale so all crime
    types are visible despite large differences in magnitude.
    """
    fig, ax = plt.subplots(figsize=(13, 7))
    fig.patch.set_facecolor("#f9f9f7")
    ax.set_facecolor("#f9f9f7")

    years = sorted(data.keys())
    crime_labels = [e["label"] for e in data[years[0]]]

    for label in crime_labels:
        probs = [
            next(e["probability"] for e in data[year] if e["label"] == label)
            for year in years
        ]
        ax.plot(years, probs, marker="o", linewidth=2, markersize=6, label=label)

    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda y, _: f"1 in {round(1/y):,}".replace(",", "\u202f"))
    )
    ax.set_xlabel("Year", fontsize=11)
    ax.set_ylabel("Annual probability per resident", fontsize=11)
    ax.set_title(
        "Crime victim probability in Estonia over time (2015–2021)",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    for label in crime_labels:
        probs = [
            next(e["probability"] for e in data[year] if e["label"] == label)
            for year in years
        ]
        line, = ax.plot(years, probs, marker="o", linewidth=2, markersize=6)
        ax.annotate(
            label,
            xy=(years[-1], probs[-1]),
            xytext=(5, 0),
            textcoords="offset points",
            va="center",
            fontsize=11,
            color=line.get_color(),
        )
    ax.grid(axis="y", which="major", alpha=0.25, color="#aaaaaa")
    # Shaded COVID-19 period (2020–2021)
    ax.axvspan("2020", "2021", alpha=0.08, color="red", zorder=0)
    ax.annotate("COVID-19\nperiod", xy=("2020", ax.get_ylim()[1]),
                xytext=(5, -15), textcoords="offset points",
                fontsize=10, color="#cc4444")
    ax.spines[["top", "right"]].set_visible(False)
    ax.annotate(
        "Source: Statistics Estonia JS009 · RV0240",
        xy=(0.5, -0.10),
        xycoords="axes fraction",
        ha="center",
        fontsize=8,
        color="#888888",
    )

    fig.subplots_adjust(right=0.82) # add extra room so labels fit
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    data = load_all_years("data/processed.json")
    plot_trend(data, "output/probability_trend.png")
