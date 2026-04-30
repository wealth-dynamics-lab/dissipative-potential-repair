# Figures Directory

This directory contains all figures generated from the empirical analysis.

## File Description

- `Figure_6_1_commutative.pdf`: Commutative diagram of the process-state duality language
- `Figure_6_2_rho_curve.pdf`: Relationship curve between rho and information loss
- `Figure_7_1_tau_trend.pdf`: Evolution trend of recovery time tau
- `Figure_8_1_scenarios.pdf`: Comparison of four policy intervention scenarios

## Correspondence with the Paper

| File | Paper Reference | Description |
|------|---------------|-------------|
| `Figure_6_1_commutative.pdf` | Figure 6.1 | Four core components of the process-state duality language |
| `Figure_6_2_rho_curve.pdf` | Figure 6.2 | Information retention degree rho and information loss |
| `Figure_7_1_tau_trend.pdf` | Figure 7.1 | Recovery time tau evolution (1990-2024) |
| `Figure_8_1_scenarios.pdf` | Figure 8.1 | Policy simulation results under four scenarios |

## Regeneration

To regenerate all figures, run:

```bash
python code/05_reproduce_figures.py --figures-only
