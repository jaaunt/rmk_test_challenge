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

def compute_probabilities(crimes_path: str, population_path: str) -> dict:
    """
    Compute annual per-person crime probabilities for each year and crime type.

    The API returns values as a flat list ordered by year first, then crime type.
    We reshape this into a dict: {year: [{label, count, probability}, ...]}

    Method: probability = reported_cases / population

    Assumptions and limitations:
    - Assumes each reported case involves a unique victim (may underestimate
      true probability if one person is victimised multiple times)
    - Based on reported crimes only — unreported cases are not captured
      (true probability is likely higher due to the 'dark figure' of crime)
    - Population used as denominator is total Estonian population,
      not at-risk subgroups
    """
    with open(crimes_path, encoding="utf-8") as f:
        crimes = json.load(f)

    with open(population_path, encoding="utf-8") as f:
        population = json.load(f)

    values = crimes["value"]
    n_crimes = len(CRIME_LABELS)

    result = {}
    for i, year in enumerate(YEARS):
        pop = population[year]
        year_counts = values[i * n_crimes : (i + 1) * n_crimes]
        events = []
        for label, count in zip(CRIME_LABELS, year_counts):
            prob = count / pop
            events.append({"label": label, "count": count, "probability": prob})
        result[year] = events
        print(f"{year}: {[e['count'] for e in events]}")

    return result


if __name__ == "__main__":
    result = compute_probabilities("data/crimes_raw.json", "data/population.json")

    with open("data/processed.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\nSaved to data/processed.json")
