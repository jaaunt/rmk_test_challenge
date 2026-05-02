import requests
import json

# Statistics Estonia API base URL
API_BASE = "https://andmed.stat.ee/api/v1/et/stat"

YEARS = ["2015", "2016", "2017", "2018", "2019", "2020", "2021"]


def _year_query(year_code: str = "Aasta") -> dict:
    """Build the standard year-filter clause used in all queries."""
    return {"code": year_code, "selection": {"filter": "item", "values": YEARS}}


def _post(table: str, query: dict) -> dict:
    """POST a query to the API and return parsed JSON, with a helpful error on failure."""
    url = f"{API_BASE}/{table}"
    r = requests.post(url, json=query)
    if not r.ok:
        raise requests.HTTPError(
            f"{r.status_code} from {table}: {r.text[:500]}", response=r
        )
    return r.json()


def fetch_crime_data() -> dict:
    """
    Fetch selected crime types for all available years (2015–2021)
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
    return _post("JS009", {
        "query": [
            _year_query(),
            {
                "code": "Kuriteo aste/liik",
                "selection": {"filter": "item", "values": ["6", "7", "9", "17", "18", "20", "35"]},
            },
            {"code": "Maakond", "selection": {"filter": "item", "values": ["00"]}},
        ],
        "response": {"format": "json-stat2"},
    })


def fetch_population() -> dict:
    """
    Fetch total Estonian population per year (2015–2021) from Statistics Estonia API (RV0240).

    Returns a dict mapping year strings to population counts.
    Sugu '1' = all genders, Elukoht '00' = all of Estonia, Vanus '000' = total.
    """
    data = _post("RV0240", {
        "query": [
            {"code": "Sugu",    "selection": {"filter": "item", "values": ["1"]}},
            {"code": "Elukoht", "selection": {"filter": "item", "values": ["00"]}},
            {"code": "Vanus",   "selection": {"filter": "item", "values": ["000"]}},
            _year_query(),
        ],
        "response": {"format": "json-stat2"},
    })
    return {year: value for year, value in zip(YEARS, data["value"])}


def fetch_births_and_deaths() -> tuple[dict, dict]:
    """
    Fetch live births and deaths per year (2015–2021) from Statistics Estonia API (RV030).

    RV030 covers 'Sünnid, surmad ja loomulik iive' (births, deaths, natural increase).
    Dimension codes verified from API metadata:
        Näitaja '1' = Elussünnid (live births)
        Näitaja '2' = Surmad (deaths)
    No Sugu or Maakond dimension exists in this table.

    Returns two dicts: (births, deaths), each mapping year strings to counts.
    """
    data = _post("RV030", {
        "query": [
            {
                "code": "Näitaja",
                "selection": {"filter": "item", "values": ["1", "2"]},
            },
            _year_query(),
        ],
        "response": {"format": "json-stat2"},
    })
    # The API returns values flat: [births_2015, ..., births_2021, deaths_2015, ..., deaths_2021]
    values = data["value"]
    n = len(YEARS)
    births = {year: values[i]     for i, year in enumerate(YEARS)}
    deaths = {year: values[n + i] for i, year in enumerate(YEARS)}
    return births, deaths


if __name__ == "__main__":
    print("Fetching crime data...")
    crimes = fetch_crime_data()
    with open("data/crimes_raw.json", "w", encoding="utf-8") as f:
        json.dump(crimes, f, ensure_ascii=False, indent=2)

    print("Fetching population...")
    population = fetch_population()
    with open("data/population.json", "w", encoding="utf-8") as f:
        json.dump(population, f, ensure_ascii=False, indent=2)

    print("Fetching births and deaths...")
    births, deaths = fetch_births_and_deaths()
    with open("data/births.json", "w", encoding="utf-8") as f:
        json.dump(births, f, ensure_ascii=False, indent=2)
    with open("data/deaths.json", "w", encoding="utf-8") as f:
        json.dump(deaths, f, ensure_ascii=False, indent=2)

    print("Done - saved all raw data to data/")
