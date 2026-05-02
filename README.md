# Estonian Crime Probability Scale

A probability scale visualising the likelihood of being a crime victim in Estonia,
built from official Statistics Estonia data.

## What it does

Fetches registered crime counts by type from the Statistics Estonia API (table JS009),
divides by the Estonian population, and plots each crime type as an annual per-person
probability on a logarithmic scale. Produces two types of visualisation:

- **Per-year lollipop charts** - snapshot of all crime type probabilities for a given year
- **Trend line chart** - how probabilities shifted from 2015 to 2021

## Results

### Probability scale (2021)
![Probability scale 2021](output/probability_scale_2021.png)

### Trend over time (2015–2021)
![Trend over time](output/probability_trend.png)

The most common crime by far is theft (~1 in 177 in 2021), followed by assault (~1 in 236).
Murder remains extremely rare (~1 in 190 000). Over the 2015–2021 period, robbery declined
steadily while fraud rose sharply - likely reflecting a broader shift toward online crime.

The COVID-19 period (2020–2021) shows several notable patterns: robbery dropped in 2020,
consistent with reduced street activity during lockdowns. Fraud rose sharply in 2021,
likely reflecting increased online activity. Most strikingly, murder cases nearly doubled in 2020 before returning to baseline. R
Rising from 5 cases in 2019 to 13 in 2020, then back to 7 in 2021. This is possibly linked to increased
domestic violence during lockdowns, though the absolute numbers are so small that a single
digit change produces a dramatic shift on a log scale. This is a known limitation when
working with rare events - interpret with caution.

## Data source

- **Crime data**: [Statistics Estonia JS009](https://andmed.stat.ee/et/stat/JS009)
  - Registered crimes by type and county, 2015–2021
- **Population**: [Statistics Estonia RV0240](https://andmed.stat.ee/et/stat/RV0240)
  - Estonian population by year, fetched programmatically

## Limitations

- Based on reported crimes only. Unreported cases are not captured
  (true probabilities are likely higher due to the dark figure of crime).
- Assumes each reported case involves a unique victim.
- Population used as denominator is total Estonian population, not at-risk subgroups.
- With rare crime types (e.g. murder, ~7 cases/year), small absolute changes
  produce large swings in probability — interpret with caution.

## How to run

Install dependencies:
```bash
pip install requests matplotlib
```

Run in order:
```bash
python fetch_data.py   # fetches crime counts and population from Statistics Estonia API
python process.py      # computes per-person probabilities for each year
python plot.py         # generates per-year lollipop charts → output/probability_scale_YYYY.png
python plot_trend.py   # generates trend line chart → output/probability_trend.png
```

## License

MIT