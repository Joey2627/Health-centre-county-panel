# Codebook: `data/derived/county_year_panel.csv`

One row per county and year: 3,136 counties, 2012–2024, 40,768 rows.

| Variable | Definition | Source |
|---|---|---|
| `fips`, `state`, `county` | Five-digit county FIPS code; state; county name | CHR |
| `year` | Calendar year, 2012–2024 | |
| `sites_added` | Permanent health-center sites added to scope in the county that year | HRSA |
| `sites_active` | Cumulative permanent sites by year end (active sites only) | HRSA |
| `first_site_year` | Year the county's first permanent site was added | HRSA |
| `entry_group` | Entry before 2014; entry 2014–2022; entry after 2022; no permanent site | HRSA |
| `entry_cohort`, `event_time` | Entry year for 2014–2022 entrants; year minus entry year | HRSA |
| `prev_hosp_stays` | Preventable hospital stays per 100,000 Medicare enrollees (2012–2022) | CHR (CMS MMD) |
| `medicare_ffs_benes`, `ma_share` | Original Medicare beneficiaries; Medicare Advantage share (2014–2024) | CMS GV |
| `ip_stays_per_1000`, `er_visits_per_1000` | Medicare inpatient stays and ER visits per 1,000 beneficiaries | CMS GV |
| `fqhc_rhc_visits_per_1000` | Medicare FQHC and rural health clinic visits per 1,000 beneficiaries | CMS GV |
| `readmission_pct` | Acute hospital readmission rate (%) | CMS GV |
| `ip_std_pay_pc`, `total_std_pay_pc` | Standardized Medicare inpatient and total spending per capita ($) | CMS GV |
| `uninsured_pct_u65`, `pop_u65` | Uninsured rate (%) and population, under 65 | SAHIE |
| `poverty_pct`, `median_hh_income` | Poverty rate (%), all ages; median household income ($) | SAIPE |
| `rucc_2023`, `rural`, `pop_2020` | Rural-Urban Continuum Code; rural = codes 4–9; 2020 population | USDA ERS |
| `sites_per_100k_2020` | Active permanent sites per 100,000 residents (2020 population) | Derived |

Sources: CHR = County Health Rankings trends file; CMS MMD = CMS Mapping Medicare Disparities; CMS GV = CMS Medicare Geographic Variation public use file; SAHIE = Census Small Area Health Insurance Estimates; SAIPE = Census Small Area Income and Poverty Estimates; USDA ERS = U.S. Department of Agriculture, Economic Research Service.
