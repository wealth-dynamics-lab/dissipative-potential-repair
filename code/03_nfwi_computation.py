"""
============================================================================
03_nfwi_computation.py
Five-Dimensional Early-Warning Matrix (NFWI) Computation
============================================================================

This module performs:
  1. Computation of the Normalized Five-Dimensional Warning Index (NFWI)
  2. Warning level classification (Green / Yellow / Orange / Red)
  3. Batch processing for all 40 countries

Mathematical reference: Equation (7.16) in main text.

Author: Baowei Mi
License: MIT License
============================================================================
"""

import numpy as np
import pandas as pd


def compute_NFWI(rho, tau, CRJ, C_over_M, R_Phi,
                 weights=None, tau_max=None,
                 mean_C_M=None, max_R_Phi=None):
    """
    Compute the Normalized Five-Dimensional Warning Index (NFWI).

    NFWI = w1*(1-rho) + w2*(tau/tau_max) + w3*(CRJ/12.0)
         + w4*|C/M - mean(C/M)| + w5*(R*Phi)/max(R*Phi)

    Parameters:
        rho:       information retention degree, in (0, 1]
        tau:       recovery time (years)
        CRJ:       Capital Return-Justice Ratio (Top10% / Bottom50%)
        C_over_M:  capital circulation efficiency (C / M)
        R_Phi:     information friction intensity (R * Phi)
        weights:   array of five weights (default: equal weights 0.2 each)
        tau_max:   maximum tau for normalization
        mean_C_M:  mean of C/M for normalization
        max_R_Phi: maximum of R*Phi for normalization

    Returns:
        NFWI: float in [0, 1]
    """
    if weights is None:
        weights = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
    if tau_max is None or np.isnan(tau_max):
        tau_max = 16.8
    if mean_C_M is None or np.isnan(mean_C_M):
        mean_C_M = 0.45
    if max_R_Phi is None or np.isnan(max_R_Phi):
        max_R_Phi = 2.8

    norm_rho = 1.0 - rho
    norm_tau = tau / tau_max
    norm_CRJ = CRJ / 12.0
    norm_C_M = abs(C_over_M - mean_C_M)
    norm_R_Phi = R_Phi / max_R_Phi

    x = np.array([norm_rho, norm_tau, norm_CRJ, norm_C_M, norm_R_Phi])
    return float(np.dot(weights, x))


def get_warning_level(NFWI):
    """
    Classify warning level based on NFWI value.

    Parameters:
        NFWI: float in [0, 1]

    Returns:
        tuple: (level_name, label, code)
            level_name: 'Green', 'Yellow', 'Orange', or 'Red'
            label:      'Safe', 'Alert', 'High Risk', or 'Critical'
            code:       1, 2, 3, or 4
    """
    if NFWI < 0.4:
        return ('Green', 'Safe', 1)
    elif NFWI < 0.6:
        return ('Yellow', 'Alert', 2)
    elif NFWI < 0.8:
        return ('Orange', 'High Risk', 3)
    else:
        return ('Red', 'Critical', 4)


def compute_NFWI_for_panel(df, weights=None):
    """
    Compute NFWI and warning levels for the entire panel dataset.

    Parameters:
        df: DataFrame with columns: rho, tau, CRJ, C_over_M, R_Phi
        weights: array of five weights (default: equal weights)

    Returns:
        DataFrame with additional columns: NFWI, Warning_Level, Warning_Label, Warning_Code
    """
    df = df.copy()

    # Compute normalization parameters from the data
    tau_max = df['tau'].max()
    mean_C_M = df['C_over_M'].mean()
    max_R_Phi = df['R_Phi'].max()

    if weights is None:
        weights = np.array([0.2, 0.2, 0.2, 0.2, 0.2])

    nfwi_values = []
    level_names = []
    level_labels = []
    level_codes = []

    for _, row in df.iterrows():
        if pd.isna(row['tau']) or pd.isna(row['rho']):
            nfwi_values.append(np.nan)
            level_names.append(np.nan)
            level_labels.append(np.nan)
            level_codes.append(np.nan)
            continue

        nfwi = compute_NFWI(
            rho=row['rho'],
            tau=row['tau'],
            CRJ=row['CRJ'],
            C_over_M=row['C_over_M'],
            R_Phi=row['R_Phi'],
            weights=weights,
            tau_max=tau_max,
            mean_C_M=mean_C_M,
            max_R_Phi=max_R_Phi
        )

        name, label, code = get_warning_level(nfwi)

        nfwi_values.append(nfwi)
        level_names.append(name)
        level_labels.append(label)
        level_codes.append(code)

    df['NFWI'] = nfwi_values
    df['Warning_Level'] = level_names
    df['Warning_Label'] = level_labels
    df['Warning_Code'] = level_codes

    return df


def summarize_warnings(df_with_nfwi):
    """
    Summarize warning levels across all countries in the latest year.

    Parameters:
        df_with_nfwi: DataFrame with NFWI and Warning_Level columns

    Returns:
        DataFrame: summary of warning levels by country
    """
    latest_year = df_with_nfwi['year'].max()
    latest = df_with_nfwi[df_with_nfwi['year'] == latest_year].copy()

    if latest.empty:
        return pd.DataFrame()

    summary = latest[['country', 'NFWI', 'Warning_Level', 'Warning_Label',
                       'rho', 'tau', 'CRJ', 'C_over_M', 'R_Phi']].copy()
    summary = summary.sort_values('NFWI', ascending=False)
    summary = summary.reset_index(drop=True)

    return summary


def print_warning_summary(df_with_nfwi):
    """
    Print a formatted summary of warning levels for all countries.

    Parameters:
        df_with_nfwi: DataFrame with NFWI and Warning_Level columns
    """
    summary = summarize_warnings(df_with_nfwi)

    if summary.empty:
        print("No data available.")
        return

    print("\n" + "=" * 80)
    print("  Five-Dimensional Early-Warning Matrix: Country Summary")
    print("=" * 80)
    print(f"{'Country':<12} {'NFWI':>8} {'Level':>8} {'Label':>12} "
          f"{'rho':>8} {'tau':>8} {'CRJ':>8}")
    print("-" * 80)

    for _, row in summary.iterrows():
        if pd.notna(row['NFWI']):
            print(f"{row['country']:<12} {row['NFWI']:>8.3f} "
                  f"{row['Warning_Level']:>8} {row['Warning_Label']:>12} "
                  f"{row['rho']:>8.3f} {row['tau']:>8.1f} {row['CRJ']:>8.1f}")

    print("-" * 80)

    # Count by level
    level_counts = summary['Warning_Level'].value_counts()
    print("\nSummary by warning level:")
    for level in ['Red', 'Orange', 'Yellow', 'Green']:
        count = level_counts.get(level, 0)
        print(f"  {level}: {count} countries")


if __name__ == "__main__":
    print("=" * 60)
    print("  Five-Dimensional Early-Warning Matrix Module")
    print("=" * 60)
    print()
    print("This module provides the core NFWI computation functions.")
    print()
    print("Available functions:")
    print("  - compute_NFWI()          : Compute NFWI for a single observation")
    print("  - get_warning_level()     : Classify warning level")
    print("  - compute_NFWI_for_panel(): Batch NFWI computation for panel data")
    print("  - summarize_warnings()    : Summarize warning levels by country")
    print("  - print_warning_summary() : Print formatted summary table")
    print()
    print("To run with actual data:")
    print("  df = pd.read_csv('data/panel_40countries.csv')")
    print("  df_result = compute_NFWI_for_panel(df)")
    print("  print_warning_summary(df_result)")
