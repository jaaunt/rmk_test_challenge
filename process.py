import json

# Estonian population in 2021 (source: Statistics Estonia RV0240)
# hardcoded for now
POPULATION_2021 = 1_331_824

# Crime type labels in the same order as the API returns values
# (matches the order of crime codes defined in fetch_data.py)
CRIME_LABELS = [
    "Tapmine",
    "Mõrv",
    "Kehaline väärkohtlemine",
    "Vargus",
    "Röövimine",
    "Kelmus",
    "Liikluskuritegu",
]

def compute_probabilities(raw_path: str) -> list[dict]:
    """
    Compute annual per-person probability for each crime type.

    Method: probability = reported_cases / population

    Assumptions and limitations:
    - Assumes each reported case involves a unique victim (may underestimate
      true probability if one person is victimised multiple times)
    - Based on reported crimes only — unreported cases are not captured
      (true probability is likely higher)
    - Population used as denominator is total Estonian population,
      not at-risk subgroups
    """
    with open(raw_path, encoding="utf-8") as f:
        data = json.load(f)

    counts = data["value"]

    events = []
    for label, count in zip(CRIME_LABELS, counts):
        prob = count / POPULATION_2021
        events.append({"label": label, "count": count, "probability": prob})
        print(f"{label}: {count} cases, probability p = {prob:.6f}")

    return events

if __name__ == "__main__":
    events = compute_probabilities("data/crimes_raw.json")

    with open("data/processed.json", "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

    print("\nSaved to data/processed.json")
