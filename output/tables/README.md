# Tables Directory

This directory contains output tables generated from the empirical analysis.

## File Description

- `Table_7_3_parameters.csv`: Core parameter estimation results
- `Table_7_4_scenarios.csv`: Comparison results of four policy intervention scenarios

## Correspondence with the Paper

| File | Paper Reference | Description |
|------|---------------|-------------|
| `Table_7_3_parameters.csv` | Table 7.3 | Parameter estimates, standard errors, and confidence intervals |
| `Table_7_4_scenarios.csv` | Table 7.4 | NFWI, rho, tau, and phase transition probability under four scenarios |

## Regeneration

To regenerate all tables, run:

```bash
python code/05_reproduce_figures.py --tables-only
