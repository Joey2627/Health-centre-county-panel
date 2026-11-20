"""Choices made in building the Essay 1 panel. Each is reported in the data memo."""

# Panel years. Preventable hospital stays (County Health Rankings trends file)
# cover 2012-2022; the Medicare Geographic Variation file covers 2014-2024.
YEARS = range(2012, 2025)

# Health-center sites counted as treatment: permanent, fixed-location sites.
# Mobile vans and seasonal sites are excluded because they do not establish
# a standing source of primary care in one county.
SITE_LOCATION_TYPES = ["Permanent"]

# Entry cohorts: a county's first permanent site arrives in one of these years.
# The window leaves at least two outcome years before (2012-2013) and the
# outcome series runs to 2022.
ENTRY_WINDOW = (2014, 2022)

# Rural: USDA 2023 Rural-Urban Continuum Codes 4-9 (nonmetropolitan).
RURAL_RUCC_MIN = 4

# SAHIE: uninsured rate for people under 65, all races, both sexes, all incomes.
SAHIE_FILTER = {"geocat": "50", "agecat": "0", "racecat": "0", "sexcat": "0", "iprcat": "0"}

# Geography: the 50 states and DC. Connecticut is dropped because HRSA codes it
# by the 2022 planning regions while the outcome series uses the old counties.
DROP_STATES = ["09"]
STATE_FIPS_MAX = "56"
