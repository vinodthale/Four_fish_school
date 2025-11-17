# Four Fish School - Repository Structure

This repository contains multiple implementations for simulating fish schooling with odor plume dynamics using the Immersed Boundary Method (IBAMR framework).

## 📁 Repository Organization

### 🎯 **Primary Implementation** (Recommended)
```
CPP_IBAMR_With_Odor/
```
**C++ IBAMR implementation with odor dynamics** - This is our main focus and most complete implementation.
- Full fluid-structure-scalar coupling
- 4 undulating fish (eels) with odor transport
- IBAMR framework with custom odor solver integration
- Production-ready code

### 🧪 **Test Suites**
```
IBAMR_CPP_Tests/
```
**Complete V&V test suite (14 tests)** for scalar transport validation in C++.
- Comprehensive verification & validation tests
- Pure C++ IBAMR implementation
- See `IBAMR_CPP_Tests/README.md` for details

```
VV_Tests/
```
**Python-based V&V tests** for initial validation.
- 14 tests for scalar transport
- Analysis and plotting scripts

### 🐍 **Python Reference Implementation**
```
Python_Odor_Dynamics/
```
**Python-based odor dynamics** - Reference implementation and analysis tools.
- Crank-Nicolson odor transport solver
- Visualization and analysis scripts
- Useful for prototyping and validation

### 🔧 **Baseline Implementation**
```
CPP_IBAMR_Baseline/
```
**C++ IBAMR without odor** - Baseline fluid-structure interaction only.
- 4 undulating fish without odor transport
- Useful for performance comparison
- Baseline for adding odor dynamics

## 🚀 Quick Start

### For C++ IBAMR with Odor (Primary Implementation)
```bash
cd CPP_IBAMR_With_Odor
mkdir build && cd build
cmake ..
make
./main2d input2d
```

### For Testing (V&V Test Suite)
```bash
cd IBAMR_CPP_Tests
./build_all_tests.sh
cd Test01_SmokeTest
../build/test01_smoke input2d
```

### For Python Analysis
```bash
cd Python_Odor_Dynamics
python odor_transport_solver_CN.py
```

## 📊 Implementation Comparison

| Feature | CPP_IBAMR_With_Odor | CPP_IBAMR_Baseline | Python_Odor_Dynamics | IBAMR_CPP_Tests |
|---------|---------------------|-------------------|---------------------|----------------|
| **Language** | C++ | C++ | Python | C++ |
| **Framework** | IBAMR | IBAMR | Custom/NumPy | IBAMR |
| **Fluid Dynamics** | ✅ Full NS | ✅ Full NS | ❌ Prescribed | ✅ Full NS |
| **Immersed Boundary** | ✅ 4 Fish | ✅ 4 Fish | ❌ No | ✅ Test-specific |
| **Odor Transport** | ✅ Coupled | ❌ No | ✅ Standalone | ✅ Validation |
| **Performance** | 🚀 Fast | 🚀 Fast | 🐌 Slow | 🚀 Fast |
| **Use Case** | Production | Baseline | Prototyping | Testing |
| **Status** | ✅ Complete | ✅ Complete | ✅ Complete | ✅ Framework Ready |

## 📖 Documentation

Each directory contains detailed README files:

- **CPP_IBAMR_With_Odor/README.md** - C++ IBAMR with odor implementation guide
- **CPP_IBAMR_Baseline/README.md** - Baseline implementation guide
- **Python_Odor_Dynamics/README.md** - Python implementation and analysis
- **IBAMR_CPP_Tests/README.md** - Complete V&V test suite documentation
- **VV_Tests/README.md** - Python V&V tests

## 🔬 Scientific Background

This work simulates collective behavior in fish schools with chemical communication (odor plumes). Key physics:

1. **Fluid Dynamics**: Incompressible Navier-Stokes equations
2. **Immersed Boundary**: Fish represented as elastic boundaries
3. **Scalar Transport**: Advection-diffusion equation for odor concentration
4. **Coupling**: Vortex dynamics modulate odor spreading

### References

1. **Lei et al. (2021)**: "Navigation in odor plumes: How do the flapping kinematics modulate the odor landscape"
   - PDF: `Navigation in odor plumes How do the flapping kinematics modulate the odor landscape.pdf`

2. **Kamran et al. (2024)**: "How does vortex dynamics help undulating bodies spread odor"
   - PDF: `How does vortex dynamics help undulating bodies spread odor.pdf`

## 🗂️ File Organization

### Root Level Files
- `README.md` - This file
- `*.pdf` - Reference papers
- `.gitignore` - Git ignore rules

### Shared Resources
- Reference papers (PDFs) accessible to all implementations
- Common documentation

## 🔧 Dependencies

### For C++ Implementations
- **IBAMR** (0.12.0+): https://ibamr.github.io/
- **SAMRAI** (included with IBAMR)
- **PETSc** (3.14+)
- **HDF5** (1.10+)
- **MPI** (OpenMPI or MPICH)
- **CMake** (3.12+)
- **C++ Compiler** (GCC 7+, Clang 5+)

### For Python Implementations
- **Python** (3.8+)
- **NumPy** (1.20+)
- **Matplotlib** (3.3+)
- **SciPy** (1.6+)

## 📝 Getting Started Guide

### Step 1: Choose Your Implementation

**For production simulations**: Use `CPP_IBAMR_With_Odor/`
- Best performance
- Full physics
- Complete implementation

**For baseline comparison**: Use `CPP_IBAMR_Baseline/`
- Fluid-structure only
- No scalar transport
- Performance reference

**For prototyping**: Use `Python_Odor_Dynamics/`
- Quick iterations
- Easy visualization
- Analysis tools

**For validation**: Use `IBAMR_CPP_Tests/`
- Test scalar transport solver
- Verify implementation
- Check convergence

### Step 2: Install Dependencies

```bash
# Install IBAMR (for C++ implementations)
# Follow: https://ibamr.github.io/installing/

# Or install Python packages (for Python implementation)
pip install -r Python_Odor_Dynamics/requirements.txt
```

### Step 3: Build and Run

See individual README files in each directory for specific instructions.

## 🎯 Development Roadmap

### Phase 1: Baseline (Complete ✅)
- [x] C++ IBAMR fluid-structure interaction
- [x] 4 undulating fish kinematics
- [x] Visualization pipeline

### Phase 2: Odor Dynamics (Complete ✅)
- [x] Python odor transport solver
- [x] C++ IBAMR scalar transport integration
- [x] Coupled fluid-odor dynamics

### Phase 3: Validation (In Progress 🔄)
- [x] V&V test suite framework
- [x] Test01: Smoke test implemented
- [ ] Tests 02-14: Implementation pending
- [ ] Literature comparison

### Phase 4: Production (Planned 📅)
- [ ] Parameter studies
- [ ] Collective behavior analysis
- [ ] Performance optimization
- [ ] Publication-ready results

## 🤝 Contributing

When adding new implementations:
1. Create a new directory following the naming convention
2. Include a comprehensive README.md
3. Document dependencies
4. Provide build/run instructions
5. Add validation tests

## 📄 License

[Specify license information]

## 📧 Contact

For questions about:
- **C++ IBAMR implementations**: See `CPP_IBAMR_*/README.md`
- **Test suite**: See `IBAMR_CPP_Tests/README.md`
- **Python implementations**: See `Python_Odor_Dynamics/README.md`

## 🔗 Useful Links

- **IBAMR Documentation**: https://ibamr.github.io/docs/
- **IBAMR GitHub**: https://github.com/IBAMR/IBAMR
- **IBAMR Examples**: https://github.com/IBAMR/IBAMR/tree/master/examples

---

**Last Updated**: 2025-11-17
**Repository Status**: Active Development
**Primary Branch**: `main`
**Current Focus**: C++ IBAMR implementation with odor dynamics
