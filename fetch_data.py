import requests
import json

# Statistics Estonia API base URL
API_BASE = "https://andmed.stat.ee/api/v1/et/stat"


def fetch_crime_data():
    """
    Fetch selected crime types for all available years (2006–2021)
    from Statistics Estonia API (JS009).

    Crime type codes (from API metadata):
        6  - tapmine (manslaughter)
        7  - mõrv (murder)
        9  - kehaline väärkohtlemine (assault)
        17 - vargus (theft)
        18 - röövimine (robbery)
        20 - kelmus (fraud)
        35 - liikluskuritegu (traffic crime)

    Maakond code '00' = Kogu Eesti (all of Estonia).
    """
    url = f"{API_BASE}/JS009"

    query = {
        "query": [
            {
                "code": "Aasta",
                "selection": {"filter": "all", "values": ["*"]}
            },
            {
                "code": "Kuriteo aste/liik",
                "selection": {
                    "filter": "item",
                    "values": ["6", "7", "9", "17", "18", "20", "35"]
                }
            },
            {
                "code": "Maakond",
                "selection": {"filter": "item", "values": ["00"]}
            }
        ],
        "response": {"format": "json-stat2"}
    }

    r = requests.post(url, json=query)
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    data = fetch_crime_data()

    with open("data/crimes_raw.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Saved to data/crimes_raw.json")
    print("Values:", data["value"])
