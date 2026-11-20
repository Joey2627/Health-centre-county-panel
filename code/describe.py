"""Descriptive tables and figures for the Essay 1 data memo.

Reads data/derived/county_year_panel.csv. Writes tables (CSV) and figures (PNG)
to output/. Everything here is descriptive; no estimate is causal.
"""
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

import config
import paths

lo, hi = config.ENTRY_WINDOW
GROUPS = [f"Entry before {lo}", f"Entry {lo}-{hi}", f"Entry after {hi}", "No permanent site"]
COLORS = dict(zip(GROUPS, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]))
STYLES = dict(zip(GROUPS, ["-", "--", "-.", ":"]))
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"

plt.rcParams.update({
    "font.family": "Arial", "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
})


def load():
    return pd.read_csv(paths.PANEL, dtype={"fips": str})


def baseline_table(p):
    """County characteristics before the entry window, by entry group."""
    b13 = p[p.year == lo - 1].set_index("fips")
    b14 = p[p.year == lo].set_index("fips")  # first Medicare year
    rows = {}
    for g in GROUPS:
        ids = b13.index[b13.entry_group == g]
        x13, x14 = b13.loc[ids], b14.loc[ids]
        rows[g] = {
            "Counties": len(ids),
            "Rural (%)": 100 * x13.rural.mean(),
            "Population, 2020 (median)": x13.pop_2020.median(),
            f"Preventable hospital stays per 100,000 Medicare enrollees, {lo - 1}": x13.prev_hosp_stays.mean(),
            f"Uninsured, under 65 (%), {lo - 1}": x13.uninsured_pct_u65.mean(),
            f"Poverty (%), {lo - 1}": x13.poverty_pct.mean(),
            f"Median household income ($), {lo - 1}": x13.median_hh_income.mean(),
            f"Medicare inpatient stays per 1,000, {lo}": x14.ip_stays_per_1000.mean(),
            f"Medicare FQHC/RHC visits per 1,000, {lo}": x14.fqhc_rhc_visits_per_1000.mean(),
        }
    t = pd.DataFrame(rows)
    t.to_csv(paths.OUTPUT / "table1_baseline_by_entry_group.csv")
    return t


def cohort_table(p):
    """Counties whose first permanent site arrives in each year of the window."""
    c = p[p.year == lo].dropna(subset=["entry_cohort"])
    t = c.groupby("entry_cohort").agg(counties=("fips", "size"), rural=("rural", "sum")).astype(int)
    t["sites added nationally (panel counties)"] = p[p.year.between(lo, hi)].groupby("year").sites_added.sum().values
    t.index = t.index.astype(int)
    t.loc["Total"] = t.sum()
    t.to_csv(paths.OUTPUT / "table2_entry_cohorts.csv")
    return t


def albers(lon, lat, lon0=-96.0, lat0=23.0, lat1=29.5, lat2=45.5):
    """Albers equal-area conic projection (contiguous U.S.)."""
    r = math.radians
    n = (math.sin(r(lat1)) + math.sin(r(lat2))) / 2
    c = math.cos(r(lat1)) ** 2 + 2 * n * math.sin(r(lat1))
    rho0 = math.sqrt(c - 2 * n * math.sin(r(lat0))) / n
    lon, lat = np.radians(np.asarray(lon) - lon0), np.radians(np.asarray(lat))
    rho = np.sqrt(c - 2 * n * np.sin(lat)) / n
    return rho * np.sin(n * lon), rho0 - rho * np.cos(n * lon)


def entry_map(p):
    geo = json.loads((paths.RAW / "geo" / "geojson-counties-fips.json").read_text(encoding="latin-1"))
    group = p[p.year == lo].set_index("fips").entry_group
    polys, colors = [], []
    for f in geo["features"]:
        fips = f["properties"]["STATE"] + f["properties"]["COUNTY"]
        if fips[:2] in ("02", "15", "72") or fips[:2] > "56":
            continue  # contiguous states only
        g = group.get(fips)
        color = COLORS.get(g, "#d9d8d4")
        geom = f["geometry"]
        rings = [geom["coordinates"][0]] if geom["type"] == "Polygon" else [pg[0] for pg in geom["coordinates"]]
        for ring in rings:
            a = np.asarray(ring)
            x, y = albers(a[:, 0], a[:, 1])
            polys.append(np.column_stack([x, y]))
            colors.append(color)
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.add_collection(PolyCollection(polys, facecolors=colors, edgecolors=SURFACE, linewidths=0.15))
    ax.autoscale_view()
    ax.set_aspect("equal")
    ax.axis("off")
    counts = group.value_counts()
    handles = [Patch(facecolor=COLORS[g], label=f"{g} ({counts.get(g, 0):,})") for g in GROUPS]
    handles.append(Patch(facecolor="#d9d8d4", label="Not in panel (Connecticut)"))
    ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=8, labelcolor=INK)
    ax.set_title("Year of each county's first permanent health-center site", loc="left", color=INK, fontsize=11)
    fig.text(0.01, 0.01, "Source: HRSA Health Center Service Delivery Sites (active sites, Nov 16, 2026). "
             "Contiguous states shown; Alaska and Hawaii are in the panel.", fontsize=7, color=INK2)
    out = paths.OUTPUT / "fig1_entry_map.png"
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return out


def trends(p):
    """Mean preventable hospital stays by year and entry group (raw means)."""
    d = p[p.year.between(2012, 2022)]
    m = d.groupby(["entry_group", "year"]).prev_hosp_stays.mean().unstack(0)[GROUPS]
    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    for g in GROUPS:
        ax.plot(m.index, m[g], color=COLORS[g], ls=STYLES[g], lw=2, label=g)
    ax.axvspan(lo - 0.5, hi + 0.5, color=GRID, alpha=0.5, lw=0)
    ax.text(lo - 0.3, ax.get_ylim()[1], "Entry window", color=INK2, fontsize=8, va="top")
    ax.set_xlim(2011.6, 2022.4)
    ax.set_xticks(range(2012, 2023, 2))
    ax.yaxis.grid(True, color=GRID, lw=0.8)
    ax.set_ylabel("Per 100,000 Medicare enrollees")
    ax.legend(frameon=False, fontsize=8, loc="lower left", labelcolor=INK)
    ax.set_title("Preventable hospital stays by entry group, 2012-2022 (county means)", loc="left", color=INK, fontsize=11)
    fig.text(0.01, -0.02, "Source: County Health Rankings trends file (CMS Mapping Medicare Disparities); HRSA sites.",
             fontsize=7, color=INK2)
    out = paths.OUTPUT / "fig2_trends_by_entry_group.png"
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)
    m.round(0).to_csv(paths.OUTPUT / "fig2_data.csv")
    return out


def event_profile(p, col, label, fname, window=(-5, 7)):
    """Entry counties' outcome relative to same-year mean of counties with no site, by years since entry.

    Normalized to zero in the year before entry. Descriptive only: no controls,
    no adjustment for staggered timing.
    """
    ref = p[p.entry_group == "No permanent site"].groupby("year")[col].mean()
    e = p.dropna(subset=["entry_cohort", col]).copy()
    e["gap"] = e[col] - e.year.map(ref)
    e = e[e.event_time.between(*window)]
    s = e.groupby("event_time").gap.agg(["mean", "sem", "count"])
    s["mean"] -= s.loc[-1, "mean"]
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    ax.axhline(0, color=INK2, lw=0.8)
    ax.axvline(-0.5, color=INK2, lw=0.8, ls=":")
    ax.fill_between(s.index, s["mean"] - 1.96 * s["sem"], s["mean"] + 1.96 * s["sem"], color="#86b6ef", alpha=0.35, lw=0)
    ax.plot(s.index, s["mean"], color="#2a78d6", lw=2, marker="o", ms=4)
    ax.yaxis.grid(True, color=GRID, lw=0.8)
    ax.set_xticks(range(window[0], window[1] + 1))
    ax.set_xlabel("Years since the county's first permanent health-center site")
    ax.set_ylabel(label)
    ax.set_title(f"{label}: entry counties minus counties with no site", loc="left", color=INK, fontsize=10.5)
    fig.text(0.01, -0.04, "Raw difference from the same-year mean of counties with no site, set to zero in the year before entry; "
             "band = 95% interval of the mean. Descriptive, not a causal estimate.", fontsize=7, color=INK2)
    out = paths.OUTPUT / fname
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)
    s.round(2).to_csv(out.with_suffix(".csv"))
    return out, s


def main():
    p = load()
    t1 = baseline_table(p)
    t2 = cohort_table(p)
    print(t1.round(1).to_string(), "\n")
    print(t2.to_string(), "\n")
    for out in (entry_map(p), trends(p)):
        print("wrote", paths.rel(out))
    for col, label, fname in [
        ("fqhc_rhc_visits_per_1000", "Medicare FQHC/RHC visits per 1,000", "fig3_event_fqhc_visits.png"),
        ("prev_hosp_stays", "Preventable stays per 100,000", "fig4_event_preventable_stays.png"),
    ]:
        out, s = event_profile(p, col, label, fname)
        print("wrote", paths.rel(out))
        print(s.round(1).to_string(), "\n")


if __name__ == "__main__":
    main()
