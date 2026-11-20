# Health-Center Sites and Preventable Hospital Use: U.S. County-Year Panel, 2012–2024

Code that builds a linked county-year dataset for research on where new federally funded health-center sites reduce preventable hospital use and Medicare spending. It is the data foundation for the first essay of my Ph.D. dissertation in economics at Kansas State University ("Model 1A").

**Author:** Joseph Olarewaju Afolabi, Department of Economics, Kansas State University · ORCID [0000-0002-7752-1459](https://orcid.org/0000-0002-7752-1459)

## Status

- **Done (November 2026):** county-year panel for 3,136 counties, 2012–2024 (40,768 rows), linking health-center site openings to preventable hospital stays, Medicare utilization and spending, insurance coverage, poverty, income and rurality. Descriptive statistics only.
- **Next (Spring 2027):** event-study estimates of the effect of a county's first permanent health-center site, using the Callaway–Sant'Anna estimator with not-yet-treated counties as controls, pre-trend tests, and county-level effects for a site-targeting model.

## Research question

Does opening a county's first permanent federally funded health-center site lower preventable hospital stays and Medicare spending, and in which counties is the effect largest? The answer feeds a site-targeting model that ranks counties by the hospital cost a new site would avoid.

## Data

All inputs are free and public. Raw files are not stored in this repository; [data/raw/README.md](data/raw/README.md) lists each file, where to download it, and where to put it.

| Source | Used for |
|---|---|
| HRSA Health Center Service Delivery and Look-Alike Sites | Site locations and the date each site was added to scope |
| County Health Rankings trends file (from CMS Mapping Medicare Disparities) | Preventable hospital stays per 100,000 Medicare enrollees, 2012–2022 |
| CMS Medicare Geographic Variation public use file | Medicare utilization and standardized spending, 2014–2024 |
| Census Small Area Health Insurance Estimates (SAHIE) | Uninsured rate under 65 |
| Census Small Area Income and Poverty Estimates (SAIPE) | Poverty rate, median household income |
| USDA ERS 2023 Rural-Urban Continuum Codes | Rurality |

## Project layout

- `code/paths.py` holds every path; `code/config.py` holds every construction choice (years, which sites count as treatment, entry window, rural cutoff, geography), each explained in comments.
- `data/raw/` is never edited; its README records each file's source and download date.
- `data/derived/` and `output/` are written only by code.

## How to run

Requires Python 3.10 or later. From the `code/` folder:

```
pip install -r ../requirements.txt
python build_panel.py   # data/raw -> data/derived/county_year_panel.csv
python describe.py      # data/derived -> output/ tables and figures
```

`build_panel.py` writes the panel (variables in [docs/codebook.md](docs/codebook.md)), a cleaned file with one row per health-center site, and `output/coverage_by_year.csv` (non-missing counts by variable and year). `describe.py` writes the descriptive tables and figures in `output/`:

- `table1_baseline_by_entry_group.csv`: baseline county characteristics by entry group
- `table2_entry_cohorts.csv`: counties entering in each year, 2014–2022
- `fig1_entry_map.png`: year of each county's first permanent site
- `fig2_trends_by_entry_group.png`: preventable hospital stays over time, by entry group
- `fig3_event_fqhc_visits.png`, `fig4_event_preventable_stays.png`: entry counties' difference from the same-year mean of counties with no site, by years since entry, set to zero in the year before entry (descriptive only: no controls and no adjustment for staggered timing)

The derived data files are not stored in the repository; running the two scripts rebuilds them.

## Construction choices and known limitations

- **Treatment** is a county's first *permanent* site; mobile and seasonal sites are excluded. Entry cohorts are 2014–2022, leaving at least two pre-entry years.
- **Active sites only.** The HRSA file lists sites operating at download. Sites that later closed are missing; site histories will be rebuilt from archived HRSA files.
- **"Added to scope"** is the date HRSA approved a site, which can differ from when it began serving patients.
- **Medicare population.** Outcomes are measured for Medicare enrollees; health centers mainly serve Medicaid and uninsured patients.
- **Connecticut is excluded**, because HRSA codes it by the 2022 planning regions while the outcome series uses the former counties.
- Raw descriptive comparisons are not causal: counties that gained a site were already improving before entry, which the event-study design addresses.

## License and citation

Code is released under the MIT License (see [LICENSE](LICENSE)). If you use it, please cite it as shown in [CITATION.cff](CITATION.cff).
