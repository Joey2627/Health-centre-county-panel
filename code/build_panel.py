"""Build the county-year panel for Essay 1 (Model 1A) from the raw public files.

Reads only data/raw/. Writes data/derived/county_year_panel.csv,
data/derived/health_center_sites_clean.csv and output/coverage_by_year.csv.
"""
import io
import zipfile

import pandas as pd

import config
import paths


def num(s):
    """Public files mark suppressed or missing cells with '*', '.' or blanks."""
    s = s.astype(str).str.replace(",", "", regex=False).str.replace("%", "", regex=False).str.strip()
    return pd.to_numeric(s.where(~s.isin(["*", ".", "", "nan", "NaN"])), errors="coerce")


def county_universe():
    """Counties in the outcome series: 50 states and DC, minus dropped states."""
    keep = ["statecode", "countycode", "county", "state", "measurename", "yearspan", "rawvalue"]
    parts = []
    for ch in pd.read_csv(paths.CHR_TRENDS, dtype=str, usecols=keep, chunksize=200_000, encoding="latin-1"):
        parts.append(ch[(ch.measurename == "Preventable hospital stays") & (ch.countycode != "000")])
    chr_ = pd.concat(parts)
    chr_["fips"] = chr_.statecode + chr_.countycode
    chr_ = chr_[(chr_.statecode <= config.STATE_FIPS_MAX) & ~chr_.statecode.isin(config.DROP_STATES)]
    chr_["year"] = chr_.yearspan.astype(int)
    chr_["prev_hosp_stays"] = num(chr_.rawvalue)
    names = chr_.drop_duplicates("fips")[["fips", "state", "county"]]
    return names, chr_[["fips", "year", "prev_hosp_stays"]]


def sites():
    """Active permanent health-center sites, one row per site, with the year added to scope."""
    d = pd.read_csv(paths.HRSA_SITES, dtype=str, low_memory=False)
    d = d.rename(columns={
        "State and County Federal Information Processing Standard Code": "fips",
        "Health Center Location Type Description": "location_type",
        "Health Center Type": "hc_type",
        "Site Added to Scope this Date": "scope_date",
        "Health Center Service Delivery Site Location Setting Description": "setting",
        "Site State Abbreviation": "site_state",
    })
    d["scope_date"] = pd.to_datetime(d.scope_date, errors="coerce")
    d["year_added"] = d.scope_date.dt.year
    cols = ["fips", "site_state", "hc_type", "location_type", "setting", "scope_date", "year_added",
            "Site Name", "Health Center Name"]
    return d[cols]


def medicare():
    """County outcomes and utilization from the Medicare Geographic Variation file (all ages)."""
    keep = {
        "BENES_OM_CNT": "medicare_ffs_benes",
        "MA_PRTCPTN_RATE": "ma_share",
        "IP_CVRD_STAYS_PER_1000_BENES": "ip_stays_per_1000",
        "ER_VISITS_PER_1000_BENES": "er_visits_per_1000",
        "FQHC_RHC_VISITS_PER_1000_BENES": "fqhc_rhc_visits_per_1000",
        "ACUTE_HOSP_READMSN_PCT": "readmission_pct",
        "IP_MDCR_STDZD_PYMT_PC": "ip_std_pay_pc",
        "TOT_MDCR_STDZD_PYMT_PC": "total_std_pay_pc",
    }
    d = pd.read_csv(paths.CMS_GV, dtype=str, low_memory=False,
                    usecols=["YEAR", "BENE_GEO_LVL", "BENE_GEO_CD", "BENE_AGE_LVL", *keep])
    d = d[(d.BENE_GEO_LVL == "County") & (d.BENE_AGE_LVL == "All")]
    out = pd.DataFrame({"fips": d.BENE_GEO_CD, "year": d.YEAR.astype(int)})
    for src, dst in keep.items():
        out[dst] = num(d[src]).values
    return out


def sahie():
    # The files are large, so rows are filtered line by line before parsing.
    rows = []
    for z in sorted(paths.SAHIE_DIR.glob("sahie-*-csv.zip")):
        keep, header = [], None
        with zipfile.ZipFile(z) as zf, zf.open(zf.namelist()[0]) as fh:
            for raw in io.TextIOWrapper(fh, encoding="latin-1"):
                cells = [c.strip() for c in raw.split(",")]
                if header is None:
                    if raw.startswith("year,version"):
                        header = cells
                    continue
                rec = dict(zip(header, cells))
                if all(rec.get(k) == v for k, v in config.SAHIE_FILTER.items()):
                    keep.append(rec)
        d = pd.DataFrame(keep)
        rows.append(pd.DataFrame({
            "fips": d.statefips + d.countyfips,
            "year": d.year.astype(int),
            "uninsured_pct_u65": num(d.PCTUI),
            "pop_u65": num(d.NIPR),
        }))
    return pd.concat(rows)


def saipe():
    rows = []
    for f in sorted(paths.SAIPE_DIR.glob("est*all.xls")):
        year = 2000 + int(f.stem[3:5])
        # The header row moves between releases; find it by its first cell.
        top = pd.read_excel(f, header=None, nrows=6, dtype=str)
        hdr = top.index[top.iloc[:, 0] == "State FIPS Code"][0]
        d = pd.read_excel(f, header=hdr, dtype=str)
        d = d[d["County FIPS Code"] != "000"]
        rows.append(pd.DataFrame({
            "fips": d["State FIPS Code"] + d["County FIPS Code"],
            "year": year,
            "poverty_pct": num(d["Poverty Percent, All Ages"]),
            "median_hh_income": num(d["Median Household Income"]),
        }))
    return pd.concat(rows)


def rucc():
    d = pd.read_csv(paths.RUCC, dtype=str, encoding="latin-1")
    w = d.pivot_table(index="FIPS", columns="Attribute", values="Value", aggfunc="first")
    out = pd.DataFrame({"fips": w.index, "rucc_2023": num(w["RUCC_2023"]).values,
                        "pop_2020": num(w["Population_2020"]).values})
    out["rural"] = (out.rucc_2023 >= config.RURAL_RUCC_MIN).astype("Int64").where(out.rucc_2023.notna())
    return out


def main():
    names, prev = county_universe()
    panel = pd.MultiIndex.from_product([names.fips, list(config.YEARS)], names=["fips", "year"]).to_frame(index=False)
    panel = panel.merge(names, on="fips", how="left")

    # Health-center sites: counts added each year and cumulative active by year end.
    s = sites()
    s.to_csv(paths.SITES_CLEAN, index=False)
    perm = s[s.location_type.isin(config.SITE_LOCATION_TYPES) & s.year_added.notna()]
    in_univ = perm.fips.isin(names.fips)
    print(f"Permanent sites: {len(perm):,}; in panel counties: {in_univ.sum():,}; "
          f"outside (territories, Connecticut, unmatched): {(~in_univ).sum():,}")
    perm = perm[in_univ]
    added = perm.groupby(["fips", "year_added"]).size().rename("sites_added").reset_index()
    first = perm.groupby("fips").year_added.min().rename("first_site_year").reset_index()

    years = pd.DataFrame({"year": range(int(perm.year_added.min()), max(config.YEARS) + 1)})
    full = names[["fips"]].merge(years, how="cross")
    full = full.merge(added.rename(columns={"year_added": "year"}), on=["fips", "year"], how="left")
    full["sites_added"] = full.sites_added.fillna(0).astype(int)
    full["sites_active"] = full.groupby("fips").sites_added.cumsum()
    panel = panel.merge(full, on=["fips", "year"], how="left")
    panel = panel.merge(first, on="fips", how="left")

    lo, hi = config.ENTRY_WINDOW
    fy = panel.first_site_year
    panel["entry_group"] = pd.cut(fy, [-1, lo - 1, hi, 9999],
                                  labels=[f"Entry before {lo}", f"Entry {lo}-{hi}", f"Entry after {hi}"]).astype(str)
    panel.loc[fy.isna(), "entry_group"] = "No permanent site"
    panel["entry_cohort"] = fy.where(fy.between(lo, hi)).astype("Int64")
    panel["event_time"] = (panel.year - panel.entry_cohort).astype("Int64")

    for part in (prev, medicare(), sahie(), saipe()):
        panel = panel.merge(part, on=["fips", "year"], how="left")
    panel = panel.merge(rucc(), on="fips", how="left")
    panel["sites_per_100k_2020"] = panel.sites_active / panel.pop_2020 * 1e5

    panel = panel.sort_values(["fips", "year"])
    panel.to_csv(paths.PANEL, index=False)
    print(f"Panel: {panel.fips.nunique():,} counties x {len(config.YEARS)} years = {len(panel):,} rows -> {paths.rel(paths.PANEL)}")

    value_cols = [c for c in panel.columns if c not in ("fips", "year", "state", "county", "entry_group")]
    cov = panel.groupby("year")[value_cols].count().T
    cov.to_csv(paths.OUTPUT / "coverage_by_year.csv")
    print(f"Coverage table -> {paths.rel(paths.OUTPUT / 'coverage_by_year.csv')}")


if __name__ == "__main__":
    main()
