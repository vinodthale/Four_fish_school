# Quick Start Guide: Lei et al. Odor Plume Navigation

This guide gets you running the Lei et al. (2021) odor plume study in IBAMR quickly.

## Prerequisites

✓ IBAMR installed with dependencies (PETSc, SAMRAI, HDF5)
✓ Python 3.7+ with numpy, matplotlib, pyvista, scipy
✓ MPI for parallel execution

## Step 1: Prepare Foil Geometry

Create a simple NACA0012 foil geometry (chord = 1.0):

```bash
python3 generate_foil_geometry.py --chord 1.0 --num_points 128 --output foil.vertex
```

Or create manually (simple ellipse approximation):
```python
import numpy as np

# Simple ellipse (2:1 aspect ratio)
theta = np.linspace(0, 2*np.pi, 128, endpoint=False)
x = 0.5 * np.cos(theta)  # Semi-major axis = 0.5 → chord = 1.0
y = 0.05 * np.sin(theta)  # Thickness = 10% chord

# Translate so leading edge at x=0
x = x + 0.5

# Save to vertex file
with open('foil.vertex', 'w') as f:
    f.write(f"{len(x)}\n")
    for xi, yi in zip(x, y):
        f.write(f"{xi} {yi}\n")
```

## Step 2: Modify `example.cpp`

Add FlappingFoilKinematics to your main simulation file:

```cpp
// At top of file, add:
#include "FlappingFoilKinematics.h"

// In main(), replace IBEELKinematics with FlappingFoilKinematics:

// Create kinematics object
Pointer<FlappingFoilKinematics> foil_kinematics =
    new FlappingFoilKinematics(
        "flapping_foil",
        input_db->getDatabase("ConstraintIBKinematics")->getDatabase("flapping_foil"),
        ib_method_ops->getLDataManager(),
        grid_geometry);

// Register with IB method
ib_method_ops->registerConstraintIBKinematics(foil_kinematics);
```

**Full integration** (already done if using provided `example.cpp`):
- Navier-Stokes integrator ✓
- AdvDiff integrator ✓
- Odor source registration ✓
- VisIt writer ✓

## Step 3: Update CMakeLists.txt

Add FlappingFoilKinematics to build:

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.15)
project(OdorPlumeNavigation)

# Find IBAMR
find_package(IBAMR REQUIRED)

# Add executable
add_executable(main2d
    example.cpp
    FlappingFoilKinematics.cpp
    IBEELKinematics.cpp  # Keep if you want both
)

# Link IBAMR
target_link_libraries(main2d IBAMR::IBAMR2d)
```

## Step 4: Build

```bash
mkdir -p build
cd build
cmake .. --debug-output
make -j4
cd ..
```

**Troubleshooting**:
- If IBAMR not found: `export CMAKE_PREFIX_PATH=/path/to/ibamr/install`
- If compilation errors: Check IBAMR version ≥ 0.12

## Step 5: Run Simulation

### Quick test (low resolution, 2 cores):
```bash
# Modify input file for quick test
sed -i 's/N = 128/N = 32/' input2d_lei_odor_plume
sed -i 's/END_TIME = 20.0/END_TIME = 2.0/' input2d_lei_odor_plume

# Run
mpirun -np 2 ./build/main2d input2d_lei_odor_plume
```

### Production run (high resolution, 8 cores):
```bash
# Use original settings
mpirun -np 8 ./build/main2d input2d_lei_odor_plume
```

**Expected runtime**:
- Quick test (N=32, 2.0s): ~10 minutes
- Production (N=128, 20.0s): ~4-8 hours on 8 cores

## Step 6: Monitor Progress

```bash
# Watch log file
tail -f odor_plume_lei.log

# Check output directories
ls -lh viz_odor_plume/
ls -lh FlappingFoil/

# Check mass conservation
grep "Mass conservation" odor_plume_lei.log
```

**Key indicators**:
- Timestep: Should be ~0.001-0.01
- CFL number: Should be < 0.3
- Mass conservation error: Should be < 1e-6

## Step 7: Visualize Results

### Using Python analysis script:
```bash
python3 analyze_odor_plume_lei.py \
    --data_dir viz_odor_plume \
    --frequency 0.5 \
    --dt_output 0.04 \
    --num_frames 200 \
    --num_phase_bins 8 \
    --output_dir plots
```

**Output**:
- `plots/phase_resolved_concentration.png` - Concentration at 8 phases
- `plots/plume_width_evolution.png` - Plume spreading over time
- `plots/centerline_concentration.png` - Concentration along y=0
- `plots/odor_plume_stats.json` - Quantitative statistics

### Using VisIt (interactive):
```bash
visit -o viz_odor_plume/dumps.visit
```

**Recommended plots in VisIt**:
1. **Pseudocolor(C)** - Odor concentration (use "viridis" colormap)
2. **Vector(U_x, U_y)** - Velocity field
3. **Pseudocolor(Omega)** - Vorticity (use "RdBu" colormap)
4. **Mesh** - Add Lagrangian mesh to show foil

## Step 8: Parameter Sweep

To reproduce different cases from Lei et al.:

### Case 1: High Strouhal (thrust-producing)
```bash
# Edit input2d_lei_odor_plume:
FREQUENCY = 0.5
HEAVE_AMPLITUDE = 0.2
PITCH_AMPLITUDE = 15.0
# → St ≈ 0.3
```

### Case 2: Low Strouhal (drag-producing)
```bash
FREQUENCY = 0.3
HEAVE_AMPLITUDE = 0.1
PITCH_AMPLITUDE = 5.0
# → St ≈ 0.15
```

### Case 3: High Schmidt number
```bash
SCHMIDT = 1000.0  # Instead of 100
# May need finer grid: N = 256
```

Run each case:
```bash
mpirun -np 8 ./build/main2d input2d_lei_case1
mpirun -np 8 ./build/main2d input2d_lei_case2
mpirun -np 8 ./build/main2d input2d_lei_case3
```

## Step 9: Post-Processing Checklist

After simulation completes, verify:

- [ ] Total simulation time reached END_TIME
- [ ] Mass conservation error < 1e-6
- [ ] VTK files contain C, U_x, U_y, Omega
- [ ] Vortex street visible in Omega field
- [ ] Odor plume extends downstream
- [ ] Phase-resolved averages show clear modulation
- [ ] Statistics JSON file generated

## Common Issues and Solutions

### Issue 1: Solver diverges (NaN values)

**Solution**: Reduce timestep
```bash
# In input file:
DT_MAX = 0.005  # Instead of 0.01
CFL_MAX = 0.2   # Instead of 0.3
```

### Issue 2: No odor in output

**Solution**: Check odor source is registered
```cpp
// In example.cpp, ensure this is present:
Pointer<CartGridFunction> odor_source_fcn = new muParserCartGridFunction(...);
adv_diff_integrator->setSourceTerm(C_var, odor_source_fcn);
```

### Issue 3: Vortex street not visible

**Solution**: Check Reynolds number and vorticity tagging
```bash
# In input file:
Re = 1000.0           # Not too low
VORTICITY_TAGGING = TRUE
TAG_BUFFER = 2
```

### Issue 4: Simulation too slow

**Solution**: Reduce resolution or use more cores
```bash
# Option 1: Lower resolution
N = 64  # Instead of 128

# Option 2: More cores
mpirun -np 16 ./build/main2d input2d_lei_odor_plume

# Option 3: Reduce end time for testing
END_TIME = 5.0  # Just 2-3 flapping cycles
```

### Issue 5: Python analysis fails

**Solution**: Install dependencies
```bash
pip install numpy matplotlib pyvista scipy

# If pyvista fails:
pip install pyvista --upgrade
```

## Expected Results

After running successfully, you should observe:

1. **Vortex street**: Clear alternating vortices in wake (visible in Omega)
2. **Odor modulation**: Concentration varies with flapping phase
3. **Enhanced dispersion**: Plume width grows faster than pure diffusion
4. **Conditional statistics**: Higher concentration in vortex cores
5. **Phase-resolved structure**: Distinct plume patterns at different phases

**Quantitative checks** (from Lei et al.):
- Strouhal number St ≈ 0.2-0.4
- Vortex spacing λ ≈ U/f ≈ 2.0 (for f=0.5, U=1.0)
- Plume enhancement factor ≈ 2-5× compared to pure diffusion

## Next Steps

**Scientific questions to explore**:

1. How does Strouhal number affect odor landscape?
   - Vary frequency and amplitude
   - Compare thrust vs. drag producing wakes

2. How does Schmidt number affect plume structure?
   - Sc = 1, 10, 100, 1000
   - Measure concentration gradients

3. What is optimal sensor placement for odor detection?
   - Analyze phase-resolved fields
   - Compute probability of detection

4. How does flapping amplitude affect mixing?
   - Measure effective diffusivity
   - Compare with quiescent flow

## Files Overview

```
Four_fish_school/
├── README_LEI_ODOR_PLUME_NAVIGATION.md   # Full documentation
├── QUICKSTART_LEI_ODOR_PLUME.md          # This file
├── example.cpp                            # Main simulation (modify)
├── FlappingFoilKinematics.cpp             # Kinematics implementation
├── FlappingFoilKinematics.h               # Kinematics header
├── input2d_lei_odor_plume                 # Input configuration
├── foil.vertex                            # Foil geometry
├── CMakeLists.txt                         # Build configuration
├── analyze_odor_plume_lei.py              # Post-processing script
└── build/                                 # Build directory
    └── main2d                             # Executable
```

## Support and References

**IBAMR help**:
- Documentation: https://ibamr.github.io/
- GitHub: https://github.com/IBAMR/IBAMR
- Google Group: https://groups.google.com/g/ibamr-users

**Lei et al. paper**:
- DOI: https://doi.org/10.2514/6.2021-2817
- Title: "Navigation in odor plumes: How do the flapping kinematics modulate the odor landscape?"

**Related work**:
- Kamran et al. (2024): arXiv:2408.16136 (chemotaxis in fish schools)
- Crimaldi & Koseff (2001): Exp. Fluids 31:90-102 (turbulent plume structure)

---

**Quick Start Complete!**

You should now be able to:
✓ Build the simulation
✓ Run Lei et al. odor plume cases
✓ Visualize and analyze results
✓ Modify parameters for exploration

For detailed implementation guide, see `README_LEI_ODOR_PLUME_NAVIGATION.md`.
