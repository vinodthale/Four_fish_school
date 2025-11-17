# Python Odor Dynamics - Reference Implementation

## Overview

This directory contains Python-based implementations for odor transport and analysis. These serve as reference implementations for prototyping, validation, and analysis of the C++ IBAMR code.

## Purpose

1. **Rapid Prototyping**: Test ideas quickly before implementing in C++
2. **Validation**: Cross-check C++ results against Python implementation
3. **Analysis**: Post-processing and visualization tools
4. **Teaching**: Easier to understand and modify than C++ code

## Contents

### Core Solvers

- **`odor_transport_solver_CN.py`** - Crank-Nicolson solver for advection-diffusion
  - Pure Python implementation
  - 2D scalar transport solver
  - Supports prescribed velocity fields

### Test Scripts

- **`test_odor_CN_with_ibamr.py`** - Test Crank-Nicolson solver with IBAMR velocity data
- **`test_odor_transport_vortex_dynamics.py`** - Test odor transport with vortex structures
- **`test_cpp_odor_integration.py`** - Validation tests for C++ implementation

### Visualization Tools

- **`plot_odor_concentration.py`** - Plot odor concentration fields
- **`plot_combined_fluid_eel.py`** - Combined fluid velocity and eel visualization
- **`plot_eel_only.py`** - Visualize eel positions and kinematics
- **`analyze_odor_plumes.py`** - Comprehensive odor plume analysis

### Utilities

- **`generate_4fish_vertices.py`** - Generate vertex files for 4-fish configuration
- **`requirements_odor_solver.txt`** - Python package dependencies

### Documentation

- **`README_ODOR_SOLVER_CN.md`** - Detailed Crank-Nicolson solver documentation
- **`README_ODOR_TRANSPORT_TEST.md`** - Testing and validation guide

## Installation

```bash
cd Python_Odor_Dynamics
pip install -r requirements_odor_solver.txt
```

### Dependencies

- Python 3.8+
- NumPy 1.20+
- Matplotlib 3.3+
- SciPy 1.6+

## Quick Start

### 1. Run Basic Odor Transport
```bash
python odor_transport_solver_CN.py
```

### 2. Visualize Results
```bash
python plot_odor_concentration.py
```

### 3. Analyze Odor Plumes
```bash
python analyze_odor_plumes.py
```

## Features

### Odor Transport Solver

The Crank-Nicolson solver (`odor_transport_solver_CN.py`) solves:

```
∂C/∂t + u·∇C = κ∇²C + S
```

Where:
- C = odor concentration
- u = fluid velocity (prescribed or from IBAMR)
- κ = diffusion coefficient (molecular diffusivity)
- S = source term

**Features**:
- 2nd order accurate in time (Crank-Nicolson)
- 2nd order accurate in space (centered differences)
- Stable for moderate CFL numbers
- Supports various boundary conditions

### Visualization

Multiple visualization options:
- Contour plots of concentration
- Velocity field overlays
- Fish position tracking
- Time evolution animations
- Cross-sectional profiles

## Usage Examples

### Example 1: Simple Diffusion
```python
from odor_transport_solver_CN import OdorTransportSolver

# Create solver
solver = OdorTransportSolver(
    Lx=10.0, Ly=3.0,
    Nx=256, Ny=128,
    kappa=0.001,  # Diffusion coefficient
    dt=0.01
)

# Set initial condition (Gaussian blob)
solver.set_initial_condition_gaussian(x0=2.0, y0=1.5, sigma=0.2)

# Run simulation
for step in range(1000):
    solver.step()
    if step % 100 == 0:
        solver.plot()
```

### Example 2: Advection-Diffusion
```python
# Set prescribed velocity field
solver.set_velocity_uniform(u=1.0, v=0.0)  # Uniform flow

# Run with advection
solver.step()
```

### Example 3: Load IBAMR Velocity Data
```python
# Load velocity from IBAMR simulation
solver.load_velocity_from_ibamr("viz_IB2d/visit000100.vtk")

# Evolve odor with realistic flow
solver.step()
```

## Comparison with C++ Implementation

| Feature | Python | C++ IBAMR |
|---------|--------|-----------|
| **Speed** | Slow (~100x slower) | Fast |
| **Memory** | High | Optimized |
| **Accuracy** | 2nd order | 2nd order |
| **Coupling** | Weak (offline) | Strong (online) |
| **Ease of Use** | Very easy | Complex |
| **Best For** | Prototyping | Production |

## Validation

The Python solver has been validated against:
1. Analytical solutions (Gaussian diffusion)
2. MMS (Method of Manufactured Solutions)
3. C++ IBAMR implementation

See `README_ODOR_TRANSPORT_TEST.md` for validation details.

## Performance

Typical performance on a modern laptop:

| Grid Size | Time/Step | Memory |
|-----------|-----------|--------|
| 128×128 | ~0.1 sec | ~50 MB |
| 256×256 | ~0.5 sec | ~200 MB |
| 512×512 | ~2 sec | ~800 MB |

**Note**: Python is ~100x slower than C++ IBAMR implementation.

## Workflow

### Typical Development Workflow

1. **Prototype in Python**: Test new ideas quickly
2. **Validate**: Compare against analytical solutions
3. **Implement in C++**: Port to IBAMR for performance
4. **Cross-validate**: Compare Python vs C++ results
5. **Analyze**: Use Python tools for post-processing

### Example Workflow: Adding New Source Term

```python
# Step 1: Prototype in Python
def new_source_term(x, y, t):
    return np.exp(-((x-5)**2 + (y-1.5)**2)/0.1) * np.sin(2*np.pi*t)

solver.set_source_function(new_source_term)
solver.run(T=10.0)

# Step 2: Validate results
# ... check if physically reasonable ...

# Step 3: Implement in C++ (see CPP_IBAMR_With_Odor/)
# Step 4: Compare results
```

## Testing

Run all tests:
```bash
python test_odor_CN_with_ibamr.py
python test_odor_transport_vortex_dynamics.py
python test_cpp_odor_integration.py
```

## Troubleshooting

### Issue: Slow Performance
**Solution**: Use smaller grids or reduce time steps. For production, use C++ implementation.

### Issue: Oscillations in Solution
**Solution**:
- Reduce time step (dt)
- Increase diffusion coefficient (κ)
- Check CFL condition: u*dt/dx < 1

### Issue: Negative Concentrations
**Solution**:
- Use smaller time step
- Check boundary conditions
- Ensure source terms are non-negative

## Extending This Code

### Add New Initial Condition
```python
def set_initial_condition_custom(self):
    for i in range(self.Nx):
        for j in range(self.Ny):
            x = self.x[i, j]
            y = self.y[i, j]
            self.C[i, j] = your_function(x, y)
```

### Add New Boundary Condition
```python
def apply_custom_bc(self):
    # Left boundary
    self.C[0, :] = boundary_value_left
    # Right boundary
    self.C[-1, :] = boundary_value_right
    # etc.
```

## References

1. **Crank-Nicolson Method**: Numerical solution of parabolic PDEs
2. **Advection-Diffusion**: Classical scalar transport theory
3. **Lei et al. (2021)**: Navigation in odor plumes (see main README)
4. **Kamran et al. (2024)**: Vortex dynamics and odor (see main README)

## Related Implementations

- **C++ IBAMR with Odor**: `../CPP_IBAMR_With_Odor/` - Production implementation
- **C++ IBAMR Baseline**: `../CPP_IBAMR_Baseline/` - Without odor
- **Test Suite**: `../IBAMR_CPP_Tests/` - V&V tests

## Next Steps

1. Run basic odor transport simulation
2. Visualize results
3. Compare with C++ implementation
4. Use for analysis and prototyping

---

**Status**: Complete reference implementation
**Last Updated**: 2025-11-17
**Recommended Use**: Prototyping, validation, and analysis
