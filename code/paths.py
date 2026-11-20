"""Folder locations for the Essay 1 project. Every script takes its paths from here."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"
OUTPUT = ROOT / "output"

HRSA_SITES = RAW / "hrsa" / "Health_Center_Service_Delivery_and_LookAlike_Sites.csv"
CMS_GV = RAW / "cms" / "2014-2024 Original Medicare Geographic Variation Public Use File.csv"
CHR_TRENDS = RAW / "chr" / "chr_trends_csv_2025.csv"
SAHIE_DIR = RAW / "sahie"
SAIPE_DIR = RAW / "saipe"
RUCC = RAW / "usda" / "2023-rural-urban-continuum-codes.csv"

PANEL = DERIVED / "county_year_panel.csv"
SITES_CLEAN = DERIVED / "health_center_sites_clean.csv"


def rel(p):
    """Path relative to the project folder, for printing."""
    return Path(p).resolve().relative_to(ROOT).as_posix()
