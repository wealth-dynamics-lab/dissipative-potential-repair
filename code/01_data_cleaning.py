"""
============================================================================
01_data_cleaning.py
Data Cleaning and Panel Construction
============================================================================

This module performs:
  1. Loading and merging multi-source raw data
  2. Missing value imputation and outlier detection
  3. Construction of derived variables (M, C, R, Phi)

Data Sources:
  - WID 2026 (World Inequality Database) - wealth share data
  - WGI (Worldwide Governance Indicators) - institutional quality indices
  - Edelman Trust Barometer 2025 - social trust index
  - Penn World Table 10.0 - macroeconomic variables
  - Chetty et al. (2014) - intergenerational mobility

Author: Baowei Mi
License: MIT License
============================================================================
"""

import numpy as np
import pandas as pd
from scipy import stats


def load_wid_data(filepath):
    """
    Load WID wealth share data.
    
    Parameters:
        filepath: path to WID raw CSV file
    
    Returns:
        DataFrame with columns: country, year, top10_share, bottom50_share, top1_share
    """
    df = pd.read_csv(filepath)
    
    df = df[df['variable'].isin(['shweal.p90p100', 'shweal.p0p50', 'shweal.p99p100'])]
    
    df_wide = df.pivot_table(
        index=['country', 'year'],
        columns='variable',
        values='value'
    ).reset_index()
    
    df_wide.columns = ['country', 'year', 'bottom50_share', 'top1_share', 'top10_share']
    
    return df_wide


def load_wgi_data(filepath):
    """
    Load WGI institutional quality indices.
    
    Returns:
        DataFrame with columns: country, year, RoL, RQ
    """
    df = pd.read_csv(filepath)
    
    df_rol = df[df['indicator'] == 'RL.EST'][['country', 'year', 'value']]
    df_rol.columns = ['country', 'year', 'RoL']
    
    df_rq = df[df['indicator'] == 'RQ.EST'][['country', 'year', 'value']]
    df_rq.columns = ['country', 'year', 'RQ']
    
    df_wgi = pd.merge(df_rol, df_rq, on=['country', 'year'], how='outer')
    
    return df_wgi


def load_edelman_data(filepath):
    """
    Load Edelman Trust Barometer social trust index.
    
    Returns:
        DataFrame with columns: country, year, trust_index
    """
    df = pd.read_csv(filepath)
    df = df[['country', 'year', 'trust_index']].copy()
    return df


def load_pwt_data(filepath):
    """
    Load Penn World Table macroeconomic variables.
    
    Returns:
        DataFrame with columns: country, year, GFCF, GDP, GDP_deflator
    """
    df = pd.read_csv(filepath)
    df = df[['country', 'year', 'cgdpo', 'csh_i', 'pl_gdpo']].copy()
    df.columns = ['country', 'year', 'GDP', 'investment_share', 'GDP_deflator']
    df['GFCF'] = df['GDP'] * df['investment_share']
    return df


def load_chetty_data(filepath):
    """
    Load Chetty et al. (2014) intergenerational mobility data.
    
    Returns:
        DataFrame with columns: country, intergen_mobility
    """
    df = pd.read_csv(filepath)
    df = df[['country', 'intergen_mobility']].copy()
    return df


def merge_all_sources(wid_path, wgi_path, edelman_path, pwt_path, chetty_path):
    """
    Merge all data sources into a unified panel.
    
    Parameters:
        wid_path:     path to WID data file
        wgi_path:     path to WGI data file
        edelman_path: path to Edelman data file
        pwt_path:     path to PWT data file
        chetty_path:  path to Chetty data file
    
    Returns:
        DataFrame: merged panel data
    """
    df_wid = load_wid_data(wid_path)
    df_wgi = load_wgi_data(wgi_path)
    df_edelman = load_edelman_data(edelman_path)
    df_pwt = load_pwt_data(pwt_path)
    df_chetty = load_chetty_data(chetty_path)
    
    df = df_wid.merge(df_wgi, on=['country', 'year'], how='left')
    df = df.merge(df_edelman, on=['country', 'year'], how='left')
    df = df.merge(df_pwt, on=['country', 'year'], how='left')
    df = df.merge(df_chetty, on=['country'], how='left')
    
    df = df.sort_values(['country', 'year']).reset_index(drop=True)
    
    return df


def handle_missing_values(df):
    """
    Handle missing values: linear interpolation.
    
    Parameters:
        df: raw panel data
    
    Returns:
        DataFrame with missing values handled
    """
    df = df.copy()
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    for col in numeric_cols:
        if col in ['country', 'year']:
            continue
        df[col] = df.groupby('country')[col].transform(
            lambda x: x.interpolate(method='linear', limit=3)
        )
    
    for col in numeric_cols:
        if df[col].isna().sum() > 0:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
    
    return df


def detect_outliers(df, method='mad', threshold=3.0):
    """
    Detect outliers using Median Absolute Deviation (MAD) method.
    
    Parameters:
        df:        panel data
        method:    detection method ('mad' or 'zscore')
        threshold: threshold multiplier
    
    Returns:
        DataFrame with outlier flags and clipped values
    """
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in ['country', 'year']]
    
    for col in numeric_cols:
        if method == 'mad':
            median_val = df[col].median()
            mad_val = np.median(np.abs(df[col] - median_val))
            if mad_val == 0:
                continue
            modified_zscore = 0.6745 * (df[col] - median_val) / mad_val
            df[f'{col}_outlier'] = np.abs(modified_zscore) > threshold
            df[col] = df[col].clip(
                lower=median_val - threshold * mad_val / 0.6745,
                upper=median_val + threshold * mad_val / 0.6745
            )
        elif method == 'zscore':
            zscore = np.abs(stats.zscore(df[col], nan_policy='omit'))
            df[f'{col}_outlier'] = zscore > threshold
            mean_val = df[col].mean()
            std_val = df[col].std()
            df[col] = df[col].clip(
                lower=mean_val - threshold * std_val,
                upper=mean_val + threshold * std_val
            )
    
    return df


def construct_derived_variables(df):
    """
    Construct derived variables.
    
    Parameters:
        df: panel data
    
    Returns:
        DataFrame with derived variables
    """
    df = df.copy()
    
    # CRJ intensity (Top 10% / Bottom 50%)
    df['CRJ'] = df['top10_share'] / df['bottom50_share']
    
    # M: material capital (trillion 2017 constant USD)
    df['M'] = (df['GFCF'] / df['GDP_deflator']) * 1e-12
    
    # C: effective circulation velocity
    df['C'] = 0.25 * (0.6 * df.get('private_credit_GDP', 0.8) +
                      0.4 * df.get('capital_inflows_GDP', 0.05))
    
    # R: geometric friction (reverse-coded WGI)
    df['R'] = 1.0 - (df['RoL'] + df['RQ']) / 2.0
    df['R'] = df['R'].clip(0, 1)
    
    # Phi: information structure pole
    crj_max = df['CRJ'].max()
    df['Phi'] = (df['CRJ'] / crj_max) * (1.0 + df.get('gini_education', 0.3))
    
    return df


def clean_and_construct(wid_path, wgi_path, edelman_path, pwt_path, chetty_path):
    """
    Complete data cleaning and variable construction pipeline.
    
    Parameters:
        wid_path:     path to WID data file
        wgi_path:     path to WGI data file
        edelman_path: path to Edelman data file
        pwt_path:     path to PWT data file
        chetty_path:  path to Chetty data file
    
    Returns:
        DataFrame: cleaned panel data with all derived variables
    """
    print("Step 1/4: Loading and merging multi-source data...")
    df = merge_all_sources(wid_path, wgi_path, edelman_path, pwt_path, chetty_path)
    print(f"  After merge: {df.shape[0]} observations, {df['country'].nunique()} countries")
    
    print("Step 2/4: Handling missing values...")
    df = handle_missing_values(df)
    missing_count = df.isna().sum().sum()
    print(f"  Remaining missing values: {missing_count}")
    
    print("Step 3/4: Detecting and handling outliers...")
    df = detect_outliers(df, method='mad', threshold=3.0)
    outlier_cols = [c for c in df.columns if c.endswith('_outlier')]
    outlier_count = df[outlier_cols].sum().sum() if outlier_cols else 0
    print(f"  Outliers detected: {outlier_count}")
    
    print("Step 4/4: Constructing derived variables...")
    df = construct_derived_variables(df)
    print(f"  Derived variables constructed: M, C, R, Phi, CRJ")
    
    return df


if __name__ == "__main__":
    print("=" * 60)
    print("  Data Cleaning and Panel Construction Module")
    print("=" * 60)
    print()
    print("This module requires actual data files to run.")
    print("Complete data loading and processing pipeline is available in the data/ directory.")
    print()
    print("Available functions:")
    print("  - load_wid_data()              : Load WID wealth share data")
    print("  - load_wgi_data()              : Load WGI institutional quality indices")
    print("  - load_edelman_data()          : Load Edelman social trust index")
    print("  - load_pwt_data()              : Load Penn World Table macro variables")
    print("  - load_chetty_data()           : Load Chetty intergenerational mobility data")
    print("  - merge_all_sources()          : Merge all data sources")
    print("  - handle_missing_values()      : Handle missing values")
    print("  - detect_outliers()            : Detect outliers")
    print("  - construct_derived_variables(): Construct derived variables")
    print("  - clean_and_construct()        : Complete data cleaning pipeline")
