"""
============================================================================
04_policy_simulation.py
Policy Intervention Simulation Module
============================================================================

This module performs:
  1. Mathematical modeling of process and state interventions
  2. Simulation of four policy intervention scenarios
  3. Estimation of phase transition probability and cumulative social cost
  4. Generation of comparison data for Table 7-4

Scenarios:
  - Scenario A: No intervention (baseline)
  - Scenario B: Primary prevention (mild process intervention)
  - Scenario C: Secondary correction (moderate state intervention)
  - Scenario D: Tertiary emergency (combined strong intervention)

Author: Baowei Mi
License: MIT License
============================================================================
"""

import numpy as np
import pandas as pd


def policy_simulation(rho0, tau0, CRJ0, C_M0, R_Phi0,
                      alpha=0.0, gamma=0.0,
                      sim_years=16, start_year=2025):
    """
    Simulate the evolution of the system under a given policy scenario.

    Parameters:
        rho0:       initial information retention degree
        tau0:       initial recovery time (years)
        CRJ0:       initial CRJ intensity
        C_M0:       initial capital circulation efficiency
        R_Phi0:     initial information friction intensity
        alpha:      process intervention strength (reduces R*Phi, boosts rho)
        gamma:      state intervention strength (reduces CRJ)
        sim_years:  number of simulation years
        start_year: start year of simulation

    Returns:
        DataFrame with columns: year, rho, tau, CRJ, C_over_M, R_Phi, NFWI
    """
    # Initialize state variables
    rho_t = rho0
    tau_t = tau0
    CRJ_t = CRJ0
    C_M_t = C_M0
    R_Phi_t = R_Phi0

    results = []

    for t in range(sim_years):
        year = start_year + t

        # Apply process intervention (alpha > 0)
        if alpha > 0:
            # Reduce information friction
            R_Phi_t *= (1.0 - alpha * 0.03)
            # Boost information retention
            rho_t = min(rho_t * (1.0 + alpha * 0.02), 1.0)

        # Apply state intervention (gamma > 0)
        if gamma > 0:
            # Reduce CRJ toward target of 8.0
            CRJ_t = max(CRJ_t * (1.0 - gamma * 0.05), 8.0)

        # Natural decay (no intervention)
        if alpha == 0.0 and gamma == 0.0:
            rho_t = max(rho_t * 0.985, 0.3)
            tau_t = min(tau_t * 1.04, 20.0)
            CRJ_t = min(CRJ_t * 1.02, 100.0)

        # Compute NFWI
        nfwi = _compute_nfwi_simple(rho_t, tau_t, CRJ_t, C_M_t, R_Phi_t)

        results.append({
            'year': year,
            'rho': rho_t,
            'tau': tau_t,
            'CRJ': CRJ_t,
            'C_over_M': C_M_t,
            'R_Phi': R_Phi_t,
            'NFWI': nfwi
        })

    return pd.DataFrame(results)


def _compute_nfwi_simple(rho, tau, CRJ, C_over_M, R_Phi):
    """
    Simplified NFWI computation for simulation (uses fixed normalization).

    Parameters:
        rho:       information retention degree
        tau:       recovery time (years)
        CRJ:       CRJ intensity
        C_over_M:  capital circulation efficiency
        R_Phi:     information friction intensity

    Returns:
        NFWI: float in [0, 1]
    """
    weights = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
    x = np.array([
        1.0 - rho,
        tau / 16.8,
        CRJ / 12.0,
        abs(C_over_M - 0.45),
        R_Phi / 2.8
    ])
    return float(np.dot(weights, x))


def run_all_scenarios(rho0, tau0, CRJ0, C_M0, R_Phi0,
                      sim_years=16, start_year=2025):
    """
    Run all four policy intervention scenarios.

    Parameters:
        rho0:       initial information retention degree
        tau0:       initial recovery time (years)
        CRJ0:       initial CRJ intensity
        C_M0:       initial capital circulation efficiency
        R_Phi0:     initial information friction intensity
        sim_years:  number of simulation years
        start_year: start year of simulation

    Returns:
        dict: mapping scenario name to DataFrame of simulation results
    """
    scenarios = {
        'No Intervention':       {'alpha': 0.0, 'gamma': 0.0},
        'Primary Prevention':    {'alpha': 0.3, 'gamma': 0.0},
        'Secondary Correction':  {'alpha': 0.0, 'gamma': 0.6},
        'Tertiary Emergency':    {'alpha': 0.7, 'gamma': 0.8}
    }

    results = {}
    for name, params in scenarios.items():
        sim_df = policy_simulation(
            rho0=rho0, tau0=tau0, CRJ0=CRJ0,
            C_M0=C_M0, R_Phi0=R_Phi0,
            alpha=params['alpha'],
            gamma=params['gamma'],
            sim_years=sim_years,
            start_year=start_year
        )
        results[name] = sim_df

    return results


def estimate_phase_transition_prob(sim_df, critical_tau=15.0, critical_rho=0.45):
    """
    Estimate the probability of phase transition within the simulation period.

    Phase transition is defined as: tau > critical_tau AND rho < critical_rho.

    Parameters:
        sim_df:       simulation DataFrame
        critical_tau: threshold for tau (years)
        critical_rho: threshold for rho

    Returns:
        float: probability in [0, 1]
    """
    transition_triggered = ((sim_df['tau'] > critical_tau) &
                            (sim_df['rho'] < critical_rho)).any()
    return 1.0 if transition_triggered else 0.0


def estimate_cumulative_cost(scenario_name, sim_years=16):
    """
    Estimate cumulative intervention cost as a percentage of GDP.

    Parameters:
        scenario_name: name of the scenario
        sim_years:     number of simulation years

    Returns:
        float: cumulative cost as fraction of GDP
    """
    cost_rates = {
        'No Intervention':       0.000,
        'Primary Prevention':    0.028,
        'Secondary Correction':  0.041,
        'Tertiary Emergency':    0.067
    }
    annual_rate = cost_rates.get(scenario_name, 0.0)
    return annual_rate * sim_years


def generate_comparison_table(scenario_results):
    """
    Generate comparison table (Table 7-4) from simulation results.

    Parameters:
        scenario_results: dict mapping scenario name to DataFrame

    Returns:
        DataFrame: comparison table
    """
    rows = []
    for name, sim_df in scenario_results.items():
        final_year = sim_df['year'].max()
        final = sim_df[sim_df['year'] == final_year].iloc[0]

        mid_year = sim_df['year'].min() + (sim_df['year'].max() - sim_df['year'].min()) // 2
        mid = sim_df[sim_df['year'] == mid_year]
        if len(mid) > 0:
            mid = mid.iloc[0]
        else:
            mid = final

        nfwi_mid = mid['NFWI']
        nfwi_final = final['NFWI']
        rho_final = final['rho']
        tau_final = final['tau']
        phase_prob = estimate_phase_transition_prob(sim_df)
        cost = estimate_cumulative_cost(name)

        rows.append({
            'Scenario': name,
            'NFWI_2030': round(nfwi_mid, 3),
            'NFWI_Final': round(nfwi_final, 3),
            'rho_Final': round(rho_final, 3),
            'tau_Final': round(tau_final, 1),
            'Phase_Transition_Prob': f"{phase_prob:.0%}",
            'Cumulative_Cost_GDP': f"{cost:.1%}"
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    print("=" * 60)
    print("  Policy Intervention Simulation Module")
    print("=" * 60)
    print()

    # Example: US 2024 baseline data
    print("Example simulation using US 2024 baseline data:")
    print(f"  rho = 0.57, tau = 12.4, CRJ = 69.6, C/M = 0.52, R*Phi = 2.1")
    print()

    scenario_results = run_all_scenarios(
        rho0=0.57, tau0=12.4, CRJ0=69.6,
        C_M0=0.52, R_Phi0=2.1,
        sim_years=16, start_year=2025
    )

    print("Simulation results (final year):")
    print("-" * 60)
    for name, sim_df in scenario_results.items():
        final = sim_df.iloc[-1]
        print(f"  {name}:")
        print(f"    NFWI = {final['NFWI']:.3f}, rho = {final['rho']:.3f}, "
              f"tau = {final['tau']:.1f}, CRJ = {final['CRJ']:.1f}")

    print()
    print("Comparison table (Table 7-4):")
    print("-" * 60)
    comparison = generate_comparison_table(scenario_results)
    print(comparison.to_string(index=False))
