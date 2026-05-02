"""
plot.py — visualise Estonian crime victim probabilities as a lollipop chart.

Reads processed probabilities from data/processed.json and produces one
chart per year, saved to the output/ directory.

Run after fetch_data.py and process.py:
    python plot.py
"""
import json
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Translate data labels to english for the plot
CRIME_LABELS_EN = {
    "Manslaughter": "Manslaughter",
    "Murder": "Murder",
    "Assault": "Assault",
    "Theft": "Theft",
    "Robbery": "Robbery",
    "Fraud": "Fraud",
    "Traffic crime": "Traffic crime",
}

def load_all_years(path: str) -> dict:
    """Load processed crime probabilities for all years from JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def plot_probability_scale(labels: list[str], probs: list[float], year: str, out_path: str):
    """
    Draw a horizontal lollipop chart of annual crime probabilities on a log scale.

    Each marker represents the probability that a randomly selected Estonian
    resident was a victim of that crime type in the given year.
    X-axis uses a log scale to accommodate several orders of magnitude.
    """
    paired = sorted(zip(probs, labels))
    probs_sorted = [p for p, _ in paired]
    labels_sorted = [l for _, l in paired]

    fig, ax = plt.subplots(figsize=(13, 7))
    fig.patch.set_facecolor("#f9f9f7")
    ax.set_facecolor("#f9f9f7")

    offsets = [10] * len(probs_sorted)

    for i, (prob, label) in enumerate(zip(probs_sorted, labels_sorted)):
        ax.hlines(i, 1e-7, prob, colors="#aac4d4", linewidth=1.5,
                  linestyle="--", alpha=0.6)
        ax.scatter(prob, i, color="#1f6e8c", s=90, zorder=3)
        ax.annotate(
            f"1 in {round(1 / prob):,}".replace(",", "\u202f"),
            xy=(prob, i),
            xytext=(0, offsets[i]),
            textcoords="offset points",
            ha="center",
            va="bottom",  # dot should always be under the label
            fontsize=9,
            fontweight="bold",
            color="#1f6e8c",
        )

    ax.set_xscale("log")
    ax.set_xlim(1e-7, 1e-1)
    ax.set_ylim(-0.8, len(labels_sorted) - 0.2)
    ax.set_yticks(range(len(labels_sorted)))
    ax.set_yticklabels(labels_sorted, fontsize=11)
    ax.xaxis.set_major_locator(ticker.LogLocator(base=10, numticks=10))
    ax.xaxis.set_minor_locator(ticker.NullLocator())
    ax.xaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, _: f"1 in {round(1/x):,}".replace(",", "\u202f"))
    )

    ax.set_xlabel("Annual probability per resident", fontsize=11)
    ax.set_title(
        f"Probability of being a crime victim in Estonia ({year})",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    ax.annotate(
        "Source: Statistics Estonia JS009 · RV0240",
        xy=(0.5, -0.12),
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
        labels = [e["label"] for e in events]
        probs = [e["probability"] for e in events]
        out_path = os.path.join(out_dir, f"probability_scale_{year}.png")
        plot_probability_scale(labels, probs, year, out_path)

if __name__ == "__main__":
    data = load_all_years("data/processed.json")
    plot_all_years(data, "output")
