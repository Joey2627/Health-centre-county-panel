# Raw data

These files are never edited. Code in `code/` reads them and writes everything in `data/derived/` and `output/`.
All files were downloaded on **November 17, 2026**.

| File | Source | Notes |
|---|---|---|
| `hrsa/Health_Center_Service_Delivery_and_LookAlike_Sites.csv` | HRSA Data Warehouse, Health Center Service Delivery and Look-Alike Sites. https://data.hrsa.gov/DataDownload/DD_Files/Health_Center_Service_Delivery_and_LookAlike_Sites.csv | Snapshot dated Nov 16, 2026 (`Data Warehouse Record Create Date`). Active sites only. 19,616 sites. |
| `cms/2014-2024 Original Medicare Geographic Variation Public Use File.csv` | CMS, Medicare Geographic Variation - by National, State & County (data.cms.gov). https://data.cms.gov/sites/default/files/2026-04/cc600d1e-d475-4b0e-80dc-1f64c01ca68c/2014-2024%20Original%20Medicare%20Geographic%20Variation%20Public%20Use%20File.csv | Catalog entry modified May 15, 2026. Years 2014-2024. PQI columns are blank at county level. |
| `chr/chr_trends_csv_2025.csv` | County Health Rankings & Roadmaps, 2025 trends file. https://www.countyhealthrankings.org/sites/default/files/media/document/chr_trends_csv_2025.csv | Preventable hospital stays (measure 5), CMS Mapping Medicare Disparities, 2012-2022, per 100,000 Medicare enrollees. |
| `sahie/sahie-YYYY-csv.zip` (2012-2024) | U.S. Census Bureau, Small Area Health Insurance Estimates. https://www2.census.gov/programs-surveys/sahie/datasets/time-series/estimates-acs/ | |
| `saipe/estYYall.xls` (2012-2024) | U.S. Census Bureau, Small Area Income and Poverty Estimates. https://www2.census.gov/programs-surveys/saipe/datasets/YYYY/YYYY-state-and-county/ | |
| `usda/2023-rural-urban-continuum-codes.csv` | USDA Economic Research Service, 2023 Rural-Urban Continuum Codes. https://www.ers.usda.gov/media/5768/2023-rural-urban-continuum-codes.csv | |
| `geo/geojson-counties-fips.json` | Plotly datasets repository (U.S. Census 2010 county boundaries). https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json | Used only to draw the map. |
