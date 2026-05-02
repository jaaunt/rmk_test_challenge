import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import math

# Estonian crime type labels in English for the plot
CRIME_LABELS_EN = {
    "Tapmine": "Manslaughter",
    "Mõrv": "Murder",
    "Kehaline väärkohtlemine": "Assault",
    "Vargus": "Theft",
    "Röövimine": "Robbery",
    "Kelmus": "Fraud",
    "Liikluskuritegu": "Traffic crime",
}

def load_events(path: str) -> tuple[list[str], list[float]]:
    """Load processed crime probabilities from JSON file."""
    with open(path, encoding="utf-8") as f:
        events = json.load(f)
    labels = [CRIME_LABELS_EN[e["label"]] for e in events]
    probs = [e["probability"] for e in events]
    return labels, probs

def plot_probability_scale(labels: list[str], probs: list[float], out_path: str):
    """
    Draw a horizontal lollipop chart of annual crime probabilities on a log scale.

    Each marker represents the probability that a randomly selected Estonian
    resident was a victim of that crime type in 2021.
    X-axis uses a log scale to accommodate several orders of magnitude.
    """
    # Sort ascending so rarest crime appears at the bottom
    paired = sorted(zip(probs, labels))
    probs_sorted = [p for p, _ in paired]
    labels_sorted = [l for _, l in paired]

    fig, ax = plt.subplots(figsize=(13, 7))
    fig.patch.set_facecolor("#f9f9f7")
    ax.set_facecolor("#f9f9f7")

    # Alternate annotation above/below to avoid overlap between close points
    offsets = [10, -14] * (len(probs_sorted) // 2 + 1)

    for i, (prob, label) in enumerate(zip(probs_sorted, labels_sorted)):
        ax.hlines(i, 1e-7, prob, colors="#aac4d4", linewidth=1.5,
                  linestyle="--", alpha=0.6)
        ax.scatter(prob, i, color="#1f6e8c", s=90, zorder=3)
        ax.annotate(
            f"1 in {int(1 / prob):,}".replace(",", "\u202f"),
            xy=(prob, i),
            xytext=(0, offsets[i]),
            textcoords="offset points",
            ha="center",
            va="bottom" if offsets[i] > 0 else "top",
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
    ax.xaxis.set_minor_locator(ticker.NullLocator())  # remove minor ticks for clarity

    ax.xaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, _: f"1 in {round(1/x):,}".replace(",", "\u202f"))
        # round up, ensures major ticks are consistent (10 000, 100 000, ...)
    )

    ax.set_xlabel("Annual probability per resident", fontsize=11)
    ax.set_title(
        "Probability of being a crime victim in Estonia (2021)",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    ax.annotate(
        "Source: Statistics Estonia JS009 · Population: 1\u202f331\u202f824",
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
    print(f"Saved to {out_path}")

if __name__ == "__main__":
    labels, probs = load_events("data/processed.json")
    plot_probability_scale(labels, probs, "output/probability_scale.png")
