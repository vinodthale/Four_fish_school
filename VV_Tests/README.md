# Verification & Validation (V&V) Test Suite for Scalar Transport

This directory contains a comprehensive V&V test suite for validating the scalar transport (odor concentration) implementation in the IBAMR-based 4-fish school simulation.

## Test Sequence (Run in Order)

| Test # | Test Name | Purpose | Status |
|--------|-----------|---------|--------|
| 1 | Smoke Test | Scalar infrastructure check | Pending |
| 2 | Pure Diffusion | Gaussian diffusion vs analytic | Pending |
| 3 | Pure Advection | Profile advection vs analytic | Pending |
| 4 | MMS | Manufactured solution verification | Pending |
| 5 | Discontinuous | Top-hat advection stability | Pending |
| 6 | Mass Conservation | Global tracer mass budget | Pending |
| 7 | Boundary Conditions | Dirichlet/Neumann/flux tests | Pending |
| 8 | Sphere Source | Compare Lei et al. | Pending |
| 9 | High Schmidt | Sc=100-1000 stability | Pending |
| 10 | Moving IB | Ellipsoid + scalar coupling | Pending |
| 11 | AMR Sensitivity | Refinement artifact checks | Pending |
| 12 | Time-step CFL | Temporal convergence | Pending |
| 13 | Long Run | Periodic conservation checks | Pending |
| 14 | Benchmarks | Literature comparisons | Pending |

## References

1. **Lei et al. (2021)** - Navigation in odor plumes (10308831)
2. **Kamran et al. (2024)** - Collective chemotactic behavior (arXiv:2408.16136v1)

## Directory Structure

```
VV_Tests/
├── Test01_SmokeTest/          # Basic scalar infrastructure
├── Test02_Diffusion_Analytic/ # Gaussian diffusion validation
├── Test03_Advection_Analytic/ # Pure advection validation
├── Test04_MMS/                # Manufactured solution
├── Test05_Discontinuous/      # Top-hat stability test
├── Test06_MassConservation/   # Mass budget validation
├── Test07_BCs/                # Boundary condition tests
├── Test08_SphereSource/       # Sphere source (Lei et al.)
├── Test09_HighSc/             # High Schmidt number
├── Test10_MovingIB/           # Moving IB + scalar
├── Test11_AMR/                # AMR sensitivity
├── Test12_TimeStep/           # Time-step convergence
├── Test13_LongRun/            # Long-run periodicity
├── Test14_Benchmarks/         # Literature comparisons
├── Analysis_Scripts/          # Post-processing tools
└── Results/                   # Output data and reports
```

## Expected Tolerances

- **Grid convergence**: Slope matching scheme order ±15%
- **Mass conservation**: Relative drift < 1e-10 (advection-only), < 1e-6 (coupled)
- **Boundary enforcement**: Dirichlet error ≤ 1e-6, Neumann flux ≤ O(Δx)
- **Stability**: No negative concentrations, no NaNs

## Running Tests

Each test directory contains:
- `input2d` - IBAMR input file
- `README.md` - Test description and procedure
- `run_test.sh` - Execution script
- `analyze.py` - Analysis script

Execute tests sequentially:
```bash
cd VV_Tests/Test01_SmokeTest
./run_test.sh
python3 analyze.py
```

## Output Format

Each test generates:
- Simulation data (VTK files)
- Error metrics (L2, L∞)
- Convergence plots
- Pass/fail report

Results are saved to `Results/TestXX_report.md`.
