# Implementation Guide: Lei et al. (2021) Odor Plume Navigation with Flapping Kinematics

## Reference
**Paper**: "Navigation in odor plumes: How do the flapping kinematics modulate the odor landscape?"
**Authors**: Menglong Lei, John P. Crimaldi, Chengyu Li
**DOI**: https://doi.org/10.2514/6.2021-2817
**Conference**: AIAA Aviation 2021 Forum
**Session**: Low-Reynolds-Number and Bio-Inspired Flows I

## Overview

This guide provides step-by-step instructions for implementing the Lei et al. odor plume study in **IBAMR** (Immersed Boundary Adaptive Mesh Refinement). The implementation couples:

1. **Prescribed flapping body** (immersed boundary with kinematics)
2. **Incompressible Navier-Stokes flow** (fluid dynamics around flapping body)
3. **Passive scalar advection-diffusion** (odor transport)
4. **Odor source on/near body** (chemical release)
5. **Post-processing** (plume structure, phase-resolved statistics)

**One-line summary**: Prescribed flapping body → incompressible flow → odor advection-diffusion with source → plume analysis

---

## Table of Contents

1. [Physical Problem](#1-physical-problem)
2. [Governing Equations](#2-governing-equations)
3. [IBAMR Framework](#3-ibamr-framework)
4. [Implementation Steps](#4-implementation-steps)
5. [Code Structure](#5-code-structure)
6. [Configuration Parameters](#6-configuration-parameters)
7. [Post-Processing](#7-post-processing)
8. [Validation](#8-validation)
9. [Advanced Topics](#9-advanced-topics)

---

## 1. Physical Problem

### 1.1 Scientific Question

**How do flapping kinematics modulate the odor landscape around swimming/flying animals?**

- Animals (fish, insects, crustaceans) use flapping propulsion
- They navigate using chemical cues (odors)
- Their own motion creates vortices that deform odor plumes
- Understanding this helps explain chemosensory navigation strategies

### 1.2 Key Features

1. **Flapping body**: Periodic heaving/pitching motion (prescribed kinematics)
2. **Wake vortices**: Von Kármán vortex street or reverse von Kármán
3. **Odor source**: Chemical released from body surface or upstream source
4. **Odor transport**: Convection by vortices + molecular diffusion
5. **Phase dependence**: Odor concentration varies with flapping phase

### 1.3 Dimensionless Parameters

| Parameter | Symbol | Definition | Typical Range | Physical Meaning |
|-----------|--------|------------|---------------|------------------|
| **Reynolds number** | Re | ρUL/μ | 100-5000 | Inertial vs viscous forces |
| **Strouhal number** | St | fA/U | 0.2-0.4 | Flapping frequency × amplitude / speed |
| **Schmidt number** | Sc | ν/D | 100-1000 | Momentum vs mass diffusivity |
| **Péclet number** | Pe | UL/D | 10⁴-10⁶ | Advection vs diffusion |

Where:
- U = swimming speed (or free-stream velocity)
- L = body length (or chord)
- f = flapping frequency
- A = flapping amplitude
- ν = kinematic viscosity
- D = molecular diffusivity

---

## 2. Governing Equations

### 2.1 Fluid Dynamics (Incompressible Navier-Stokes)

**Continuity equation** (mass conservation):
```
∇·u = 0
```

**Momentum equation**:
```
∂u/∂t + u·∇u = -∇p/ρ + ν∇²u + f_IB
```

where:
- **u** = fluid velocity
- **p** = pressure
- **ρ** = fluid density
- **ν** = kinematic viscosity
- **f_IB** = immersed boundary force (from flapping body)

### 2.2 Odor Transport (Advection-Diffusion)

**Scalar transport equation**:
```
∂C/∂t + u·∇C = D∇²C + S
```

where:
- **C** = odor concentration
- **D** = molecular diffusivity (D = ν/Sc)
- **S** = source term (odor release from body)

**Boundary conditions**:
- Far-field: C → 0 (or background concentration)
- Body surface: Fixed concentration or flux condition

### 2.3 Immersed Boundary Method

**Lagrangian-Eulerian coupling**:
```
f_IB(x,t) = ∫ F(s,t) δ(x - X(s,t)) ds
```

where:
- **X(s,t)** = Lagrangian marker positions (body surface)
- **F(s,t)** = Lagrangian force density
- **δ** = Dirac delta function (regularized)
- **s** = Lagrangian coordinate along body

**Prescribed kinematics**: X(s,t) is specified (not computed from forces)

---

## 3. IBAMR Framework

### 3.1 Key Components

IBAMR provides the following integrators and methods:

| Component | IBAMR Class | Purpose |
|-----------|-------------|---------|
| **Navier-Stokes solver** | `INSStaggeredHierarchyIntegrator` | Incompressible flow |
| **Immersed boundary** | `ConstraintIBMethod` | Prescribed body kinematics |
| **Scalar transport** | `AdvDiffHierarchyIntegrator` | Odor advection-diffusion |
| **Grid management** | `PatchHierarchy` | Adaptive mesh refinement |
| **Kinematics** | Custom class (e.g., `IBEELKinematics`) | Define body motion |

### 3.2 Integration Strategy

**Time-stepping sequence** (each timestep):

1. Update Lagrangian positions: X^(n+1) = X^n + kinematics
2. Spread IB force: f_IB = spread(F)
3. Advance Navier-Stokes: solve for u^(n+1), p^(n+1)
4. Advance scalar transport: solve for C^(n+1)
5. Output data and diagnostics

**Coupling**:
- Navier-Stokes → AdvDiff: velocity field u
- Body kinematics → AdvDiff: source location/strength
- One-way coupling (odor doesn't affect flow)

---

## 4. Implementation Steps

### Step 1: Create Flapping Body Kinematics Class

**Goal**: Define prescribed motion for flapping foil/body

**Base class**: Inherit from `IBAMR::ConstraintIBKinematics`

**Required methods**:
```cpp
class FlappingFoilKinematics : public ConstraintIBKinematics
{
public:
    // Set shape at current time
    void setKinematicsVelocity(
        const double time,
        const std::vector<double>& incremented_angle_from_reference_axis,
        const std::vector<double>& center_of_mass,
        const std::vector<double>& tagged_pt_position) override;

    // Set deformation velocity
    void setShape(
        const double time,
        const std::vector<double>& incremented_angle_from_reference_axis) override;

    // Get COM velocity
    void getShape(
        const double time,
        std::vector<double>& shape) override;
};
```

**Example: Pitching foil**
```cpp
void FlappingFoilKinematics::setKinematicsVelocity(
    const double time,
    const std::vector<double>& /*incremented_angle_from_reference_axis*/,
    const std::vector<double>& center_of_mass,
    const std::vector<double>& /*tagged_pt_position*/)
{
    // Pitching motion: θ(t) = θ_0 sin(2πft)
    const double f = d_frequency;        // Flapping frequency
    const double theta_0 = d_amplitude;  // Pitch amplitude (radians)
    const double omega = 2.0 * M_PI * f;

    // Current pitch angle
    const double theta = theta_0 * std::sin(omega * time);

    // Pitch rate (angular velocity)
    const double theta_dot = theta_0 * omega * std::cos(omega * time);

    // Set deformation velocity (rotation about pivot point)
    // For each Lagrangian point X_i:
    //   V_i = θ̇ × (X_i - X_pivot)

    // Store in d_kinematics_vel (implementation detail)
    d_current_time = time;
    d_new_kinematics_vel[2] = theta_dot;  // Angular velocity (z-component in 2D)
}
```

**Example: Heaving + pitching (combined motion)**
```cpp
void FlappingFoilKinematics::setKinematicsVelocity(
    const double time,
    const std::vector<double>& /*incremented_angle_from_reference_axis*/,
    const std::vector<double>& center_of_mass,
    const std::vector<double>& /*tagged_pt_position*/)
{
    const double f = d_frequency;
    const double omega = 2.0 * M_PI * f;
    const double phi = d_phase_offset;  // Phase between heave and pitch

    // Heaving motion (vertical translation)
    const double h_0 = d_heave_amplitude;
    const double h = h_0 * std::sin(omega * time);
    const double h_dot = h_0 * omega * std::cos(omega * time);

    // Pitching motion (rotation)
    const double theta_0 = d_pitch_amplitude;
    const double theta = theta_0 * std::sin(omega * time + phi);
    const double theta_dot = theta_0 * omega * std::cos(omega * time + phi);

    // Set translational velocity (COM)
    d_new_kinematics_vel[0] = 0.0;       // No horizontal motion
    d_new_kinematics_vel[1] = h_dot;     // Vertical heaving
    d_new_kinematics_vel[2] = theta_dot; // Pitching

    d_current_time = time;
}
```

**Parameter selection** (from Lei et al.):
- **St = 0.2-0.4**: Optimal for thrust generation
- **Re = 300-3000**: Low-to-moderate Reynolds number
- **Amplitude**: Typically 0.1-0.3 chord lengths

---

### Step 2: Set Up Navier-Stokes Solver

**In `example.cpp`**:

```cpp
// Create Navier-Stokes integrator
Pointer<INSStaggeredHierarchyIntegrator> navier_stokes_integrator =
    new INSStaggeredHierarchyIntegrator(
        "INSStaggeredHierarchyIntegrator",
        app_initializer->getComponentDatabase("INSStaggeredHierarchyIntegrator"));

// Create IB method
Pointer<ConstraintIBMethod> ib_method_ops =
    new ConstraintIBMethod(
        "ConstraintIBMethod",
        app_initializer->getComponentDatabase("ConstraintIBMethod"));

// Register IB method with Navier-Stokes
navier_stokes_integrator->registerBodyForceFunction(
    new IBMethodBodyForceFunction(ib_method_ops));
```

**In `input2d`**:

```
// Reynolds number and viscosity
Re = 1000.0
MU = 1.0 / Re
RHO = 1.0

// Solver parameters
INSStaggeredHierarchyIntegrator {
   mu = MU
   rho = RHO

   start_time = 0.0
   end_time = 20.0        // ~10 flapping cycles for St=0.3, f=0.5

   cfl = 0.3
   dt_max = 0.01

   enable_logging = TRUE

   // Output variables
   output_U = TRUE        // Velocity
   output_P = TRUE        // Pressure
   output_F = TRUE        // IB force
   output_Omega = TRUE    // Vorticity
   output_Div_U = TRUE    // Divergence (should be ~0)

   // Numerical schemes
   convective_op_type = "PPM"              // Piecewise Parabolic Method
   convective_difference_form = "ADVECTIVE"

   // Pressure solver
   normalize_pressure = TRUE
}
```

**Domain and boundary conditions**:

```
CartesianGeometry {
   domain_boxes = [(0,0), (8*N-1, 4*N-1)]

   // Domain size: 8L × 4L (L = chord length)
   x_lo = -2.0, -2.0
   x_up =  6.0,  2.0

   // Periodic in y, inflow/outflow in x
   periodic_dimension = 0, 1  // (x, y)
}

// For non-periodic x (inflow/outflow):
VelocityBcCoefs_0 {
   // x-boundaries (inflow/outflow)
   acoef_function_0 = "1.0"   // Left: u = U_inf
   acoef_function_1 = "0.0"   // Right: ∂u/∂x = 0 (convective outflow)

   bcoef_function_0 = "0.0"
   bcoef_function_1 = "1.0"

   gcoef_function_0 = "1.0"   // U_inf (free-stream velocity)
   gcoef_function_1 = "0.0"
}
```

**Adaptive mesh refinement**:

```
GriddingAlgorithm {
   max_levels = 3           // 3 AMR levels
   ratio_to_coarser {
      level_1 = 4,4         // 4x refinement
      level_2 = 4,4
   }

   largest_patch_size {
      level_0 = 512,512
   }

   smallest_patch_size {
      level_0 = 4,4
   }

   // Tagging strategy
   tagging_method = "GRADIENT_DETECTOR"
}

StandardTagAndInitialize {
   tagging_method = "GRADIENT_DETECTOR"

   // Refine based on vorticity
   RefineBoxes {
      level_0_tags = "VORTICITY"  // Tag high vorticity regions
   }
}
```

---

### Step 3: Add Advection-Diffusion Integrator (Odor Transport)

**In `example.cpp`** (after Navier-Stokes setup):

```cpp
// Create advection-diffusion integrator for odor transport
Pointer<AdvDiffHierarchyIntegrator> adv_diff_integrator =
    new AdvDiffHierarchyIntegrator(
        "AdvDiffHierarchyIntegrator",
        app_initializer->getComponentDatabase("AdvDiffHierarchyIntegrator"));

// Set advection velocity (from Navier-Stokes)
adv_diff_integrator->setAdvectionVelocity(
    navier_stokes_integrator->getAdvectionVelocityVariable());

// Register with Navier-Stokes (for coupled time-stepping)
navier_stokes_integrator->registerAdvDiffHierarchyIntegrator(adv_diff_integrator);

// Create variable for odor concentration
Pointer<CellVariable<NDIM, double>> C_var = new CellVariable<NDIM, double>("C");
adv_diff_integrator->registerTransportedQuantity(C_var);

// Set diffusion coefficient
adv_diff_integrator->setDiffusionCoefficient(C_var, D);  // D = ν/Sc

// Register with VisIt for visualization
Pointer<VisItDataWriter<NDIM>> visit_data_writer = app_initializer->getVisItDataWriter();
if (visit_data_writer)
{
    adv_diff_integrator->registerVisItDataWriter(visit_data_writer);
}
```

**In `input2d`**:

```
// Odor transport parameters
SCHMIDT = 100.0                    // Schmidt number
KAPPA = MU / (RHO * SCHMIDT)       // Diffusion coefficient D = ν/Sc

AdvDiffHierarchyIntegrator {
   start_time = 0.0
   end_time = 20.0

   // Numerical schemes
   convective_op_type = "PPM"                  // Same as Navier-Stokes
   convective_difference_form = "CONSERVATIVE"  // For mass conservation

   // Diffusion solver (implicit)
   diffusion_time_stepping_type = "BACKWARD_EULER"

   cfl = 0.5
   dt_max = 0.01

   enable_logging = TRUE
}

// Initial condition: Gaussian blob
OdorInitialConditions {
   // Gaussian centered at (-1.0, 0.0) upstream of foil
   function_0 = "1.0 * exp(-((X_0 + 1.0)^2 + X_1^2) / (2.0 * 0.2^2))"
}

// Boundary conditions
OdorBcCoefs {
   // Neumann (zero flux) at all boundaries
   acoef_function_0 = "0.0"
   acoef_function_1 = "0.0"
   acoef_function_2 = "0.0"
   acoef_function_3 = "0.0"

   bcoef_function_0 = "1.0"
   bcoef_function_1 = "1.0"
   bcoef_function_2 = "1.0"
   bcoef_function_3 = "1.0"

   gcoef_function_0 = "0.0"
   gcoef_function_1 = "0.0"
   gcoef_function_2 = "0.0"
   gcoef_function_3 = "0.0"
}
```

**Schmidt number considerations**:
- **Sc = 1**: Momentum and mass diffuse at same rate (gases)
- **Sc = 100-1000**: Typical for odors in water (mass diffuses slowly)
- **Sc > 1000**: Very sharp concentration gradients → need fine grid

**Grid resolution** for scalar:
```
Δx ≲ δ_c = D·T = (ν/Sc)·T
```
where T is characteristic time scale (1/f for flapping).

---

### Step 4: Implement Odor Source Term

**Option A: Fixed Eulerian Source** (easier)

Add source term in `input2d`:

```cpp
// In example.cpp, register source function
Pointer<CartGridFunction> odor_source_fcn =
    new muParserCartGridFunction(
        "odor_source",
        app_initializer->getComponentDatabase("OdorSource"),
        grid_geometry);

adv_diff_integrator->setSourceTerm(C_var, odor_source_fcn);
```

```
// In input2d
OdorSource {
   // Gaussian source centered at foil leading edge (x=0, y=0)
   // Source strength Q = 1.0, width σ = 0.1
   function = "1.0 * exp(-(X_0^2 + X_1^2) / (2.0 * 0.1^2))"
}
```

**Option B: Lagrangian Source** (more accurate, body-attached)

Spread source from IB markers to Eulerian grid:

```cpp
// In example.cpp, in main time-stepping loop
void add_lagrangian_odor_source(
    Pointer<PatchHierarchy<NDIM>> patch_hierarchy,
    Pointer<AdvDiffHierarchyIntegrator> adv_diff_integrator,
    LDataManager* l_data_manager,
    const double time,
    const double dt)
{
    // Get Lagrangian data
    Pointer<LData> X_data = l_data_manager->getLData("X", /*current_time*/);

    // Source strength per Lagrangian point
    const double Q_per_marker = 0.01;  // Adjust based on desired total flux

    // Get odor concentration variable
    VariableDatabase<NDIM>* var_db = VariableDatabase<NDIM>::getDatabase();
    Pointer<CellVariable<NDIM, double>> C_var = var_db->getVariable("C");

    // Spread source from Lagrangian to Eulerian
    // (Use same spreading kernel as IB force)
    const std::string& kernel_name = "IB_4";  // 4-point delta function

    // For each Lagrangian marker:
    for (int k = 0; k < X_data->getGhostedLocalNodeCount(); ++k)
    {
        // Get marker position
        const double* const X = X_data->getGhostedLocalFormVecArray();
        const double x = X[NDIM*k];
        const double y = X[NDIM*k + 1];

        // Spread Gaussian to nearby Eulerian points
        // S(X_eulerian) += Q * δ_h(X_eulerian - X_lagrangian) * ds
        // (Implementation uses IBTK spreading operator)
    }

    // Add to RHS of advection-diffusion equation
    adv_diff_integrator->addSourceTerm(C_var, /*source_patch_data*/);
}
```

**Option C: Fixed Concentration Boundary** (for body-released odor)

Set Dirichlet BC on body surface:

```
// Near body surface: C = C_0 (fixed concentration)
// Use IBMethod to enforce concentration on Lagrangian markers
// then spread to Eulerian grid
```

**Recommended**: Start with **Option A** (fixed Eulerian source) for simplicity, then move to **Option B** for production runs.

---

### Step 5: Run Coupled Simulation

**Build**:
```bash
mkdir build && cd build
cmake .. --debug-output
make -j4
cd ..
```

**Run**:
```bash
# Serial
./build/main2d input2d

# Parallel (8 processes)
mpirun -np 8 ./build/main2d input2d
```

**Expected output**:
```
viz_odor_plume/
├── dumps.visit
└── visit_dump_000*.vtk
    ├── U_x.vtk           # Velocity x-component
    ├── U_y.vtk           # Velocity y-component
    ├── Omega.vtk         # Vorticity
    ├── P.vtk             # Pressure
    └── C.vtk             # ODOR CONCENTRATION
```

**Monitoring**:
```bash
# Watch log file
tail -f odor_plume.log

# Check mass conservation
grep "Mass conservation" odor_plume.log
```

---

## 5. Code Structure

### 5.1 Directory Layout

```
odor_plume_navigation/
├── example.cpp                      # Main simulation (modify existing)
├── FlappingFoilKinematics.cpp       # New: flapping kinematics
├── FlappingFoilKinematics.h         # New: header
├── input2d_odor_plume               # New: input file for Lei et al. case
├── foil.vertex                      # Foil geometry (Lagrangian markers)
├── CMakeLists.txt                   # Build configuration
├── postprocess/
│   ├── analyze_plume.py             # Phase-resolved averaging
│   ├── plot_concentration.py        # Visualization
│   └── compute_statistics.py        # Variance, intermittency
└── README_LEI_ODOR_PLUME.md         # This file
```

### 5.2 Modifying Existing Code

**From current `example.cpp`** (four fish school):

1. **Replace** `IBEELKinematics` with `FlappingFoilKinematics`
2. **Keep** Navier-Stokes setup (INSStaggeredHierarchyIntegrator)
3. **Keep** AdvDiff setup (already implemented)
4. **Add** odor source term registration
5. **Modify** domain size (smaller for single foil)

**From current `input2d`**:

1. **Keep** Re, Sc parameters
2. **Modify** kinematics section:
   ```
   ConstraintIBKinematics {
       flapping_foil {
           structure_names = "foil"
           structure_levels = MAX_LEVELS - 1

           frequency = 0.5           # Flapping frequency
           heave_amplitude = 0.2     # Heave amplitude / chord
           pitch_amplitude = 15.0    # Pitch amplitude (degrees)
           phase_offset = 90.0       # Phase between heave/pitch (deg)

           # Computed Strouhal: St = f*A/U_inf
       }
   }
   ```

---

## 6. Configuration Parameters

### 6.1 Lei et al. Canonical Cases

Based on the paper, here are typical parameter sets:

**Case 1: Thrust-producing (reverse von Kármán)**
```
Re = 1000
St = 0.3
heave_amplitude = 0.2 * chord
pitch_amplitude = 15° (0.262 rad)
phase_offset = 90° (heave leads pitch)
Sc = 100
```

**Case 2: Drag-producing (von Kármán vortex street)**
```
Re = 1000
St = 0.15
heave_amplitude = 0.1 * chord
pitch_amplitude = 5° (0.087 rad)
phase_offset = 90°
Sc = 100
```

**Case 3: High Schmidt number**
```
Re = 1000
St = 0.3
heave_amplitude = 0.2 * chord
pitch_amplitude = 15°
phase_offset = 90°
Sc = 1000  # Sharp concentration gradients
```

### 6.2 Grid Resolution Guidelines

**For Re = 1000, Sc = 100**:

| Region | Resolution | Rationale |
|--------|------------|-----------|
| **Near body** | Δx/L ≈ 0.01 | Resolve boundary layer |
| **Wake** | Δx/L ≈ 0.02 | Capture vortices |
| **Far-field** | Δx/L ≈ 0.05 | Background flow |

**Base grid**: N = 64 → domain 8L × 4L → Δx ≈ 0.125L
**Refinement**: 3 levels, ratio 4 → finest Δx ≈ 0.008L ✓

**Schmidt number constraint**:
```
Δx ≲ δ_c ≈ √(D·T) = √(ν·T/Sc)

For Sc = 100, T = 1/f = 2.0:
δ_c ≈ √(0.001 · 2.0 / 100) ≈ 0.004
→ Need Δx < 0.004 → Use finest level (Δx ≈ 0.008) marginally OK
→ For Sc = 1000, may need 4 levels
```

---

## 7. Post-Processing

### 7.1 Loading Data (Python)

```python
import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt

def load_frame(frame_idx):
    """Load velocity and concentration from VTK"""
    base_path = f"viz_odor_plume/visit_dump_{frame_idx:04d}/"

    # Load velocity
    u_x = pv.read(base_path + "U_x.vtk")
    u_y = pv.read(base_path + "U_y.vtk")

    # Load concentration
    C = pv.read(base_path + "C.vtk")

    # Load vorticity
    omega = pv.read(base_path + "Omega.vtk")

    return u_x, u_y, C, omega

# Example: Load frame 100
u_x, u_y, C, omega = load_frame(100)

# Extract arrays
C_array = C["C"]  # Concentration values
omega_array = omega["Omega"]  # Vorticity
```

### 7.2 Phase-Resolved Averaging

**Goal**: Average odor field at same phase of flapping cycle

```python
def phase_resolved_average(num_frames, frequency, dt_output):
    """
    Compute <C>(x, y, φ) where φ is flapping phase
    """
    # Determine phase for each frame
    phases = []
    C_fields = []

    for frame_idx in range(num_frames):
        t = frame_idx * dt_output
        phase = (2 * np.pi * frequency * t) % (2 * np.pi)

        _, _, C, _ = load_frame(frame_idx)

        phases.append(phase)
        C_fields.append(C["C"])

    # Bin by phase (e.g., 8 bins)
    num_bins = 8
    phase_bins = np.linspace(0, 2*np.pi, num_bins+1)

    C_avg = np.zeros((num_bins, *C_fields[0].shape))
    counts = np.zeros(num_bins)

    for phase, C_field in zip(phases, C_fields):
        bin_idx = np.digitize(phase, phase_bins) - 1
        if 0 <= bin_idx < num_bins:
            C_avg[bin_idx] += C_field
            counts[bin_idx] += 1

    # Average
    for i in range(num_bins):
        if counts[i] > 0:
            C_avg[i] /= counts[i]

    return C_avg, phase_bins

# Compute phase-resolved average
C_avg, phase_bins = phase_resolved_average(200, frequency=0.5, dt_output=0.04)

# Plot concentration at φ = π/2
plt.figure(figsize=(10, 5))
plt.contourf(C_avg[2], levels=20, cmap='viridis')
plt.colorbar(label='<C>(φ=π/2)')
plt.title('Phase-resolved odor concentration at φ=π/2')
plt.show()
```

### 7.3 Plume Statistics

**Variance** (measure of concentration fluctuations):
```python
def compute_variance(C_fields):
    """Compute spatial variance of concentration"""
    C_mean = np.mean(C_fields, axis=0)
    C_var = np.mean((C_fields - C_mean)**2, axis=0)
    return C_var

variance_field = compute_variance(C_fields)
```

**Intermittency** (filament structure):
```python
def compute_intermittency(C_fields, threshold):
    """Fraction of time C > threshold"""
    return np.mean(C_fields > threshold, axis=0)

intermittency = compute_intermittency(C_fields, threshold=0.5)
```

**Centerline concentration**:
```python
def extract_centerline(C, y_center=0.0):
    """Extract concentration along y=0"""
    # Find grid points near y=0
    grid_y = C.points[:, 1]
    mask = np.abs(grid_y - y_center) < 0.05

    x_centerline = C.points[mask, 0]
    C_centerline = C["C"][mask]

    # Sort by x
    sort_idx = np.argsort(x_centerline)

    return x_centerline[sort_idx], C_centerline[sort_idx]

x_cl, C_cl = extract_centerline(C)

plt.figure()
plt.plot(x_cl, C_cl, 'b-', linewidth=2)
plt.xlabel('x/L')
plt.ylabel('C')
plt.title('Centerline concentration profile')
plt.grid(True)
plt.show()
```

### 7.4 Conditional Statistics

**Concentration conditioned on vorticity sign**:
```python
def conditional_average(C_array, omega_array):
    """Average C conditioned on vortex sign"""
    C_in_positive_vortex = C_array[omega_array > 0].mean()
    C_in_negative_vortex = C_array[omega_array < 0].mean()

    return C_in_positive_vortex, C_in_negative_vortex

C_pos, C_neg = conditional_average(C_array, omega_array)
print(f"<C | ω>0> = {C_pos:.3f}")
print(f"<C | ω<0> = {C_neg:.3f}")
```

---

## 8. Validation

### 8.1 Convergence Tests

**Grid convergence**:
```bash
# Run with 3 grid resolutions
N=32:  run with N=32, MAX_LEVELS=3 → finest Δx = 32/4³ = 0.5
N=64:  run with N=64, MAX_LEVELS=3 → finest Δx = 64/4³ = 1.0
N=128: run with N=128, MAX_LEVELS=3 → finest Δx = 128/4³ = 2.0

# Compare centerline concentration profiles
# Expect convergence at O(Δx²) for diffusion, O(Δx) for convection
```

**Temporal convergence**:
```bash
# Run with 3 timesteps
dt_max = 0.02
dt_max = 0.01
dt_max = 0.005

# Compare time-averaged concentration
# Expect convergence at O(Δt²) for Crank-Nicolson
```

### 8.2 Physical Validation

**Mass conservation**:
```python
def check_mass_conservation(C_fields, dx, dy):
    """Check total mass over time"""
    masses = []
    for C in C_fields:
        total_mass = np.sum(C) * dx * dy
        masses.append(total_mass)

    mass_error = (np.max(masses) - np.min(masses)) / np.mean(masses)
    print(f"Mass conservation error: {mass_error*100:.2f}%")
    return masses

masses = check_mass_conservation(C_fields, dx=0.01, dy=0.01)
```

**Vortex street validation**:
- Check vorticity contours match literature (von Kármán for St < 0.2)
- Measure vortex spacing: λ ≈ U/f (approximately)

**Plume width growth**:
```python
def measure_plume_width(C_array, x_location):
    """Measure plume width at given x location"""
    # Extract vertical profile at x
    # Compute standard deviation
    sigma_y = np.std(C_array[x == x_location])
    return sigma_y
```

---

## 9. Advanced Topics

### 9.1 Time-Dependent Source (Moving with Body)

**Challenge**: Source moves with flapping body

**Solution**: Update source location each timestep

```cpp
// In time-stepping loop
void update_odor_source_location(
    Pointer<CartGridFunction> source_fcn,
    const double* COM,        // Center of mass from IB
    const double time)
{
    // Update source center to track body COM
    std::ostringstream source_expr;
    source_expr << "1.0 * exp(-((X_0 - " << COM[0] << ")^2 + "
                << "(X_1 - " << COM[1] << ")^2) / (2.0 * 0.1^2))";

    // Re-parse expression
    source_fcn->setDataOnPatchHierarchy(/*new expression*/);
}
```

### 9.2 Multi-Species Transport

**Example**: Track both attractant and repellent

```cpp
// Register two transported quantities
Pointer<CellVariable<NDIM, double>> C_attractant =
    new CellVariable<NDIM, double>("C_attractant");
Pointer<CellVariable<NDIM, double>> C_repellent =
    new CellVariable<NDIM, double>("C_repellent");

adv_diff_integrator->registerTransportedQuantity(C_attractant);
adv_diff_integrator->registerTransportedQuantity(C_repellent);

// Set different diffusion coefficients
adv_diff_integrator->setDiffusionCoefficient(C_attractant, D_attract);
adv_diff_integrator->setDiffusionCoefficient(C_repellent, D_repel);
```

### 9.3 Reactive Transport

**Add decay/production terms**:

```
∂C/∂t + u·∇C = D∇²C - λC + R
```

where:
- λC = first-order decay (e.g., chemical degradation)
- R = production term

**Implementation**:
```cpp
// Register reaction term as source
class DecayReactionTerm : public CartGridFunction
{
public:
    void setDataOnPatch(
        const int data_idx,
        Pointer<hier::Variable<NDIM>> var,
        Pointer<hier::Patch<NDIM>> patch,
        const double data_time,
        const bool initial_time = false,
        Pointer<hier::PatchLevel<NDIM>> level = nullptr) override
    {
        // Get concentration
        Pointer<CellData<NDIM, double>> C_data = patch->getPatchData(C_idx);

        // Compute reaction: R = -λC
        for (CellIterator<NDIM> ic(patch->getBox()); ic; ic++)
        {
            const CellIndex<NDIM>& i = ic();
            double C = (*C_data)(i);
            double R = -d_decay_rate * C;
            (*reaction_data)(i) = R;
        }
    }

private:
    double d_decay_rate;
};
```

### 9.4 Chemotaxis (Two-Way Coupling)

**Feedback**: Odor affects body kinematics

**Approach**:
1. Compute odor gradient at sensor locations:
   ```cpp
   Vector2d grad_C = compute_gradient_at_point(C_data, sensor_location);
   ```

2. Modify kinematics based on gradient:
   ```cpp
   // In FlappingFoilKinematics::setKinematicsVelocity()
   double grad_C_x = sample_concentration_gradient_x(sensor_location);
   double turning_rate = alpha * grad_C_x;  // Klinokinesis

   // Adjust heading
   d_new_kinematics_vel[2] += turning_rate;  // Add to angular velocity
   ```

3. Iterate until convergence (within each timestep)

**Reference**: Kamran et al. (2024), arXiv:2408.16136

---

## 10. Troubleshooting

### Issue 1: Solver Divergence

**Symptom**: NaN or very large values in concentration

**Causes**:
- CFL number too large (convection)
- Diffusion timestep too large (rare with implicit)
- Negative concentrations

**Solutions**:
```
// Reduce timestep
dt_max = 0.005  // Instead of 0.01

// Enforce positivity
adv_diff_integrator->setConservativeConvectionDifference(true);

// Increase solver tolerance
HelmholtzHypreSolver {
   max_iterations = 1000
   relative_residual_tol = 1.0e-6
}
```

### Issue 2: Mass Not Conserved

**Symptom**: Total mass drifts over time

**Solutions**:
```
// Use conservative form
AdvDiffHierarchyIntegrator {
   convective_difference_form = "CONSERVATIVE"  // NOT "ADVECTIVE"
}

// Check boundary conditions (should be zero flux for closed domain)
OdorBcCoefs {
   // Ensure ∂C/∂n = 0 at boundaries
   bcoef_function = "1.0"
   gcoef_function = "0.0"
}
```

### Issue 3: High Schmidt Number Instability

**Symptom**: Oscillations in concentration field for Sc > 100

**Solutions**:
```
// Refine grid further
MAX_LEVELS = 4  // Instead of 3

// Use tighter solver tolerance
HelmholtzHypreSolver {
   relative_residual_tol = 1.0e-8  // Tighter
}

// Reduce timestep
dt_max = 0.001
```

### Issue 4: Vortices Not Resolved

**Symptom**: Wake looks diffused, no clear vortex street

**Solutions**:
```
// Increase Reynolds number or decrease viscosity
Re = 3000  // Instead of 1000

// Ensure vorticity tagging is enabled
StandardTagAndInitialize {
   tagging_method = "VORTICITY_DETECTOR"
}

// Check grid resolution near body
MAX_LEVELS = 3
REF_RATIO = 4
```

---

## 11. Complete Example Input File

**File: `input2d_lei_odor_plume`**

```
// =============================================================================
// Lei et al. (2021) Odor Plume Navigation - IBAMR Implementation
// =============================================================================

// Physical parameters
Re = 1000.0                        // Reynolds number
MU = 1.0 / Re                      // Dynamic viscosity
RHO = 1.0                          // Fluid density

// Odor transport parameters
SCHMIDT = 100.0                    // Schmidt number
KAPPA = MU / (RHO * SCHMIDT)       // Diffusion coefficient D = ν/Sc

// Flapping parameters
FREQUENCY = 0.5                    // Flapping frequency (Hz)
HEAVE_AMPLITUDE = 0.2              // Heave amplitude / chord
PITCH_AMPLITUDE = 0.262            // Pitch amplitude (radians) = 15°
PHASE_OFFSET = 1.571               // Phase offset (radians) = 90°

// Computed parameters
STROUHAL = FREQUENCY * HEAVE_AMPLITUDE  // St ≈ 0.1 (need U_inf for exact)

// Grid spacing parameters
MAX_LEVELS = 3
REF_RATIO  = 4, 4
N = 128                            // Base grid resolution

// Solver parameters
DELTA_FUNCTION       = "IB_4"
START_TIME           = 0.0
END_TIME             = 20.0        // 10 flapping cycles
MAX_INTEGRATOR_STEPS = 1000000
CFL_MAX              = 0.3
DT_MAX               = 0.01
VORTICITY_TAGGING    = TRUE
TAG_BUFFER           = 2

// =============================================================================
// NAVIER-STOKES SOLVER
// =============================================================================
INSStaggeredHierarchyIntegrator {
   mu  = MU
   rho = RHO

   start_time = START_TIME
   end_time = END_TIME

   cfl = CFL_MAX
   dt_max = DT_MAX

   enable_logging = TRUE

   // Output variables
   output_U = TRUE
   output_P = TRUE
   output_F = TRUE
   output_Omega = TRUE
   output_Div_U = FALSE

   // Convection scheme
   convective_op_type = "PPM"
   convective_difference_form = "ADVECTIVE"

   // Pressure solver
   normalize_pressure = TRUE

   // Viscous solver
   viscous_time_stepping_type = "BACKWARD_EULER"
}

// =============================================================================
// ADVECTION-DIFFUSION SOLVER (ODOR)
// =============================================================================
AdvDiffHierarchyIntegrator {
   start_time = START_TIME
   end_time = END_TIME

   // Convection scheme (same as Navier-Stokes)
   convective_op_type = "PPM"
   convective_difference_form = "CONSERVATIVE"

   // Diffusion scheme (implicit)
   diffusion_time_stepping_type = "BACKWARD_EULER"

   cfl = 0.5
   dt_max = DT_MAX

   enable_logging = TRUE
}

// Odor initial condition
OdorInitialConditions {
   // Gaussian blob upstream of foil
   function_0 = "1.0 * exp(-((X_0 + 2.0)^2 + X_1^2) / (2.0 * 0.3^2))"
}

// Odor boundary conditions (zero flux)
OdorBcCoefs {
   acoef_function_0 = "0.0"
   acoef_function_1 = "0.0"
   acoef_function_2 = "0.0"
   acoef_function_3 = "0.0"

   bcoef_function_0 = "1.0"
   bcoef_function_1 = "1.0"
   bcoef_function_2 = "1.0"
   bcoef_function_3 = "1.0"

   gcoef_function_0 = "0.0"
   gcoef_function_1 = "0.0"
   gcoef_function_2 = "0.0"
   gcoef_function_3 = "0.0"
}

// Odor source term
OdorSource {
   // Small Gaussian source at foil leading edge
   function = "0.5 * exp(-(X_0^2 + X_1^2) / (2.0 * 0.05^2))"
}

// =============================================================================
// IMMERSED BOUNDARY METHOD
// =============================================================================
ConstraintIBMethod {
   delta_fcn = DELTA_FUNCTION
   enable_logging = TRUE

   // Kinematics update method
   needs_divfree_velocity_u = FALSE
}

// Flapping foil kinematics
ConstraintIBKinematics {
   flapping_foil {
      structure_names = "foil"
      structure_levels = MAX_LEVELS - 1

      calculate_translational_momentum = 1, 1, 0
      calculate_rotational_momentum = 0, 0, 1

      lag_position_update_method = "CONSTRAINT_VELOCITY"

      // Kinematics parameters
      frequency = FREQUENCY
      heave_amplitude = HEAVE_AMPLITUDE
      pitch_amplitude = PITCH_AMPLITUDE
      phase_offset = PHASE_OFFSET
   }
}

// =============================================================================
// DOMAIN AND GRID
// =============================================================================
CartesianGeometry {
   domain_boxes = [(0,0), (4*N-1, 2*N-1)]

   // Domain size: 8L × 4L (L = chord = 1.0)
   x_lo = -2.0, -2.0
   x_up =  6.0,  2.0

   // Periodic in y
   periodic_dimension = 0, 1
}

GriddingAlgorithm {
   max_levels = MAX_LEVELS

   ratio_to_coarser {
      level_1 = REF_RATIO
      level_2 = REF_RATIO
   }

   largest_patch_size {
      level_0 = 512, 512
   }

   smallest_patch_size {
      level_0 = 8, 8
   }

   efficiency_tolerance = 0.85e0
   combine_efficiency = 0.85e0
}

StandardTagAndInitialize {
   tagging_method = "GRADIENT_DETECTOR"
}

LoadBalancer {
   bin_pack_method = "SPATIAL"
   max_workload_factor = 1.0
}

// =============================================================================
// VISUALIZATION
// =============================================================================
VisItDataWriter {
   dirname = "viz_odor_plume"
   visit_number_procs_per_file = 1
}

// =============================================================================
// TIMERS
// =============================================================================
TimerManager {
   print_total = TRUE
   print_threshold = 0.01
   timer_list = "IBAMR::*::*", "IBTK::*::*", "*::*::*"
}
```

---

## 12. Summary Checklist

Before running, ensure you have:

- [ ] Implemented `FlappingFoilKinematics` class (or modified `IBEELKinematics`)
- [ ] Created foil geometry file (`foil.vertex`)
- [ ] Set up Navier-Stokes integrator in `example.cpp`
- [ ] Set up AdvDiff integrator for odor transport
- [ ] Registered odor source term
- [ ] Configured `input2d` with Lei et al. parameters (Re, St, Sc)
- [ ] Set appropriate grid resolution (check Δx < δ_c for Sc)
- [ ] Enabled vorticity-based AMR
- [ ] Registered VisIt writer for visualization
- [ ] Built executable successfully
- [ ] Run test case and check outputs (C.vtk files exist)
- [ ] Verified mass conservation (check logs)
- [ ] Implemented post-processing scripts (phase-resolved averaging)

---

## 13. References

1. **Lei et al. (2021)**: "Navigation in odor plumes: How do the flapping kinematics modulate the odor landscape?" AIAA 2021-2817, https://doi.org/10.2514/6.2021-2817

2. **IBAMR Documentation**: https://ibamr.github.io/
   - AdvDiffHierarchyIntegrator API
   - ConstraintIBMethod examples
   - Navier-Stokes solver configuration

3. **Kamran et al. (2024)**: "Collective Chemotactic Behavior in Fish Schools", arXiv:2408.16136

4. **Crimaldi & Koseff (2001)**: "High-resolution measurements of the spatial and temporal scalar structure of a turbulent plume", Exp. Fluids 31:90-102

5. **Griffith & Patankar (2020)**: "Immersed Methods for Fluid-Structure Interaction", Ann. Rev. Fluid Mech. 52:421-448

---

**Document Version**: 1.0
**Last Updated**: 2025-11-16
**IBAMR Compatibility**: v0.12+
**Author**: Generated for Four Fish School project
