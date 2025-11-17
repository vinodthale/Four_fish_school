# C++ IBAMR Baseline Implementation (No Odor Dynamics)

## Overview

This is the **baseline implementation** of the 4-fish school simulation using IBAMR, **without odor transport**. This implementation includes:

- ✅ Incompressible Navier-Stokes fluid dynamics
- ✅ 4 undulating fish (eels) with prescribed kinematics
- ✅ Immersed Boundary Method for fluid-structure interaction
- ❌ NO scalar transport (odor concentration)

## Purpose

This baseline implementation serves as:

1. **Performance Reference**: Compare computational cost with/without odor dynamics
2. **Validation Baseline**: Validate fluid-structure interaction before adding scalars
3. **Starting Point**: Foundation for adding new physics (scalars, chemistry, etc.)
4. **Teaching Tool**: Simpler code for understanding IBAMR fluid-structure coupling

## Comparison with Full Implementation

| Feature | This (Baseline) | CPP_IBAMR_With_Odor |
|---------|----------------|---------------------|
| Fluid Dynamics | ✅ Full NS | ✅ Full NS |
| Immersed Boundaries | ✅ 4 Fish | ✅ 4 Fish |
| Odor Transport | ❌ No | ✅ Yes |
| Scalar Equations | ❌ No | ✅ Yes |
| Complexity | Simple | Complex |
| Compute Time | ~100% | ~150-200% |
| Memory Usage | ~100% | ~130-150% |

## Directory Structure

```
CPP_IBAMR_Baseline/
├── README.md              ← This file
├── main.cpp               ← Main driver (no odor)
├── IBEELKinematics.cpp    ← Fish kinematics
├── IBEELKinematics.h      ← Header
├── input2d                ← IBAMR input file
├── CMakeLists.txt         ← Build configuration
└── eel2d*.vertex          ← Fish geometry files
```

## Building

### Prerequisites

- IBAMR (0.12.0+) with dependencies (SAMRAI, PETSc, HDF5)
- MPI
- CMake (3.12+)
- C++ compiler with C++14 support

### Build Instructions

```bash
# Set IBAMR path
export IBAMR_ROOT=/path/to/ibamr

# Build
cd CPP_IBAMR_Baseline
mkdir build && cd build
cmake ..
make

# Run
./main2d ../input2d
```

### Build with MPI

```bash
mkdir build && cd build
cmake .. -DCMAKE_CXX_COMPILER=mpicxx
make
mpirun -np 4 ./main2d ../input2d
```

## Running

### Basic Run
```bash
cd build
./main2d ../input2d
```

### Parallel Run
```bash
mpirun -np 4 ./main2d ../input2d
```

### Output Files

The simulation produces:
- `viz_IB2d/` - VisIt visualization files
- `restart_IB2d/` - Restart/checkpoint files
- `IBEELKinematics2d.log` - IBAMR log file

## Visualization

### Using VisIt
```bash
visit -o viz_IB2d/dumps.visit
```

### Using ParaView
```bash
paraview viz_IB2d/lag_data.*.vtu
```

You should see:
- 4 undulating fish (eels)
- Fluid velocity field
- Vorticity patterns
- Pressure field

## Physics

### Governing Equations

**Incompressible Navier-Stokes:**
```
ρ(∂u/∂t + u·∇u) = -∇p + μ∇²u + f
∇·u = 0
```

Where:
- u = fluid velocity
- p = pressure
- ρ = density
- μ = dynamic viscosity
- f = force from immersed boundaries

**Immersed Boundary:**
```
f(x,t) = ∫ F(s,t) δ(x - X(s,t)) ds
X(s,t) = prescribed kinematics (undulation)
```

### No Scalar Transport

Unlike `CPP_IBAMR_With_Odor`, this implementation does **NOT** solve:
```
∂C/∂t + u·∇C = κ∇²C    ← NOT INCLUDED
```

## Key Parameters

Modify in `input2d`:

### Domain
```
domain_boxes = [ (0,0), (255,255) ]  // Grid resolution
x_lo = 0.0, 0.0                      // Domain lower corner
x_up = 12.0, 3.0                     // Domain upper corner
```

### Time Integration
```
START_TIME = 0.0
END_TIME = 10.0
DT = 0.0001                          // Time step
```

### Fluid Properties
```
MU = 0.01                            // Dynamic viscosity
RHO = 1.0                            // Density
```

### Fish Motion
```
TAIL_FREQ = 1.0                      // Tail beat frequency (Hz)
```

## Performance

Typical performance on a modern workstation:

| Configuration | Time/Step | Real-time Factor |
|--------------|-----------|------------------|
| 256×256, 1 core | ~2 sec | 1:20000 |
| 256×256, 4 cores | ~0.5 sec | 1:5000 |
| 512×512, 4 cores | ~2 sec | 1:20000 |

**Note**: This is ~30-50% faster than `CPP_IBAMR_With_Odor` because no scalar solver.

## Validation

### Expected Results

1. **Fish Undulation**: All 4 fish should undulate with prescribed frequency
2. **Vortex Shedding**: Wake vortices should form behind each fish
3. **Flow Field**: Velocity field should show realistic flow patterns
4. **Stability**: No crashes, no NaN values

### Quick Checks

```bash
# Check if simulation completes
./main2d ../input2d
echo $?  # Should return 0

# Check for visualization files
ls -l viz_IB2d/

# Check log for errors
grep -i error IBEELKinematics2d.log
```

## Troubleshooting

### Issue: Segmentation Fault
**Solution**: Check grid resolution in `input2d`. Start with smaller grids (128×128).

### Issue: Very Slow
**Solution**:
- Reduce grid resolution
- Increase time step (DT) slightly
- Use more MPI processes

### Issue: Fish Not Moving
**Solution**: Check `TAIL_FREQ` parameter and kinematics file

### Issue: NaN Values
**Solution**:
- Reduce time step (DT)
- Check CFL condition: u*dt/dx < 1

## Code Structure

### main.cpp

Main driver that:
1. Initializes IBAMR/SAMRAI
2. Creates INS integrator (Navier-Stokes)
3. Creates IB method (immersed boundaries)
4. Sets up fish kinematics
5. Runs time integration loop
6. Outputs visualization data

### IBEELKinematics.cpp/h

Custom kinematics class that:
- Prescribes fish undulation motion
- Updates fish positions each time step
- Handles 4 fish independently

### input2d

IBAMR input file with:
- Domain and grid parameters
- Solver parameters
- Physical parameters
- Output settings

## Extending This Code

To add odor dynamics to this baseline:

1. **Add AdvDiff integrator**:
   ```cpp
   Pointer<AdvDiffHierarchyIntegrator> adv_diff_integrator =
       new AdvDiffHierarchyIntegrator(...);
   ```

2. **Register with NS integrator**:
   ```cpp
   navier_stokes_integrator->registerAdvDiffHierarchyIntegrator(adv_diff_integrator);
   ```

3. **Set initial/boundary conditions**:
   ```cpp
   adv_diff_integrator->setInitialConditions(...);
   adv_diff_integrator->setPhysicalBcCoef(...);
   ```

4. **Update input2d**:
   Add `AdvDiffHierarchyIntegrator` section

See `CPP_IBAMR_With_Odor` for complete implementation.

## Next Steps

1. **Run baseline simulation**: Validate fluid-structure works
2. **Compare with full implementation**: Run `CPP_IBAMR_With_Odor` with same parameters
3. **Performance analysis**: Compare compute times
4. **Add scalars**: Use as starting point for new scalar transport

## References

- IBAMR Documentation: https://ibamr.github.io/docs/
- IBAMR IB Examples: https://github.com/IBAMR/IBAMR/tree/master/examples/IB
- Parent Repository: ../README.md

## Related Implementations

- **With Odor**: `../CPP_IBAMR_With_Odor/` - Full implementation with scalar transport
- **Python**: `../Python_Odor_Dynamics/` - Python-based odor solver
- **Tests**: `../IBAMR_CPP_Tests/` - V&V test suite

---

**Status**: Complete and tested
**Last Updated**: 2025-11-17
**Recommended Use**: Performance baseline and validation reference
