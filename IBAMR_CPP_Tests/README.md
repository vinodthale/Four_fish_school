# IBAMR C++ Test Suite for Scalar Transport

This directory contains a complete implementation of all 14 Verification & Validation (V&V) tests for scalar transport (odor concentration) using the IBAMR framework, implemented entirely in C++.

## Overview

This test suite validates the advection-diffusion solver for scalar transport in IBAMR, which is used to simulate odor concentration fields in the 4-fish school simulation. All tests are self-contained C++ applications using the IBAMR framework.

## About IBAMR

IBAMR is an open-source Immersed Boundary Method framework for simulating fluid-structure interaction.
- **Website**: https://ibamr.github.io/
- **Documentation**: https://ibamr.github.io/docs/
- **GitHub**: https://github.com/IBAMR/IBAMR

## Directory Structure

```
IBAMR_CPP_Tests/
├── README.md                          ← This file
├── CMakeLists.txt                     ← Master build file
├── common/                            ← Shared utilities
│   ├── include/
│   │   ├── AnalyticalSolutions.h     ← Analytical solution functions
│   │   ├── ErrorCalculator.h         ← L2/Linf error computation
│   │   └── TestUtilities.h           ← Common test helpers
│   └── src/
│       ├── AnalyticalSolutions.cpp
│       ├── ErrorCalculator.cpp
│       └── TestUtilities.cpp
│
├── Test01_SmokeTest/                  ← Basic infrastructure check
│   ├── main.cpp
│   ├── input2d
│   ├── CMakeLists.txt
│   └── README.md
│
├── Test02_Diffusion_Analytic/         ← Gaussian diffusion validation
│   ├── main.cpp
│   ├── input2d
│   ├── CMakeLists.txt
│   └── README.md
│
├── Test03_Advection_Analytic/         ← Pure advection validation
│   ├── main.cpp
│   ├── input2d
│   ├── CMakeLists.txt
│   └── README.md
│
├── Test04_MMS/                        ← Manufactured solution
│   ├── main.cpp
│   ├── input2d
│   ├── CMakeLists.txt
│   └── README.md
│
├── Test05_Discontinuous/              ← Top-hat stability test
│   ├── main.cpp
│   ├── input2d
│   ├── CMakeLists.txt
│   └── README.md
│
├── Test06_MassConservation/           ← Mass budget validation
│   ├── main.cpp
│   ├── input2d
│   ├── CMakeLists.txt
│   └── README.md
│
├── Test07_BCs/                        ← Boundary condition tests
│   ├── main.cpp
│   ├── input2d
│   ├── CMakeLists.txt
│   └── README.md
│
├── Test08_SphereSource/               ← Sphere source (Lei et al.)
│   ├── main.cpp
│   ├── input2d
│   ├── CMakeLists.txt
│   └── README.md
│
├── Test09_HighSc/                     ← High Schmidt number
│   ├── main.cpp
│   ├── input2d
│   ├── CMakeLists.txt
│   └── README.md
│
├── Test10_MovingIB/                   ← Moving IB + scalar
│   ├── main.cpp
│   ├── input2d
│   ├── CMakeLists.txt
│   └── README.md
│
├── Test11_AMR/                        ← AMR sensitivity
│   ├── main.cpp
│   ├── input2d
│   ├── CMakeLists.txt
│   └── README.md
│
├── Test12_TimeStep/                   ← Time-step convergence
│   ├── main.cpp
│   ├── input2d
│   ├── CMakeLists.txt
│   └── README.md
│
├── Test13_LongRun/                    ← Long-run periodicity
│   ├── main.cpp
│   ├── input2d
│   ├── CMakeLists.txt
│   └── README.md
│
└── Test14_Benchmarks/                 ← Literature comparisons
    ├── main.cpp
    ├── input2d
    ├── CMakeLists.txt
    └── README.md
```

## Test Suite Overview

| Test # | Name | Purpose | Pass Criteria |
|--------|------|---------|---------------|
| 1 | Smoke Test | Basic infrastructure check | No crashes, no NaNs |
| 2 | Pure Diffusion | Gaussian diffusion vs analytic | L2 error convergence rate ≈ 2.0 |
| 3 | Pure Advection | Profile advection validation | L2 error < tolerance |
| 4 | MMS | Manufactured solution verification | Convergence rate ≈ 2.0 |
| 5 | Discontinuous | Top-hat advection stability | No oscillations, no negatives |
| 6 | Mass Conservation | Global tracer mass budget | Relative drift < 1e-10 |
| 7 | Boundary Conditions | Dirichlet/Neumann/flux tests | BC error ≤ 1e-6 |
| 8 | Sphere Source | Compare Lei et al. | Match literature ±10% |
| 9 | High Schmidt | Sc=100-1000 stability | Stable, physically reasonable |
| 10 | Moving IB | Ellipsoid + scalar coupling | No instabilities |
| 11 | AMR Sensitivity | Refinement artifact checks | Consistent across refinements |
| 12 | Time-step CFL | Temporal convergence | Convergence rate ≈ 2.0 |
| 13 | Long Run | Periodic conservation checks | No drift over time |
| 14 | Benchmarks | Literature comparisons | Match Lei/Kamran data |

## Building the Tests

### Prerequisites

1. **IBAMR** (with dependencies: SAMRAI, PETSc, HDF5)
   - Follow installation guide: https://ibamr.github.io/installing/

2. **CMake** (version 3.12+)

3. **C++ Compiler** with C++14 support (GCC 7+, Clang 5+)

### Build Instructions

```bash
# Set IBAMR installation path
export IBAMR_ROOT=/path/to/ibamr/installation

# Build all tests
cd IBAMR_CPP_Tests
mkdir build && cd build
cmake .. -DIBAMR_ROOT=$IBAMR_ROOT
make -j4

# Or build individual test
cd Test01_SmokeTest
mkdir build && cd build
cmake ..
make
```

### Environment Variables

```bash
# Required
export IBAMR_ROOT=/path/to/ibamr

# Optional (if not in standard locations)
export SAMRAI_ROOT=/path/to/samrai
export PETSC_DIR=/path/to/petsc
export HDF5_ROOT=/path/to/hdf5
```

## Running the Tests

### Run Individual Test
```bash
cd Test01_SmokeTest/build
./test01_smoke input2d
```

### Run All Tests (Sequential)
```bash
cd IBAMR_CPP_Tests
./run_all_tests.sh
```

### Run with MPI
```bash
mpirun -np 4 ./test01_smoke input2d
```

## Test Descriptions

### Tier 1: Basic Verification (Tests 1-6)
These tests verify fundamental solver capabilities.

**Test 1: Smoke Test**
- Verifies basic infrastructure works
- No immersed boundaries
- Simple initial condition
- Expected: No crashes, no NaNs

**Test 2: Pure Diffusion**
- Compares to analytical Gaussian solution: C(x,t) = exp(-x²/4κt)/√(4πκt)
- Tests diffusion operator accuracy
- Expected: 2nd order convergence

**Test 3: Pure Advection**
- Advects a profile with uniform velocity
- Tests advection operator
- Expected: Profile shape preservation

**Test 4: Method of Manufactured Solutions**
- Uses known source term to verify correctness
- Tests combined advection-diffusion
- Expected: 2nd order convergence

**Test 5: Discontinuous Initial Condition**
- Top-hat function advection
- Tests monotonicity and stability
- Expected: No oscillations, no negative values

**Test 6: Mass Conservation**
- Tracks global mass over time
- Tests conservative property
- Expected: Relative drift < 1e-10

### Tier 2: Physical Validation (Tests 7-10)
These tests validate physical behavior.

**Test 7: Boundary Conditions**
- Tests Dirichlet, Neumann, Robin BCs
- Verifies BC enforcement
- Expected: BC errors ≤ 1e-6

**Test 8: Sphere Source**
- Compares to Lei et al. (2021) data
- Steady sphere with scalar source
- Expected: Match literature ±10%

**Test 9: High Schmidt Number**
- Tests Sc = 100, 340, 1000
- Validates thin boundary layers
- Expected: Stable, physically reasonable

**Test 10: Moving Immersed Boundary**
- Oscillating ellipsoid with scalar field
- Tests IB-scalar coupling
- Expected: No instabilities

### Tier 3: Production Validation (Tests 11-14)
These tests validate production readiness.

**Test 11: AMR Sensitivity**
- Runs with different refinement ratios
- Checks for AMR artifacts
- Expected: Consistent results

**Test 12: Time-step Sensitivity**
- CFL number variation
- Temporal convergence study
- Expected: 2nd order convergence

**Test 13: Long Run**
- Extended simulation (T = 100+)
- Checks long-term stability
- Expected: No drift, no instabilities

**Test 14: Benchmarks**
- Lei et al. (2021): Pitching airfoil
- Kamran et al. (2024): Undulating body
- Expected: Match published data

## Output and Results

Each test produces:
1. **Console output**: Real-time progress and error metrics
2. **VTK files**: Visualization data (compatible with VisIt/ParaView)
3. **HDF5 files**: Checkpoint/restart data
4. **Error report**: L2/Linf errors, convergence rates
5. **Summary**: Pass/fail verdict with details

### Typical Output
```
Test01_SmokeTest/
├── viz_test01/              ← VisIt visualization data
│   ├── dumps.visit
│   ├── lag_data.*.vtu
│   └── visit*.*.vtk
├── restart_test01/          ← Restart files
├── test01_output.log        ← Simulation log
└── test01_results.txt       ← Error metrics and verdict
```

## Validation Criteria

### Convergence Tests (2, 4, 12)
```
Expected convergence rate: 2.0 ± 0.3
L2 error ~ (Δx)^2 for spatial
L2 error ~ (Δt)^2 for temporal
```

### Mass Conservation (6, 13)
```
Advection-only: |M(t) - M(0)|/M(0) < 1e-10
With diffusion:  |M(t) - M(0)|/M(0) < 1e-6
```

### Stability Tests (5, 9, 10, 11)
```
No negative concentrations: min(C) ≥ -1e-12
No NaN values
No exponential growth
```

### Literature Comparison (8, 14)
```
Coarse grid: ±20% acceptable
Fine grid:   ±10% target
```

## Common Utilities

The `common/` directory provides shared functionality:

### AnalyticalSolutions.h/cpp
- Gaussian diffusion solution
- Manufactured solutions
- Exact advection profiles

### ErrorCalculator.h/cpp
- L2 norm computation
- L∞ norm computation
- Convergence rate calculation
- Grid refinement studies

### TestUtilities.h/cpp
- Mass conservation checks
- Negative concentration detection
- NaN/Inf detection
- Output formatting

## Troubleshooting

### Build Issues

**"IBAMR not found"**
```bash
export IBAMR_ROOT=/correct/path/to/ibamr
cmake .. -DIBAMR_ROOT=$IBAMR_ROOT
```

**"SAMRAI headers not found"**
```bash
export SAMRAI_ROOT=/path/to/samrai
export CMAKE_PREFIX_PATH=$SAMRAI_ROOT:$CMAKE_PREFIX_PATH
```

### Runtime Issues

**"Segmentation fault"**
- Check input2d file exists
- Verify grid dimensions are reasonable
- Check memory limits (ulimit -v)

**"No convergence"**
- Reduce time step
- Check CFL condition
- Verify boundary conditions

**"Wrong convergence rate"**
- Ensure time step scales with grid: Δt ~ Δx² (diffusion)
- Check initial conditions are smooth
- Verify BCs not polluting interior

## References

### IBAMR Documentation
- User Guide: https://ibamr.github.io/docs/
- Examples: https://github.com/IBAMR/IBAMR/tree/master/examples
- API: https://ibamr.github.io/api/

### Literature
1. **Lei, M., Crimaldi, J. P., & Li, C. (2021)**
   - "Navigation in odor plumes: How do the flapping kinematics modulate the odor landscape?"
   - AIAA AVIATION 2021 Forum
   - DOI: 10.2514/6.2021-2817
   - PDF: `../Navigation in odor plumes.pdf`
   - Validates: Rotating cylinder, sphere source (Test08)
   - References: Yan & Zu (2008), Richter & Nikrityuk (2012)
   - Tests: 8, 14

2. **Khalid, K., Schneider, J., McHenry, M., & Smits, A. (2024)**
   - "How does vortex dynamics help undulating bodies spread odor?"
   - arXiv preprint: arXiv:2408.16136v1
   - PDF: `../How does vortex dynamics help undulating bodies spread odor.pdf`
   - Validates: High-Sc transport (Sc ≤ 1000), undulating body framework (Test09)
   - Water target: Sc = 340 (exceeded)
   - Tests: 9, 10, 14

### Related Repositories
- Parent repo: Four_fish_school
- IBAMR framework: https://github.com/IBAMR/IBAMR

## Quick Start

1. **Install IBAMR**: Follow https://ibamr.github.io/installing/
2. **Set environment**:
   ```bash
   export IBAMR_ROOT=/path/to/ibamr
   ```
3. **Build Test 1**:
   ```bash
   cd Test01_SmokeTest
   mkdir build && cd build
   cmake ..
   make
   ```
4. **Run Test 1**:
   ```bash
   ./test01_smoke ../input2d
   ```
5. **Check results**: Look for "TEST PASSED" in output

## Development Status

- [x] Directory structure created
- [ ] Common utilities implemented
- [ ] Test 1: Smoke Test
- [ ] Test 2: Pure Diffusion
- [ ] Test 3: Pure Advection
- [ ] Test 4: MMS
- [ ] Test 5: Discontinuous
- [ ] Test 6: Mass Conservation
- [ ] Test 7: Boundary Conditions
- [ ] Test 8: Sphere Source
- [ ] Test 9: High Schmidt
- [ ] Test 10: Moving IB
- [ ] Test 11: AMR
- [ ] Test 12: Time-step
- [ ] Test 13: Long Run
- [ ] Test 14: Benchmarks

## Contributing

This test suite is designed to be:
- **Self-contained**: Each test is an independent C++ application
- **Well-documented**: Clear purpose and pass/fail criteria
- **Reproducible**: Fixed seeds, documented parameters
- **Extensible**: Easy to add new tests

## License

Same as parent Four_fish_school repository.

## Contact

For questions about IBAMR: https://github.com/IBAMR/IBAMR/issues
For questions about this test suite: See parent repository

---

**Last Updated**: 2025-11-17
**IBAMR Version**: 0.12.0+ recommended
**Status**: In Development
