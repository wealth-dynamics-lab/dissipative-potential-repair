# Data Directory

This directory contains all data files used in the empirical analysis.

---

## File List

### 1. 40-country 2024 wealth inequality40国2024年不平等财富数据.csv

Cross-sectional data for 2024, containing 40 countries.

Columns:

- `country`: ISO 3166-1 alpha-3 country code
- `epsilon`: absolute abundance coefficient
- `CRJ`: Capital Return-Justice Ratio (Top 10% / Bottom 50% wealth share)

Source: World Inequality Report 2026 Country Sheets (published November 2025).

### 2. codeWID_Data_WID raw panel data (50 countries, 1995-2023)（50国1995-2003年数据）.csv

Panel data for 50 countries, spanning 1995-2023.

This file was downloaded from the World Inequality Database (WID) on
21 April 2026 at 16:31:12.

Columns include:

- `p90p100`: Top 10% wealth share, by country and year
- `p0p50`: Bottom 50% wealth share, by country and year
- `p99p100`: Top 1% wealth share, by country and year

The file uses WID's standard wide-format structure. Each column header
contains the variable name and country code (e.g., `shweal_z_US` for
US data).

---

## Data Sources

All data are publicly available from the following sources:

- World Inequality Database (WID): https://wid.world
- World Inequality Report 2026: https://wir2026.wid.world

---

## Usage Notes

1. All data users must comply with the open-access terms specified on
   the WID website (https://wid.world).

2. When using these data in research, please cite the original sources:

   - WID 2026: World Inequality Database, 2026 Release.
   - WIR 2026: World Inequality Lab (2026). World Inequality Report 2026.

3. For the cleaned panel dataset (long format, 40 countries, 1990-2024),
   see the data processing scripts in `code/01_data_cleaning.py`.
