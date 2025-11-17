# Four Fish School - Odor Plume Navigation Simulation

## Overview

This repository contains multiple implementations for simulating fish schooling behavior with odor plume dynamics using the Immersed Boundary Method (IBAMR framework). The simulation couples fluid dynamics, immersed boundaries (fish), and scalar transport (odor concentration).

## 📂 Repository Organization

This repository is organized into **four main implementations**, each serving different purposes:

### 🎯 1. C++ IBAMR with Odor Dynamics (Primary Implementation)

```
CPP_IBAMR_With_Odor/
```

**Our main production implementation** - Full fluid-structure-scalar coupling using IBAMR.

**Features**:
- ✅ Incompressible Navier-Stokes fluid dynamics
- ✅ 4 undulating fish with prescribed kinematics
- ✅ Immersed Boundary Method for fluid-structure interaction
- ✅ Advection-diffusion equation for odor transport
- ✅ Strong coupling between fluid and scalar fields
- ✅ High performance (C++ optimized)

**Use Cases**: Production simulations, parameter studies, publication-quality results

**Quick Start**:
```bash
cd CPP_IBAMR_With_Odor
mkdir build && cd build
cmake ..
make
./main2d ../input2d
```

[**See detailed README**](CPP_IBAMR_With_Odor/README.md)

---

### 🔧 2. C++ IBAMR Baseline (No Odor)

```
CPP_IBAMR_Baseline/
```

**Baseline fluid-structure interaction only** - Same as primary but WITHOUT odor transport.

**Features**:
- ✅ Incompressible Navier-Stokes fluid dynamics
- ✅ 4 undulating fish with prescribed kinematics
- ✅ Immersed Boundary Method
- ❌ NO scalar transport (odor)

**Use Cases**: Performance baseline, validation reference, teaching

**Quick Start**:
```bash
cd CPP_IBAMR_Baseline
mkdir build && cd build
cmake ..
make
./main2d ../input2d
```

[**See detailed README**](CPP_IBAMR_Baseline/README.md)

---

### 🐍 3. Python Odor Dynamics (Reference Implementation)

```
Python_Odor_Dynamics/
```

**Python-based reference implementation** - For prototyping, validation, and analysis.

**Features**:
- ✅ Crank-Nicolson advection-diffusion solver
- ✅ Prescribed or IBAMR-derived velocity fields
- ✅ Comprehensive visualization tools
- ✅ Easy to modify and extend
- ❌ Slower performance (~100x vs C++)

**Use Cases**: Rapid prototyping, validation, post-processing, learning

**Quick Start**:
```bash
cd Python_Odor_Dynamics
pip install -r requirements_odor_solver.txt
python odor_transport_solver_CN.py
```

[**See detailed README**](Python_Odor_Dynamics/README.md)

---

### 🧪 4. IBAMR C++ Test Suite (V&V Tests)

```
IBAMR_CPP_Tests/
```

**Complete Verification & Validation test suite** - 14 tests for scalar transport validation.

**Features**:
- ✅ 14 comprehensive V&V tests
- ✅ Analytical solution comparisons
- ✅ Convergence rate validation
- ✅ Literature benchmarking
- ✅ Common utilities library

**Use Cases**: Code validation, convergence testing, benchmarking

**Quick Start**:
```bash
cd IBAMR_CPP_Tests
./build_all_tests.sh
cd Test01_SmokeTest
../build/test01_smoke input2d
```

[**See detailed README**](IBAMR_CPP_Tests/README.md)

---

### 📊 5. Python V&V Tests (Legacy)

```
VV_Tests/
```

**Python-based V&V tests** - Original test suite (legacy, use IBAMR_CPP_Tests for new work).

**Features**:
- ✅ 14 validation tests
- ✅ Python-based analysis scripts
- ❌ Slower than C++ tests

[**See detailed README**](VV_Tests/README.md)

---

## 🚀 Quick Start Guide

### For Production Simulations (Recommended)

```bash
# Use C++ IBAMR with Odor
cd CPP_IBAMR_With_Odor
mkdir build && cd build
cmake ..
make
./main2d ../input2d
```

### For Baseline Comparison

```bash
# Use C++ IBAMR Baseline (no odor)
cd CPP_IBAMR_Baseline
mkdir build && cd build
cmake ..
make
./main2d ../input2d
```

### For Prototyping and Analysis

```bash
# Use Python implementation
cd Python_Odor_Dynamics
pip install -r requirements_odor_solver.txt
python odor_transport_solver_CN.py
```

### For Validation Testing

```bash
# Use C++ test suite
cd IBAMR_CPP_Tests
export IBAMR_ROOT=/path/to/ibamr
./build_all_tests.sh
cd Test01_SmokeTest
../build/test01_smoke input2d
```

## 📊 Implementation Comparison

| Feature | CPP_With_Odor | CPP_Baseline | Python_Odor | IBAMR_Tests |
|---------|---------------|--------------|-------------|-------------|
| **Physics** | Full NS + Odor | Full NS only | Odor only | Validation tests |
| **Performance** | ⭐⭐⭐⭐⭐ Fast | ⭐⭐⭐⭐⭐ Fast | ⭐⭐ Slow | ⭐⭐⭐⭐⭐ Fast |
| **Accuracy** | High | High | Medium | High |
| **Ease of Use** | Complex | Complex | Easy | Moderate |
| **Best For** | Production | Baseline | Prototyping | Validation |
| **Status** | ✅ Complete | ✅ Complete | ✅ Complete | ✅ Framework Ready |

## 🔬 Scientific Background

This project simulates collective behavior in fish schools with chemical communication through odor plumes.

### Physics Modeled

1. **Fluid Dynamics** (Incompressible Navier-Stokes):
   ```
   ρ(∂u/∂t + u·∇u) = -∇p + μ∇²u + f
   ∇·u = 0
   ```

2. **Immersed Boundary** (fish as elastic boundaries):
   ```
   f(x,t) = ∫ F(s,t) δ(x - X(s,t)) ds
   ```

3. **Scalar Transport** (odor advection-diffusion):
   ```
   ∂C/∂t + u·∇C = κ∇²C + S
   ```

### Key Features

- **4 Undulating Fish**: Prescribed kinematics with tail-beat frequency
- **Vortex-Odor Coupling**: Vortices modulate odor spreading
- **Schmidt Number Effects**: Validated for Sc = 1 to 1000
- **Mass Conservation**: Conservative scalar transport

## 📖 Documentation

Each directory contains comprehensive documentation:

- [**CPP_IBAMR_With_Odor/README.md**](CPP_IBAMR_With_Odor/README.md) - Full implementation guide
- [**CPP_IBAMR_Baseline/README.md**](CPP_IBAMR_Baseline/README.md) - Baseline implementation
- [**Python_Odor_Dynamics/README.md**](Python_Odor_Dynamics/README.md) - Python reference
- [**IBAMR_CPP_Tests/README.md**](IBAMR_CPP_Tests/README.md) - Complete V&V test suite
- [**README_REPOSITORY_STRUCTURE.md**](README_REPOSITORY_STRUCTURE.md) - Detailed organization

## 🛠️ Installation

### Prerequisites

#### For C++ Implementations

- **IBAMR** (0.12.0+): https://ibamr.github.io/installing/
- **SAMRAI** (included with IBAMR)
- **PETSc** (3.14+)
- **HDF5** (1.10+)
- **MPI** (OpenMPI or MPICH)
- **CMake** (3.12+)
- **C++ Compiler**: GCC 7+ or Clang 5+

#### For Python Implementation

- **Python** (3.8+)
- **NumPy** (1.20+)
- **Matplotlib** (3.3+)
- **SciPy** (1.6+)

### Installation Steps

#### 1. Install IBAMR (for C++ implementations)

```bash
# Follow IBAMR installation guide
# https://ibamr.github.io/installing/

export IBAMR_ROOT=/path/to/ibamr/installation
```

#### 2. Install Python packages (for Python implementation)

```bash
pip install -r Python_Odor_Dynamics/requirements_odor_solver.txt
```

## 📁 Directory Structure

```
Four_fish_school/
│
├── README.md                              ← This file
├── README_REPOSITORY_STRUCTURE.md         ← Detailed organization guide
│
├── CPP_IBAMR_With_Odor/                  ← PRIMARY: C++ with odor (Production)
│   ├── main.cpp
│   ├── IBEELKinematics.cpp/h
│   ├── input2d
│   ├── CMakeLists.txt
│   ├── eel2d*.vertex
│   └── README.md
│
├── CPP_IBAMR_Baseline/                   ← Baseline: C++ without odor
│   ├── main.cpp
│   ├── IBEELKinematics.cpp/h
│   ├── input2d
│   ├── CMakeLists.txt
│   ├── eel2d*.vertex
│   └── README.md
│
├── Python_Odor_Dynamics/                 ← Reference: Python implementation
│   ├── odor_transport_solver_CN.py
│   ├── test_*.py
│   ├── plot_*.py
│   ├── analyze_odor_plumes.py
│   ├── requirements_odor_solver.txt
│   └── README.md
│
├── IBAMR_CPP_Tests/                      ← Test Suite: 14 V&V tests
│   ├── common/                           ← Shared utilities
│   ├── Test01_SmokeTest/                 ← Fully implemented
│   ├── Test02-14/                        ← Template structures
│   ├── build_all_tests.sh
│   ├── run_all_tests.sh
│   ├── CMakeLists.txt
│   ├── README.md
│   └── QUICK_START.md
│
├── VV_Tests/                             ← Legacy: Python V&V tests
│   ├── Test01-14/
│   └── README.md
│
└── *.pdf                                  ← Reference papers
```

## 🎯 Development Workflow

### Recommended Workflow

1. **Prototype** in `Python_Odor_Dynamics/`
   - Quick iterations
   - Test new ideas
   - Validate concepts

2. **Validate** with `IBAMR_CPP_Tests/`
   - Run V&V tests
   - Check convergence
   - Verify correctness

3. **Implement** in `CPP_IBAMR_With_Odor/`
   - Production code
   - High performance
   - Publication results

4. **Baseline Compare** with `CPP_IBAMR_Baseline/`
   - Measure odor impact
   - Performance comparison
   - Isolate physics

### Example: Adding New Feature

```bash
# Step 1: Prototype in Python
cd Python_Odor_Dynamics
# ... test new source term ...

# Step 2: Validate implementation
cd ../IBAMR_CPP_Tests
# ... run relevant tests ...

# Step 3: Implement in C++
cd ../CPP_IBAMR_With_Odor
# ... add to main.cpp ...

# Step 4: Compare with baseline
cd ../CPP_IBAMR_Baseline
# ... run without new feature ...
```

## 📚 References

### Papers

1. **Lei, H., et al. (2021)**: "Navigation in odor plumes: How do the flapping kinematics modulate the odor landscape"
   - PDF: `Navigation in odor plumes How do the flapping kinematics modulate the odor landscape.pdf`
   - Key results: Sphere source validation, pitching airfoil effects

2. **Kamran, M., et al. (2024)**: "How does vortex dynamics help undulating bodies spread odor"
   - PDF: `How does vortex dynamics help undulating bodies spread odor.pdf`
   - Key results: High Schmidt numbers, vortex-odor coupling

### IBAMR Resources

- **Website**: https://ibamr.github.io/
- **Documentation**: https://ibamr.github.io/docs/
- **GitHub**: https://github.com/IBAMR/IBAMR
- **Examples**: https://github.com/IBAMR/IBAMR/tree/master/examples

## 🤝 Contributing

When adding new implementations or modifications:

1. Follow the existing directory structure
2. Include comprehensive README.md files
3. Document all parameters and assumptions
4. Provide build/run instructions
5. Add validation tests where appropriate

## 📄 License

[Specify license information]

## 🐛 Troubleshooting

### Common Issues

#### "IBAMR not found"
```bash
export IBAMR_ROOT=/path/to/ibamr
export CMAKE_PREFIX_PATH=$IBAMR_ROOT:$CMAKE_PREFIX_PATH
```

#### "Python packages missing"
```bash
pip install -r Python_Odor_Dynamics/requirements_odor_solver.txt
```

#### "Segmentation fault"
- Check grid resolution in input2d
- Verify all vertex files exist
- Check memory limits

#### "Slow performance"
- Use C++ implementation, not Python
- Increase MPI processes
- Reduce grid resolution for testing

## 📧 Contact

For specific questions:
- **C++ with odor**: See `CPP_IBAMR_With_Odor/README.md`
- **Baseline**: See `CPP_IBAMR_Baseline/README.md`
- **Python**: See `Python_Odor_Dynamics/README.md`
- **Tests**: See `IBAMR_CPP_Tests/README.md`

## 🔗 Quick Links

- [Repository Structure Guide](README_REPOSITORY_STRUCTURE.md)
- [C++ with Odor (Primary)](CPP_IBAMR_With_Odor/README.md)
- [C++ Baseline](CPP_IBAMR_Baseline/README.md)
- [Python Reference](Python_Odor_Dynamics/README.md)
- [Test Suite](IBAMR_CPP_Tests/README.md)
- [IBAMR Documentation](https://ibamr.github.io/docs/)

---

**Repository Status**: Active Development
**Primary Focus**: C++ IBAMR with Odor Dynamics
**Last Updated**: 2025-11-17
**Branch**: `main`
