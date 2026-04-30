"""
============================================================================
05_reproduce_figures.py
Figure Reproduction Script
============================================================================

This module reproduces all figures in the main text:
  - Figure 6.1: Commutative diagram of process-state duality language
  - Figure 6.2: Relationship between rho and information loss L(rho, k)
  - Figure 7.1: Recovery time tau evolution (1990-2024)
  - Figure 8.1: Comparison of four policy intervention scenarios

Author: Baowei Mi
License: MIT License
============================================================================
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


def configure_plotting():
    """
    Configure matplotlib global settings for consistent figure style.
    """
    plt.rcParams.update({
        'font.family': 'serif',
        'font.size': 11,
        'axes.labelsize': 12,
        'axes.titlesize': 14,
        'legend.fontsize': 10,
        'figure.dpi': 150,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.format': 'pdf'
    })


def plot_figure_6_1(save_path='output/figures/Figure_6_1_commutative.pdf'):
    """
    Reproduce Figure 6.1: Commutative diagram of the process-state duality language.

    The diagram shows the four core components:
      D (dynamic process category)
      S (static result category)
      U: D -> S (transformation functor)
      eta: Id_D => V o U (irreversible natural transformation)
    """
    configure_plotting()
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Draw boxes for D and S
    box_D = FancyBboxPatch((1, 5), 3, 1.5, boxstyle="round,pad=0.1",
                           facecolor='lightblue', edgecolor='black', linewidth=2)
    box_S = FancyBboxPatch((6, 5), 3, 1.5, boxstyle="round,pad=0.1",
                           facecolor='lightgreen', edgecolor='black', linewidth=2)
    ax.add_patch(box_D)
    ax.add_patch(box_S)

    # Labels
    ax.text(2.5, 5.75, r'$\mathcal{D}$ (Dynamic)', ha='center', va='center', fontsize=14, fontweight='bold')
    ax.text(7.5, 5.75, r'$\mathcal{S}$ (Static)', ha='center', va='center', fontsize=14, fontweight='bold')

    # Arrow U: D -> S
    ax.annotate('', xy=(6, 6.3), xytext=(4, 6.3),
                arrowprops=dict(arrowstyle='->', color='black', lw=2))
    ax.text(5, 6.6, r'$U: \mathcal{D} \to \mathcal{S}$', ha='center', fontsize=12)

    # Arrow V: S -> D
    ax.annotate('', xy=(4, 5.2), xytext=(6, 5.2),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1.5, linestyle='dashed'))
    ax.text(5, 4.9, r'$V: \mathcal{S} \to \mathcal{D}$', ha='center', fontsize=10, color='gray')

    # eta: Id_D => V o U
    ax.annotate('', xy=(2.5, 3.5), xytext=(2.5, 5),
                arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax.text(3.0, 4.25, r'$\eta: \mathrm{Id}_{\mathcal{D}} \Rightarrow V \circ U$',
            fontsize=11, color='red', rotation=90, va='center')

    # Title
    ax.set_title('Figure 6.1: Process-State Duality Language\nCore Components', fontsize=14, fontweight='bold')

    plt.savefig(save_path)
    plt.close()
    print(f"  Saved: {save_path}")


def plot_figure_6_2(save_path='output/figures/Figure_6_2_rho_curve.pdf'):
    """
    Reproduce Figure 6.2: Relationship between information retention degree rho
    and information loss L(rho, k).
    """
    configure_plotting()
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))

    rho = np.linspace(0.01, 0.99, 200)
    k_values = [0.0, 0.3, 0.6, 0.9]
    colors = ['blue', 'green', 'orange', 'red']

    for k, color in zip(k_values, colors):
        L = -rho * np.log(rho) - (1 - rho) * np.log(1 - rho) + k * (rho ** 2)
        ax.plot(rho, L, color=color, linewidth=2, label=f'k = {k}')

    ax.axvline(x=0.5, color='black', linestyle='--', alpha=0.4, label=r'$\rho = 0.5$')
    ax.set_xlabel(r'Information Retention Degree $\rho$', fontsize=13)
    ax.set_ylabel(r'Information Loss $\mathcal{L}(\rho, k)$', fontsize=13)
    ax.set_title('Figure 6.2: Information Retention Degree and Information Loss', fontsize=14, fontweight='bold')
    ax.legend(loc='upper center', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 3)

    plt.savefig(save_path)
    plt.close()
    print(f"  Saved: {save_path}")


def plot_figure_7_1(df_panel=None, save_path='output/figures/Figure_7_1_tau_trend.pdf'):
    """
    Reproduce Figure 7.1: Evolution trend of recovery time tau (1990-2024).

    Parameters:
        df_panel: cleaned panel data (if None, generates mock data)
        save_path: output path
    """
    configure_plotting()
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    if df_panel is not None and 'tau' in df_panel.columns:
        countries = ['USA', 'GBR', 'DEU', 'JPN', 'BRA']
        colors = ['red', 'blue', 'green', 'orange', 'purple']

        for country, color in zip(countries, colors):
            df_c = df_panel[df_panel['country'] == country].sort_values('year')
            if 'tau' in df_c.columns:
                ax.plot(df_c['year'], df_c['tau'], color=color, linewidth=2, label=country)
    else:
        # Generate mock data for illustration
        years = np.arange(1990, 2025)
        np.random.seed(42)
        tau_usa = 3.5 + 0.25 * (years - 1990) + np.random.normal(0, 0.5, len(years))
        tau_gbr = 2.8 + 0.12 * (years - 1990) + np.random.normal(0, 0.3, len(years))
        tau_deu = 3.0 + 0.08 * (years - 1990) + np.random.normal(0, 0.3, len(years))
        tau_jpn = 2.5 + 0.10 * (years - 1990) + np.random.normal(0, 0.4, len(years))
        tau_bra = 4.5 + 0.18 * (years - 1990) + np.random.normal(0, 0.6, len(years))

        ax.plot(years, tau_usa, color='red', linewidth=2, label='USA')
        ax.plot(years, tau_gbr, color='blue', linewidth=2, label='GBR')
        ax.plot(years, tau_deu, color='green', linewidth=2, label='DEU')
        ax.plot(years, tau_jpn, color='orange', linewidth=2, label='JPN')
        ax.plot(years, tau_bra, color='purple', linewidth=2, label='BRA')

    ax.axhline(y=10, color='red', linestyle='--', alpha=0.4, label=r'$\tau = 10$ (Critical)')
    ax.set_xlabel('Year', fontsize=13)
    ax.set_ylabel(r'Recovery Time $\tau$ (years)', fontsize=13)
    ax.set_title('Figure 7.1: Recovery Time Evolution (1990-2024)', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.savefig(save_path)
    plt.close()
    print(f"  Saved: {save_path}")


def plot_figure_8_1(scenario_results=None, save_path='output/figures/Figure_8_1_scenarios.pdf'):
    """
    Reproduce Figure 8.1: Comparison of four policy intervention scenarios.

    Parameters:
        scenario_results: dict mapping scenario name to DataFrame (if None, uses mock)
        save_path: output path
    """
    configure_plotting()
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    if scenario_results is None:
        from code.policy_simulation import run_all_scenarios
        scenario_results = run_all_scenarios(
            rho0=0.57, tau0=12.4, CRJ0=69.6, C_M0=0.52, R_Phi0=2.1,
            sim_years=16, start_year=2025
        )

    colors = {
        'No Intervention': 'red',
        'Primary Prevention': 'orange',
        'Secondary Correction': 'goldenrod',
        'Tertiary Emergency': 'blue'
    }

    # Subplot (a): NFWI evolution
    ax = axes[0, 0]
    for name, sim_df in scenario_results.items():
        ax.plot(sim_df['year'], sim_df['NFWI'], color=colors[name], linewidth=2.5, label=name)
    ax.axhline(y=0.4, color='green', linestyle='--', alpha=0.5, label='Green threshold')
    ax.axhline(y=0.8, color='red', linestyle='--', alpha=0.5, label='Red threshold')
    ax.set_xlabel('Year')
    ax.set_ylabel('NFWI')
    ax.set_title('(a) NFWI Evolution')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Subplot (b): rho evolution
    ax = axes[0, 1]
    for name, sim_df in scenario_results.items():
        ax.plot(sim_df['year'], sim_df['rho'], color=colors[name], linewidth=2)
    ax.set_xlabel('Year')
    ax.set_ylabel(r'Information Retention $\rho$')
    ax.set_title('(b) Information Retention Evolution')
    ax.grid(True, alpha=0.3)

    # Subplot (c): tau evolution
    ax = axes[1, 0]
    for name, sim_df in scenario_results.items():
        ax.plot(sim_df['year'], sim_df['tau'], color=colors[name], linewidth=2)
    ax.set_xlabel('Year')
    ax.set_ylabel(r'Recovery Time $\tau$ (years)')
    ax.set_title('(c) Recovery Time Evolution')
    ax.grid(True, alpha=0.3)

    # Subplot (d): CRJ evolution
    ax = axes[1, 1]
    for name, sim_df in scenario_results.items():
        ax.plot(sim_df['year'], sim_df['CRJ'], color=colors[name], linewidth=2)
    ax.axhline(y=12.0, color='black', linestyle=':', alpha=0.7, label='CRJ = 12.0')
    ax.set_xlabel('Year')
    ax.set_ylabel('CRJ')
    ax.set_title('(d) CRJ Evolution')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    fig.suptitle('Figure 8.1: Comparison of Four Policy Intervention Scenarios',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"  Saved: {save_path}")


def reproduce_all_figures(df_panel=None):
    """
    Reproduce all figures in the paper.

    Parameters:
        df_panel: cleaned panel data (optional; if None, uses mock data)
    """
    print("=" * 60)
    print("  Reproducing All Figures")
    print("=" * 60)
    print()

    plot_figure_6_1()
    plot_figure_6_2()
    plot_figure_7_1(df_panel)
    plot_figure_8_1()

    print()
    print("All figures saved to output/figures/")
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Reproduce figures from the paper.')
    parser.add_argument('--all', action='store_true', help='Reproduce all figures')
    parser.add_argument('--fig61', action='store_true', help='Reproduce Figure 6.1 only')
    parser.add_argument('--fig62', action='store_true', help='Reproduce Figure 6.2 only')
    parser.add_argument('--fig71', action='store_true', help='Reproduce Figure 7.1 only')
    parser.add_argument('--fig81', action='store_true', help='Reproduce Figure 8.1 only')
    parser.add_argument('--data', type=str, default=None, help='Path to panel data CSV')
    args = parser.parse_args()

    df = None
    if args.data:
        df = pd.read_csv(args.data)
        print(f"Loaded panel data: {df.shape[0]} observations")

    if args.all or (not args.fig61 and not args.fig62 and not args.fig71 and not args.fig81):
        reproduce_all_figures(df)
    else:
        if args.fig61:
            plot_figure_6_1()
        if args.fig62:
            plot_figure_6_2()
        if args.fig71:
            plot_figure_7_1(df)
        if args.fig81:
            plot_figure_8_1()
