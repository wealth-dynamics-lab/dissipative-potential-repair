"""
============================================================================
02_parameter_estimation.py
Parameter Estimation: tau, rho, k, and Hansen Threshold
============================================================================

This module performs:
  1. Estimation of information retention degree rho (Eq. 7.6)
  2. Rolling-window AR(1) estimation of recovery time tau (Eq. 7.8-7.9)
  3. Panel regression estimation of compression constant k (Eq. 7.7)
  4. Hansen panel threshold regression for CRJ phase transition point
  5. GARCH volatility correction

Author: Baowei Mi
License: MIT License
============================================================================
"""

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.filters.hp_filter import hpfilter
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from arch import arch_model
from sklearn.linear_model import LinearRegression


# ============================================================
# 2.1 Information Retention Degree (rho) Estimation
# ============================================================
def estimate_rho(igm, internet_pen, avg_school, max_product=None):
    """
    Estimate information retention degree rho.

    rho = (IGM * InfoDiff) / max(IGM * InfoDiff)

    Parameters:
        igm:          intergenerational mobility index (Chetty et al. 2014, 0-1)
        internet_pen: internet penetration rate (0-1)
        avg_school:   average years of schooling (Z-score standardized)
        max_product:  global maximum of IGM * InfoDiff (for normalization)

    Returns:
        rho: array, information retention degree in (0, 1]
    """
    info_diff = 0.6 * np.asarray(internet_pen) + 0.4 * np.asarray(avg_school)
    product = np.asarray(igm) * info_diff
    
    if max_product is None:
        max_product = np.nanmax(product) if np.any(~np.isnan(product)) else 1.0
    
    rho = product / max_product
    rho = np.clip(rho, 1e-6, 1.0)
    
    return rho


# ============================================================
# 2.2 Recovery Time (tau) Estimation - Rolling Window AR(1)
# ============================================================
def estimate_tau(crj_series, window=15):
    """
    Estimate recovery time tau using rolling-window AR(1) model.

    tau = -1 / ln(phi), where phi is the AR(1) coefficient.

    Parameters:
        crj_series: array-like, CRJ time series
        window:     int, rolling window length (default 15 years)

    Returns:
        tau_series: array, tau estimates for each time point
    """
    n = len(crj_series)
    tau_series = np.full(n, np.nan)
    
    for t in range(window - 1, n):
        y = np.array(crj_series[t - window + 1 : t + 1], dtype=float)
        
        # HP filter detrending
        cycle, trend = hpfilter(y, lamb=1600)
        y_detrended = cycle
        
        # ADF test
        if len(y_detrended) > 5:
            adf_p = adfuller(y_detrended, maxlag=min(5, len(y_detrended) // 2))[1]
            if adf_p > 0.05:
                y_detrended = np.diff(y_detrended)
        
        # AR(1) estimation
        try:
            fitted = ARIMA(y_detrended, order=(1, 0, 0)).fit()
            phi = fitted.params[1]
            if 0.01 < phi < 0.99:
                tau_series[t] = -1.0 / np.log(phi)
        except:
            continue
    
    return tau_series


def estimate_tau_for_country(df_country, crj_col='CRJ', window=15):
    """
    Estimate tau for a single country panel.

    Parameters:
        df_country: DataFrame for one country
        crj_col:    column name for CRJ
        window:     rolling window length

    Returns:
        Series: tau estimates aligned to original index
    """
    crj_series = df_country[crj_col].values
    tau_values = estimate_tau(crj_series, window=window)
    return pd.Series(tau_values, index=df_country.index)


# ============================================================
# 2.3 Compression Constant (k) Estimation
# ============================================================
def estimate_k(crj_series, gini_series):
    """
    Estimate compression constant k.

    k_{i,t} = beta * CRJ_{i,t} / Gini_{i,t} + gamma * Delta_CRJ_{i,t-1}

    Parameters:
        crj_series:  array-like, CRJ time series
        gini_series: array-like, Gini coefficient time series

    Returns:
        dict: {'beta': ..., 'gamma': ..., 'r_squared': ...}
    """
    crj = np.asarray(crj_series).ravel()
    gini = np.asarray(gini_series).ravel()
    
    ratio = crj / gini
    delta_crj = np.diff(crj, prepend=crj[0])
    
    X = np.column_stack([ratio, delta_crj])
    y = gini
    
    valid = ~np.isnan(X).any(axis=1) & ~np.isnan(y)
    
    model = LinearRegression().fit(X[valid], y[valid])
    r_squared = model.score(X[valid], y[valid])
    
    return {
        'beta': model.coef_[0],
        'gamma': model.coef_[1],
        'r_squared': r_squared
    }


# ============================================================
# 2.4 Hansen Panel Threshold Regression
# ============================================================
def hansen_threshold(y, q, x_control=None, n_bootstrap=1000):
    """
    Hansen (1999) panel threshold regression.

    Endogenously identifies the structural break point in threshold variable q.

    Parameters:
        y:            dependent variable (e.g., Top 10% wealth share)
        q:            threshold variable (e.g., CRJ or epsilon)
        x_control:    control variable matrix (optional)
        n_bootstrap:  number of bootstrap replications

    Returns:
        dict: {'threshold': ..., 'F_stat': ..., 'p_value': ..., 'bootstrap_reps': ...}
    """
    y = np.asarray(y).ravel()
    q = np.asarray(q).ravel()
    
    valid = ~(np.isnan(y) | np.isnan(q))
    y, q = y[valid], q[valid]
    n = len(y)
    
    # Search for optimal threshold
    q_sorted = np.sort(np.unique(q))
    trim = int(0.15 * n)
    q_candidates = q_sorted[trim : n - trim]
    
    best_ssr = np.inf
    best_gamma = None
    
    for gamma in q_candidates:
        d = (q <= gamma).astype(int)
        if x_control is not None:
            X = np.column_stack([d, x_control[valid]])
        else:
            X = d.reshape(-1, 1)
        
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        ssr = np.sum((y - X @ beta) ** 2)
        
        if ssr < best_ssr:
            best_ssr = ssr
            best_gamma = gamma
    
    # F-statistic
    ssr_linear = np.sum((y - np.mean(y)) ** 2)
    ssr_threshold = best_ssr
    f_stat = ((ssr_linear - ssr_threshold) / 1) / (ssr_threshold / (n - 2))
    
    # Bootstrap p-value
    f_boot = []
    for _ in range(n_bootstrap):
        y_shuffled = np.random.permutation(y)
        ssr_boot = np.inf
        for gamma in q_candidates:
            d_b = (q <= gamma).astype(int)
            beta_b = np.linalg.lstsq(d_b.reshape(-1, 1), y_shuffled, rcond=None)[0]
            ssr_b = min(ssr_b, np.sum((y_shuffled - d_b * beta_b) ** 2))
        ssr0_b = np.sum((y_shuffled - np.mean(y_shuffled)) ** 2)
        f_boot.append(((ssr0_b - ssr_b) / 1) / (ssr_b / (n - 2)))
    
    p_value = np.mean(np.array(f_boot) >= f_stat)
    
    return {
        'threshold': best_gamma,
        'F_stat': f_stat,
        'p_value': p_value,
        'bootstrap_reps': n_bootstrap
    }


# ============================================================
# 2.5 GARCH Volatility Correction
# ============================================================
def garch_volatility(crj_series):
    """
    Estimate GARCH(1,1) conditional volatility for tau uncertainty correction.

    Parameters:
        crj_series: array-like, CRJ time series

    Returns:
        cond_vol: array, conditional volatility series
    """
    crj = np.asarray(crj_series)
    returns = np.diff(np.log(np.maximum(crj, 0.01)))
    
    try:
        model = arch_model(returns, vol='Garch', p=1, q=1)
        fitted = model.fit(disp='off')
        return fitted.conditional_volatility
    except:
        return np.full(len(returns), np.nanstd(returns))


def estimate_tau_with_garch(crj_series, window=15):
    """
    Estimate tau with GARCH volatility correction.

    Parameters:
        crj_series: array-like, CRJ time series
        window:     rolling window length

    Returns:
        dict: {'tau': tau_series, 'tau_lower': lower_bound, 'tau_upper': upper_bound}
    """
    tau_raw = estimate_tau(crj_series, window=window)
    vol = garch_volatility(crj_series)
    
    # Pad volatility to match tau length
    vol_padded = np.full(len(tau_raw), np.nan)
    vol_padded[-len(vol):] = vol if len(vol) <= len(tau_raw) else vol[:len(tau_raw)]
    
    # Confidence bands: tau +/- 1.96 * scaled_vol
    scaling = np.nanmean(tau_raw) / np.nanmean(vol_padded) if np.nanmean(vol_padded) > 0 else 1.0
    tau_lower = tau_raw - 1.96 * vol_padded * scaling
    tau_upper = tau_raw + 1.96 * vol_padded * scaling
    
    return {
        'tau': tau_raw,
        'tau_lower': tau_lower,
        'tau_upper': tau_upper
    }


# ============================================================
# 2.6 Batch Estimation for Panel Data
# ============================================================
def estimate_all_parameters(df_panel, window=15):
    """
    Estimate all core parameters for the full panel dataset.

    Parameters:
        df_panel: DataFrame with columns: country, year, CRJ, top10_share,
                  bottom50_share, internet_penetration, avg_schooling,
                  intergen_mobility, RoL, RQ, GFCF, GDP_deflator
        window:   rolling window length for tau estimation

    Returns:
        DataFrame: panel data with added columns: rho, tau, k, C_over_M, R_Phi
    """
    results = []
    
    for country, group in df_panel.groupby('country'):
        df_c = group.sort_values('year').copy()
        
        # rho estimation
        if all(col in df_c.columns for col in ['intergen_mobility', 'internet_penetration', 'avg_schooling']):
            df_c['rho'] = estimate_rho(
                df_c['intergen_mobility'].values,
                df_c['internet_penetration'].values,
                df_c['avg_schooling'].values
            )
        else:
            df_c['rho'] = np.nan
        
        # tau estimation
        if 'CRJ' in df_c.columns:
            tau_results = estimate_tau_with_garch(df_c['CRJ'].values, window=window)
            df_c['tau'] = tau_results['tau']
            df_c['tau_lower'] = tau_results['tau_lower']
            df_c['tau_upper'] = tau_results['tau_upper']
        
        # k estimation (if Gini available)
        if 'CRJ' in df_c.columns and 'gini_wealth' in df_c.columns:
            k_results = estimate_k(df_c['CRJ'].values, df_c['gini_wealth'].values)
            df_c['k'] = k_results['beta'] * df_c['CRJ'] / df_c['gini_wealth'] + \
                        k_results['gamma'] * df_c['CRJ'].diff().fillna(0)
        
        # Derived variables
        if all(col in df_c.columns for col in ['M', 'C', 'R', 'Phi']):
            df_c['C_over_M'] = df_c['C'] / df_c['M']
            df_c['R_Phi'] = df_c['R'] * df_c['Phi']
        
        results.append(df_c)
    
    df_full = pd.concat(results, ignore_index=True)
    return df_full


if __name__ == "__main__":
    print("=" * 60)
    print("  Parameter Estimation Module")
    print("=" * 60)
    print()
    print("This module provides functions for estimating all core parameters:")
    print()
    print("  - estimate_rho()              : Information retention degree")
    print("  - estimate_tau()              : Recovery time (rolling AR(1))")
    print("  - estimate_tau_with_garch()   : Recovery time with GARCH correction")
    print("  - estimate_k()                : Compression constant")
    print("  - hansen_threshold()          : Hansen panel threshold regression")
    print("  - garch_volatility()          : GARCH conditional volatility")
    print("  - estimate_all_parameters()   : Batch estimation for full panel")
    print()
    print("See GitHub repository for complete usage examples.")
