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
                "selection": {"filter": "item",
                              "values": ["2015","2016","2017","2018","2019","2020","2021"]}
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

def fetch_population() -> dict:
    """
    Fetch total Estonian population per year (2015–2021) from Statistics Estonia API (RV0240).

    Returns a dict mapping year strings to population counts.
    Sugu code '1' = Mehed ja naised (all genders), Elukoht '00' = Kogu Eesti (all of Estonia),
    Vanus '000' = Kokku (total).
    """
    url = f"{API_BASE}/RV0240"

    query = {
        "query": [
            {"code": "Sugu", "selection": {"filter": "item", "values": ["1"]}},
            {"code": "Elukoht", "selection": {"filter": "item", "values": ["00"]}},
            {"code": "Vanus", "selection": {"filter": "item", "values": ["000"]}},
            {"code": "Aasta", "selection": {"filter": "item",
                "values": ["2015","2016","2017","2018","2019","2020","2021"]}}
        ],
        "response": {"format": "json-stat2"}
    }

    r = requests.post(url, json=query)
    r.raise_for_status()
    data = r.json()

    years = ["2015","2016","2017","2018","2019","2020","2021"]
    return {year: value for year, value in zip(years, data["value"])}

if __name__ == "__main__":
    data = fetch_crime_data()
    population = fetch_population()

    with open("data/crimes_raw.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open("data/population.json", "w", encoding="utf-8") as f:
        json.dump(population, f, ensure_ascii=False, indent=2)

    print("Saved crimes_raw.json and population.json")
