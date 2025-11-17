# V&V Checklist Implementation Guide

## Overview
This document provides a comprehensive guide to implementing and executing the verification & validation (V&V) checklist for scalar transport in the IBAMR-based 4-fish school simulation.

## Quick Start

### Prerequisites
```bash
# Required software
- IBAMR (with AdvDiffHierarchyIntegrator)
- Python 3.7+ with numpy, matplotlib, scipy
- MPI (for parallel runs)
- CMake 3.1+ (for compilation)

# Install Python dependencies
pip install numpy matplotlib scipy pyvista
```

### Running Tests

#### Individual Test
```bash
cd VV_Tests/Test01_SmokeTest
./run_test.sh
```

#### All Tests
```bash
cd VV_Tests
./run_all_tests.sh
```

## Test Hierarchy

### Tier 1: Basic Infrastructure (Tests 1-3)
**Run these first** - they verify basic scalar machinery without complex physics.

- **Test 1: Smoke Test** - Does it run without crashing?
- **Test 2: Pure Diffusion** - Is diffusion operator correct?
- **Test 3: Pure Advection** - Is advection operator correct?

**Status**: If these fail, fix solver before proceeding.

### Tier 2: Solver Verification (Tests 4-6)
Verify combined operators and conservation properties.

- **Test 4: MMS** - Full coupled solver verification
- **Test 5: Discontinuous** - Limiter and stability checks
- **Test 6: Mass Conservation** - Global conservation budget

**Status**: These verify mathematical correctness.

### Tier 3: Physical Validation (Tests 7-10)
Compare against physics and literature.

- **Test 7: Boundary Conditions** - BC implementation correct?
- **Test 8: Sphere Source** - Matches Lei et al. published data?
- **Test 9: High Schmidt** - Handles realistic Sc numbers?
- **Test 10: Moving IB** - IB-scalar coupling works?

**Status**: These validate physical accuracy.

### Tier 4: Production Readiness (Tests 11-14)
Ensure robustness for production simulations.

- **Test 11: AMR** - Adaptive refinement working correctly?
- **Test 12: Time-step** - Temporal accuracy verified?
- **Test 13: Long Run** - No drift over many cycles?
- **Test 14: Benchmarks** - Final comparison with literature

**Status**: These ensure production reliability.

## Recommended Execution Order

### Phase 1: Quick Validation (1-2 hours)
Run smoke tests to verify basic functionality:
```bash
cd Test01_SmokeTest && ./run_test.sh
cd Test02_Diffusion_Analytic && ./run_test.sh  # Coarse grid only
```

### Phase 2: Core Verification (Half day)
Full analytic validation:
```bash
# Test 2: All three grids for convergence
cd Test02_Diffusion_Analytic
./run_convergence_study.sh

# Test 3: Advection convergence
cd Test03_Advection_Analytic
./run_test.sh
```

### Phase 3: Physical Validation (1-2 days)
```bash
# Test 8: Sphere source (compare Lei et al.)
cd Test08_SphereSource
./run_test.sh

# Test 10: Moving IB
cd Test10_MovingIB
./run_test.sh
```

### Phase 4: Production Tests (2-3 days)
```bash
# Long runs and benchmarks
cd Test13_LongRun
./run_test.sh

cd Test14_Benchmarks
./run_all_benchmarks.sh
```

## Pass/Fail Criteria Summary

| Test | Pass Criteria | Tolerance |
|------|---------------|-----------|
| 1. Smoke | No crash, BCs enforced | Qualitative |
| 2. Diffusion | Convergence order ≈ 2 | ±15% |
| 3. Advection | Order matches scheme | ±15% |
| 4. MMS | 2nd order convergence | ±15% |
| 5. Discontinuous | No negative C, oscillations | Max overshoot < 1.1 |
| 6. Mass | Drift < threshold | <1e-10 (advec), <1e-6 (diff) |
| 7. BCs | Flux across Neumann BC | <O(Δx) |
| 8. Sphere | Centerline decay match | ±10-20% of Lei et al. |
| 9. High Sc | Stable, no oscillations | Qualitative |
| 10. IB | No leakage, pattern match | Flux <O(Δx²) |
| 11. AMR | Match uniform fine grid | Within discretization error |
| 12. Time-step | Temporal convergence | Order matches scheme |
| 13. Long Run | No secular drift | Mass conserved |
| 14. Benchmarks | Literature agreement | ±10-20% |

## Key Tolerances

### Convergence Rates
- **Expected order**: Match discretization scheme
- **Acceptable range**: ±15% of expected
- **Example**: For 2nd-order scheme, accept rates 1.7-2.3

### Mass Conservation
- **Advection-only**: `|M(t)-M(0)|/M(0) < 1e-10`
- **Advection-diffusion**: `|M(t)-M(0)|/M(0) < 1e-6`
- **With source**: `M(t) - M(0) = ∫Q dt` (within numerical error)

### Boundary Conditions
- **Dirichlet**: `|C_boundary - C_prescribed| < 1e-6`
- **Neumann**: `|∫ ∂C/∂n dS| < C_tol × Δx`
- **IB no-flux**: `|flux| < O(Δx²)`

### Literature Comparison
- **Coarse grid**: ±20% acceptable
- **Refined grid**: Should approach ±10%
- **Qualitative features**: Must match (e.g., wake shape)

## Common Issues and Debugging

### Test Failures

#### Test 1 (Smoke) Fails
**Symptoms**: Crash, NaNs, wrong BC values

**Debug**:
1. Check IBAMR installation
2. Verify `AdvDiffHierarchyIntegrator` registered
3. Check BC specification in input file
4. Inspect log file for errors

#### Test 2 (Diffusion) Poor Convergence
**Symptoms**: Order < 1.5 or > 2.5

**Debug**:
1. Check `diffusion_time_stepping_type` (should be CRANK_NICOLSON or BACKWARD_EULER)
2. Verify Δt proportional to Δx² for stability
3. Check BCs not polluting interior
4. Verify diffusion coefficient set correctly

#### Test 3 (Advection) High Errors
**Symptoms**: Large L² errors, oscillations

**Debug**:
1. Check `convective_op_type` (PPM, CENTERED, etc.)
2. Verify CFL < 1.0
3. For centered schemes, may need limiter
4. Check velocity field is correct

#### Test 6 (Mass) Drift
**Symptoms**: Mass changes over time

**Debug**:
1. Check BCs (should be no-flux for conservation)
2. Verify velocity field divergence-free
3. Check no unintended sources/sinks
4. Inspect grid resolution (too coarse may lose mass)

#### Test 10 (Moving IB) Leakage
**Symptoms**: Flux across IB surface non-zero

**Debug**:
1. Verify IB BC implementation (∂C/∂n=0)
2. Check delta function width
3. Ensure sufficient grid resolution near IB
4. Inspect IB velocity interpolation

## Analysis Tools

### Provided Scripts

Each test includes:
- `analyze.py`: Python analysis script
- `plot_convergence.py`: Convergence plots
- `compare_literature.py`: Benchmark comparisons (Tests 8, 14)

### Custom Analysis

#### Extract from VTK
```python
import pyvista as pv

# Read VTK file
mesh = pv.read('viz_test/data_000100.vtk')

# Extract scalar field
C = mesh['C']  # or appropriate variable name

# Compute metrics
C_max = C.max()
C_mean = C.mean()
mass = (C * dx * dy).sum()
```

#### Compute Errors
```python
import numpy as np

def compute_errors(C_num, C_ana, dx):
    diff = C_num - C_ana
    L2 = np.sqrt(np.sum(diff**2) * dx**2)
    Linf = np.max(np.abs(diff))
    return L2, Linf
```

#### Convergence Rate
```python
def convergence_rate(dx, errors):
    log_dx = np.log(dx)
    log_err = np.log(errors)
    # Fit line: log(err) = p*log(dx) + c
    p = np.polyfit(log_dx, log_err, 1)[0]
    return p
```

## Literature References

### Lei et al. (2021) - Navigation in odor plumes
**File**: `Navigation in odor plumes How do the flapping kinematics modulate the odor landscape.pdf`

**Key Data**:
- Sphere source validation (Section 2)
- Schmidt number effects
- Pitching airfoil + odor interaction
- Centerline concentration profiles

**Relevant Tests**: 8, 10, 14

### Kamran et al. (2024) - Collective chemotactic behavior
**File**: `How does vortex dynamics help undulating bodies spread odor.pdf` (arXiv:2408.16136)

**Key Data**:
- High Schmidt numbers (Sc up to 340)
- Vortex-odor coupling
- Undulating body wake enhancement
- Grid convergence studies

**Relevant Tests**: 9, 10, 14

## Reporting Results

### Individual Test Report
Each test generates:
```
TestXX_report.md
- Test description
- Setup parameters
- Results (errors, convergence rates)
- Figures (convergence plots, comparisons)
- Pass/Fail verdict
```

### Master Report
After running all tests:
```bash
cd VV_Tests
python3 generate_master_report.py
```

Produces `VV_Master_Report.pdf` with:
- Executive summary (pass/fail table)
- All convergence plots
- Literature comparisons
- Recommendations for production

## Customization

### Modifying Test Parameters

Edit `input2d` in each test directory:
```
// Change grid resolution
N = 128  // instead of 64

// Change diffusion coefficient
KAPPA = 0.001  // adjust as needed

// Change time integration
diffusion_time_stepping_type = "CRANK_NICOLSON"  // or BACKWARD_EULER
```

### Adding New Tests

1. Create directory: `TestXX_NewTest/`
2. Add README.md describing test
3. Create `input2d` configuration
4. Write `analyze.py` script
5. Create `run_test.sh` launcher
6. Update `run_all_tests.sh`

### Modifying Tolerances

Edit analysis scripts:
```python
# In analyze.py
PASS_TOL_CONVERGENCE = 0.15  # ±15%
PASS_TOL_MASS = 1e-6
PASS_TOL_BC = 1e-6
```

## Performance Optimization

### Parallel Execution
```bash
# Run on N processors
mpirun -np 4 ./test_executable input2d

# For cluster (example SLURM)
sbatch run_test_parallel.sh
```

### Grid Selection
- **Coarse validation**: N=64 (minutes)
- **Production validation**: N=256 (hours)
- **High-fidelity**: N=512+ with AMR (days)

### Time Integration
- **Explicit**: Fast but small Δt (CFL < 1)
- **Implicit diffusion**: Stable for large Sc
- **CRANK_NICOLSON**: Best accuracy (2nd order in time)

## Troubleshooting Compilation

### IBAMR Not Found
```bash
export IBAMR_DIR=/path/to/ibamr/install
export CMAKE_PREFIX_PATH=$IBAMR_DIR:$CMAKE_PREFIX_PATH
```

### Linking Errors
Check `CMakeLists.txt`:
```cmake
FIND_PACKAGE(IBAMR REQUIRED)
TARGET_LINK_LIBRARIES(test_executable IBAMR::IBAMR2d)
```

### Runtime Errors
```bash
# Check library paths
export LD_LIBRARY_PATH=$IBAMR_DIR/lib:$LD_LIBRARY_PATH

# Verify PETSC/SAMRAI
ldd ./test_executable
```

## Next Steps After V&V

### If All Tests Pass ✅
1. Proceed to production simulations
2. Run 4-fish school with scalar transport
3. Analyze odor plumes and vortex interactions
4. Compare with Lei et al. experimental/numerical data

### If Some Tests Fail ❌
1. Identify failure mode (solver bug, BC issue, discretization error)
2. Fix implementation
3. Re-run failed tests
4. Document fixes in `VV_Tests/Results/fixes.md`

### Production Recommendations
Based on V&V results:
- **Grid resolution**: Minimum N based on Test 2 convergence
- **Time step**: From Test 12 CFL study
- **AMR levels**: From Test 11 cost-benefit analysis
- **Schmidt number**: Validated range from Test 9

## Contact and Contribution

For issues, improvements, or questions:
- Review individual test READMEs
- Check IBAMR documentation
- Consult Lei et al. and Kamran et al. papers
- Document any custom modifications in `VV_Tests/MODIFICATIONS.md`

---

**Version**: 1.0
**Date**: 2024
**Status**: Complete test suite ready for execution
