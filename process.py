"""
process.py — compute annual per-person event probabilities from raw Statistics Estonia data.

Reads raw JSON files produced by fetch_data.py and outputs data/processed.json, a dict
structured as {year: [event, ...]}.  Each event has:
    label       : display name
    probability : annual probability per Estonian resident
    category    : 'crime' or 'anchor'
    count       : raw count (crime and fetched anchor events only)
    source      : citation string (anchor events only)

Run after fetch_data.py:
    python process.py
"""

import json

YEARS = [str(y) for y in range(2015, 2022)]

# Crime type labels in the same order as the API returns values
# (matches the order of crime codes defined in fetch_data.py)
CRIME_LABELS = [
    "Manslaughter",
    "Murder",
    "Assault",
    "Theft",
    "Robbery",
    "Fraud",
    "Traffic crime",
]

# Anchor events that cannot be fetched from any API — hardcoded with citations.
#
#   Birthday coincidence: deterministic — exactly 1/365 days in a year.
#
# Lightning fatality: no Estonia specfic data available
# Based on WHO and European estimates (~0.2–1 per million per year).
# Using ~1 in 1,000,000 annual probability as an order-of-magnitude estimate.
STATIC_ANCHORS = [
    {
        "label": "Dying on your birthday\n(birthday matches death date)",
        "probability": 1 / 365,
        "source": "deterministic (1/365)",
    },
    {
        "label": "Struck by lightning\n(fatality, Annual)",
        "probability": 1 / 1_000_000,
        "source": "National Weather Service: https://www.weather.gov/safety/lightning-odds",
    },
]


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def compute_probabilities(
    crimes_path: str,
    population_path: str,
    births_path: str,
    deaths_path: str,
) -> dict:
    """
    Compute annual per-person probabilities for all years and event types.

    Crime probabilities: reported_cases / population (JS009 / RV0240).
    Fetched anchor probabilities: count / population, sourced from:
        births — RV030 (Näitaja '1')
        deaths — RV030 (Näitaja '2')
    Static anchor probabilities: hardcoded constants (see STATIC_ANCHORS above).

    Assumptions and limitations:
    - Crime counts reflect reported cases only; true rates are likely higher.
    - Each crime case is assumed to involve a unique victim.
    - Population denominator is total Estonia, not at-risk subgroups.
    - Lightning rate is a European average — Estonia-specific data unavailable.
    """
    crimes     = load_json(crimes_path)
    population = load_json(population_path)
    births     = load_json(births_path)
    deaths     = load_json(deaths_path)

    crime_values = crimes["value"]
    n_crimes = len(CRIME_LABELS)

    result = {}
    for i, year in enumerate(YEARS):
        pop = population[year]
        events = []

        # --- crime events ---
        year_counts = crime_values[i * n_crimes : (i + 1) * n_crimes]
        for label, count in zip(CRIME_LABELS, year_counts):
            events.append({
                "label": label,
                "count": count,
                "probability": count / pop,
                "category": "crime",
            })

        # --- fetched anchor events ---
        events.extend([
            {
                "label": "Being born in Estonia\n(in a given year)",
                "count": births[year],
                "probability": births[year] / pop,
                "source": "Statistics Estonia RV030",
                "category": "anchor",
            },
            {
                "label": "Dying in Estonia\n(in a given year)",
                "count": deaths[year],
                "probability": deaths[year] / pop,
                "source": "Statistics Estonia RV030",
                "category": "anchor",
            },
        ])

        # --- static anchor events (same value every year) ---
        for anchor in STATIC_ANCHORS:
            events.append({
                "label": anchor["label"],
                "probability": anchor["probability"],
                "source": anchor["source"],
                "category": "anchor",
            })

        result[year] = events
        print(f"{year}: {len(events)} events ({n_crimes} crimes + {len(events) - n_crimes} anchors)")

    return result


if __name__ == "__main__":
    result = compute_probabilities(
        crimes_path="data/crimes_raw.json",
        population_path="data/population.json",
        births_path="data/births.json",
        deaths_path="data/deaths.json",
    )

    with open("data/processed.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\nSaved to data/processed.json")
