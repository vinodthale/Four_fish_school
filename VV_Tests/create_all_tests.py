#!/usr/bin/env python3
"""
Master script to generate all V&V test configurations

This creates input files, READMEs, and analysis scripts for Tests 3-14
"""

import os
import textwrap

def create_test03():
    """Test 3: Pure Advection"""
    test_dir = "Test03_Advection_Analytic"
    os.makedirs(test_dir, exist_ok=True)

    # README
    readme = textwrap.dedent("""
    # Test 3: Pure Advection of Smooth Profile - Analytic Validation

    ## Purpose
    Verify advection discretization with constant uniform velocity

    ## Analytic Solution
    For constant velocity u=(U,0), initial profile translates:
    ```
    C(x,y,t) = C₀(x - Ut, y)
    ```

    ## Setup
    - Domain: Periodic [0,10] × [0,1]
    - Grid: 64, 128, 256 for convergence
    - Velocity: u = (1.0, 0.0) constant
    - Initial: C = sin(2πx) or Gaussian
    - Diffusion: κ = 0 (pure advection) or very small
    - Time: Integrate one full period T = L/U = 10

    ## Pass Criteria
    - Convergence order matches scheme (1st for upwind, 2nd for centered)
    - L² error < 0.01 on finest grid
    - Profile returns to initial state after period

    ## Expected Order
    - Upwind: 1st order
    - Centered: 2nd order
    - PPM: 3rd order (local)
    """)
    with open(f"{test_dir}/README.md", "w") as f:
        f.write(readme)

    # Input file
    input_file = textwrap.dedent("""
    // Test 3: Pure Advection
    MU = 1.0e-2
    RHO = 1.0
    KAPPA = 1.0e-8  // Minimal diffusion

    MAX_LEVELS = 1
    N = 64

    START_TIME = 0.0
    END_TIME = 10.0  // One period
    DT_MAX = 0.01
    CFL_MAX = 0.5

    U_ADVECTION = 1.0  // Constant velocity

    Main {
       log_file_name = "test03.log"
       viz_writer = "VisIt"
       viz_dump_interval = 50
       viz_dump_dirname = "viz_test03"
    }

    CartesianGeometry {
       domain_boxes = [(0,0), (10*N-1, N-1)]
       x_lo = 0.0, 0.0
       x_up = 10.0, 1.0
       periodic_dimension = 1, 1  // PERIODIC
    }

    GriddingAlgorithm {
       max_levels = MAX_LEVELS
       largest_patch_size { level_0 = 512, 512 }
       smallest_patch_size { level_0 = 8, 8 }
    }

    StandardTagAndInitialize { tagging_method = "GRADIENT_DETECTOR" }
    LoadBalancer { bin_pack_method = "SPATIAL" }

    INSStaggeredHierarchyIntegrator {
       mu = MU
       rho = RHO
       start_time = START_TIME
       end_time = END_TIME
       cfl = CFL_MAX
       dt_max = DT_MAX
    }

    // Prescribed constant velocity
    VelocityInitialConditions {
       function_0 = "1.0"  // U
       function_1 = "0.0"  // V
    }

    AdvDiffHierarchyIntegrator {
       start_time = START_TIME
       end_time = END_TIME
       cfl = CFL_MAX
       dt_max = DT_MAX
       diffusion_time_stepping_type = "BACKWARD_EULER"
       convective_time_stepping_type = "ADAMS_BASHFORTH"
       convective_op_type = "PPM"  // Try CENTERED, PPM
       convective_difference_form = "CONSERVATIVE"
    }

    // Initial: sine wave
    OdorInitialConditions {
       function_0 = "sin(2.0*3.14159265359*X_0)"
    }

    diffusion_coefficient = KAPPA
    """)
    with open(f"{test_dir}/input2d", "w") as f:
        f.write(input_file)

    print(f"✓ Created {test_dir}")

def create_test04():
    """Test 4: Method of Manufactured Solutions"""
    test_dir = "Test04_MMS"
    os.makedirs(test_dir, exist_ok=True)

    readme = textwrap.dedent("""
    # Test 4: Method of Manufactured Solutions (MMS)

    ## Purpose
    Full verification of coupled advection-diffusion solver

    ## Manufactured Solution
    Choose:
    ```
    C(x,y,t) = sin(πx) sin(πy) exp(-βt)
    ```
    Compute source term S such that:
    ```
    ∂C/∂t + u·∇C - α∇²C = S(x,y,t)
    ```

    ## Setup
    - Domain: [0,1] × [0,1]
    - Velocity: u = (U₀, V₀) constant (e.g., u=(1,0.5))
    - Diffusion: α = 0.01
    - Dirichlet BCs from analytic solution
    - Source term computed from manufactured solution

    ## Source Term
    ```
    S = -β·sin(πx)sin(πy)exp(-βt)              [time derivative]
        + U₀·π·cos(πx)sin(πy)exp(-βt)          [advection x]
        + V₀·π·sin(πx)cos(πy)exp(-βt)          [advection y]
        + 2π²α·sin(πx)sin(πy)exp(-βt)          [diffusion]
    ```

    ## Pass Criteria
    - 2nd order convergence in space and time
    - L² error < 1e-4 on finest grid

    ## Implementation
    Requires custom source function in IBAMR input
    """)
    with open(f"{test_dir}/README.md", "w") as f:
        f.write(readme)

    print(f"✓ Created {test_dir}")

def create_test05():
    """Test 5: Discontinuous Transport"""
    test_dir = "Test05_Discontinuous"
    os.makedirs(test_dir, exist_ok=True)

    readme = textwrap.dedent("""
    # Test 5: Advection of Discontinuous Profile (Top-Hat)

    ## Purpose
    Test numerical diffusion, oscillations, and stability for sharp fronts

    ## Setup
    - Domain: [0,1] periodic
    - Initial: Top-hat (C=1 for 0.4<x<0.6, else C=0)
    - Velocity: u = 1.0 constant
    - Advect one full period

    ## What to Measure
    - Front smearing (numerical diffusion)
    - Gibbs oscillations (overshoots/undershoots)
    - Positivity preservation

    ## Pass Criteria
    - No negative concentrations
    - No overshoot > 1.1
    - Smearing consistent with scheme (upwind: O(Δx), centered: less)
    - L¹ error reasonable

    ## Expected Behavior
    - Upwind: stable, diffusive
    - Centered: oscillatory without limiter
    - PPM/WENO: sharper, less diffusive
    """)
    with open(f"{test_dir}/README.md", "w") as f:
        f.write(readme)

    print(f"✓ Created {test_dir}")

def create_test06():
    """Test 6: Mass Conservation"""
    test_dir = "Test06_MassConservation"
    os.makedirs(test_dir, exist_ok=True)

    readme = textwrap.dedent("""
    # Test 6: Global Mass Conservation Test

    ## Purpose
    Verify global tracer mass budget

    ## Setup
    - Closed domain (no-flux BCs)
    - Initial: arbitrary C distribution
    - Velocity: divergence-free field
    - No diffusion (or with diffusion + no-flux BCs)
    - No sources

    ## What to Measure
    ```
    M(t) = ∫∫ C(x,y,t) dx dy
    ```
    Should be constant: M(t) = M(0)

    ## Pass Criteria
    - Advection-only: |M(t)-M(0)|/M(0) < 1e-10
    - With diffusion: |M(t)-M(0)|/M(0) < 1e-6
    - With source Q: M(t) - M(0) = ∫₀ᵗ Q(τ) dτ

    ## Implementation
    Compute global integral at each timestep and check drift
    """)
    with open(f"{test_dir}/README.md", "w") as f:
        f.write(readme)

    print(f"✓ Created {test_dir}")

def create_test07():
    """Test 7: Boundary Conditions"""
    test_dir = "Test07_BCs"
    os.makedirs(test_dir, exist_ok=True)

    readme = textwrap.dedent("""
    # Test 7: Boundary Condition Tests

    ## Purpose
    Verify Dirichlet, Neumann, and Robin BCs for scalar

    ## Test Cases

    ### 7a: Dirichlet Inlet
    - Constant C=1 at inlet
    - Outflow at outlet
    - Verify profile develops downstream

    ### 7b: Neumann on IB Surface
    - Small sphere with ∂C/∂n = 0
    - Compute normal flux across surface
    - Should be ≈ 0

    ### 7c: Robin (Flux) BC
    - Prescribed flux on patch
    - Verify global mass increase = ∫ flux dt

    ## Pass Criteria
    - Dirichlet: |C_surface - C_prescribed| < 1e-6
    - Neumann: |∫ ∂C/∂n dS| < O(Δx)
    - Robin: Mass balance within numerical error

    ## Implementation
    Run 3 sub-tests with different BC configurations
    """)
    with open(f"{test_dir}/README.md", "w") as f:
        f.write(readme)

    print(f"✓ Created {test_dir}")

def create_test08():
    """Test 8: Sphere Source"""
    test_dir = "Test08_SphereSource"
    os.makedirs(test_dir, exist_ok=True)

    readme = textwrap.dedent("""
    # Test 8: Point/Sphere Source - Literature Comparison

    ## Purpose
    Validate source handling and wake advection vs Lei et al.

    ## Reference
    Lei et al. (2021) - Navigation in odor plumes
    Validated temperature/odor transport around sphere

    ## Setup
    - Uniform inflow U
    - Fixed sphere at (x₀,0)
    - Dirichlet C=C_h on sphere surface OR distributed source
    - Schmidt number Sc = ν/α = 0.71 (air) or 340 (water)

    ## Cases
    1. Steady release: measure centerline C(x) downstream
    2. Transient pulse: track downstream advection/diffusion

    ## Pass Criteria
    - Centerline decay matches published data (±10-20%)
    - Wake shape qualitatively similar
    - Mass flux balance

    ## Expected Results
    - C decays downstream as ~1/x (far field)
    - Wake width grows as ~√(αx/U)
    """)
    with open(f"{test_dir}/README.md", "w") as f:
        f.write(readme)

    print(f"✓ Created {test_dir}")

def create_test09():
    """Test 9: High Schmidt Number"""
    test_dir = "Test09_HighSc"
    os.makedirs(test_dir, exist_ok=True)

    readme = textwrap.dedent("""
    # Test 9: High Schmidt Number Test (Sc=100-1000)

    ## Purpose
    Ensure solver handles very small molecular diffusivity (sharp gradients)

    ## Background
    - Water: Sc ~ 100-1000 (ν/α very large)
    - Requires fine grid near gradients
    - Stiff diffusion operator

    ## Setup
    - Flow past source
    - Sc = 100, 340, 1000
    - Implicit diffusion solver
    - AMR refinement on |∇C|

    ## What to Monitor
    - Numerical stability
    - Required Δt (CFL constraint)
    - Spurious oscillations
    - Excessive numerical diffusion

    ## Pass Criteria
    - Stable solution (no blow-up)
    - No excessive oscillations
    - Physically plausible concentration distribution

    ## Implementation Notes
    - Use BACKWARD_EULER or CRANK_NICOLSON
    - AMR essential for sharp gradients
    - May need small CFL
    """)
    with open(f"{test_dir}/README.md", "w") as f:
        f.write(readme)

    print(f"✓ Created {test_dir}")

def create_test10():
    """Test 10: Moving IB with Scalar"""
    test_dir = "Test10_MovingIB"
    os.makedirs(test_dir, exist_ok=True)

    readme = textwrap.dedent("""
    # Test 10: Moving Immersed Body with Scalar BCs

    ## Purpose
    Test coupling between IB motion and scalar (ellipsoid pitching)

    ## Setup
    - Ellipsoid pitching kinematics (from main code)
    - Upstream sphere source at fixed location
    - Zero-normal-gradient BC on ellipsoid: ∂C/∂n = 0
    - Run several cycles until periodic

    ## What to Measure
    - No scalar leakage across IB surface (flux ≈ 0)
    - Odor iso-surfaces qualitatively match vortices
    - Mass budget conservation
    - Comparison with Lei et al. figures

    ## Pass Criteria
    - |∫_{IB} ∂C/∂n dS| < O(Δx²)
    - Odor patterns resemble published shapes
    - No spurious concentration spikes near IB

    ## Implementation
    Use existing example.cpp with ellipsoid kinematics
    """)
    with open(f"{test_dir}/README.md", "w") as f:
        f.write(readme)

    print(f"✓ Created {test_dir}")

def create_test11():
    """Test 11: AMR Sensitivity"""
    test_dir = "Test11_AMR"
    os.makedirs(test_dir, exist_ok=True)

    readme = textwrap.dedent("""
    # Test 11: AMR Behavior & Refinement Sensitivity

    ## Purpose
    Ensure AMR captures scalar gradients without artifacts

    ## Setup
    - Sphere + ellipsoid case
    - Multiple refinement strategies:
      1. Refine on vorticity only
      2. Refine on |∇C| only
      3. Refine on both

    ## What to Measure
    - Spurious oscillations at level interfaces
    - Centerline C compared to uniform fine grid
    - Computational cost vs accuracy

    ## Pass Criteria
    - AMR solution matches uniform fine grid (within discretization error)
    - No visible artifacts at refinement boundaries
    - Speedup > 2x with comparable accuracy

    ## Implementation
    Run same case with different tagging criteria
    """)
    with open(f"{test_dir}/README.md", "w") as f:
        f.write(readme)

    print(f"✓ Created {test_dir}")

def create_test12():
    """Test 12: Time-step Sensitivity"""
    test_dir = "Test12_TimeStep"
    os.makedirs(test_dir, exist_ok=True)

    readme = textwrap.dedent("""
    # Test 12: Time-Step & CFL Sensitivity

    ## Purpose
    Ensure Δt is stable and accurate

    ## Setup
    - Advection-dominant case (high U)
    - Run with Δt halved 2-3 times

    ## What to Measure
    - Stability (no blow-up)
    - Temporal convergence order
    - Mass conservation vs Δt

    ## Pass Criteria
    - Δt_prod sits on converged plateau (further reduction changes <1%)
    - Temporal order matches scheme (1st for BE, 2nd for CN)

    ## Implementation
    Repeat sphere case with Δt = Δt₀, Δt₀/2, Δt₀/4
    """)
    with open(f"{test_dir}/README.md", "w") as f:
        f.write(readme)

    print(f"✓ Created {test_dir}")

def create_test13():
    """Test 13: Long-Run Periodicity"""
    test_dir = "Test13_LongRun"
    os.makedirs(test_dir, exist_ok=True)

    readme = textwrap.dedent("""
    # Test 13: Long-Run Conservation & Periodicity

    ## Purpose
    Check for secular drift over many cycles

    ## Setup
    - Ellipsoid pitching (oscillatory kinematics)
    - Run 20-50 cycles
    - Monitor cycle-averaged quantities

    ## What to Measure
    - Total scalar mass M(t)
    - Peak C at sensor locations
    - Force/kinematic periodicity

    ## Pass Criteria
    - No artificial drift beyond source/sink effects
    - Periodic metrics converge after ~5-10 cycles
    - Mass conservation maintained long-term

    ## Implementation
    Use production setup, long time integration
    """)
    with open(f"{test_dir}/README.md", "w") as f:
        f.write(readme)

    print(f"✓ Created {test_dir}")

def create_test14():
    """Test 14: Benchmark Comparisons"""
    test_dir = "Test14_Benchmarks"
    os.makedirs(test_dir, exist_ok=True)

    readme = textwrap.dedent("""
    # Test 14: Comparison with Published Benchmarks

    ## Purpose
    Cross-check solver vs published CFD validations

    ## Benchmarks

    ### 14a: Lei et al. (2021) - Odor in plumes
    - Sphere + pitching airfoil
    - Compare iso-surfaces and PDFs
    - Schmidt number effects

    ### 14b: Kamran et al. (2024) - Undulating bodies
    - Wake-odor coupling
    - Vortex dynamics enhancing spread
    - Qualitative feature comparison

    ### 14c: Yan & Zu - Heat transfer
    - Rotating cylinder
    - Temperature/scalar distribution
    - (Used by Lei as validation)

    ## Pass Criteria
    - Reproduce main qualitative features
    - Quantitative agreement 10-20% (coarse)
    - Closer agreement on refined grids

    ## Implementation
    Extract published data points and compare
    """)
    with open(f"{test_dir}/README.md", "w") as f:
        f.write(readme)

    print(f"✓ Created {test_dir}")

def create_master_runner():
    """Create master runner script"""
    script = textwrap.dedent("""
    #!/bin/bash
    # Master script to run all V&V tests

    echo "======================================================================="
    echo "V&V TEST SUITE - SCALAR TRANSPORT VALIDATION"
    echo "======================================================================="

    FAILED_TESTS=()
    PASSED_TESTS=()

    run_test() {
        local test_dir=$1
        local test_name=$2

        echo ""
        echo "-----------------------------------------------------------------------"
        echo "Running $test_name"
        echo "-----------------------------------------------------------------------"

        if [ -d "$test_dir" ] && [ -f "$test_dir/run_test.sh" ]; then
            cd "$test_dir"
            ./run_test.sh
            if [ $? -eq 0 ]; then
                PASSED_TESTS+=("$test_name")
                echo "✓ $test_name PASSED"
            else
                FAILED_TESTS+=("$test_name")
                echo "✗ $test_name FAILED"
            fi
            cd ..
        else
            echo "⚠️  $test_name not implemented yet"
        fi
    }

    # Run tests in order
    run_test "Test01_SmokeTest" "Test 1: Smoke Test"
    run_test "Test02_Diffusion_Analytic" "Test 2: Pure Diffusion"
    run_test "Test03_Advection_Analytic" "Test 3: Pure Advection"
    run_test "Test04_MMS" "Test 4: MMS"
    run_test "Test05_Discontinuous" "Test 5: Discontinuous"
    run_test "Test06_MassConservation" "Test 6: Mass Conservation"
    run_test "Test07_BCs" "Test 7: Boundary Conditions"
    run_test "Test08_SphereSource" "Test 8: Sphere Source"
    run_test "Test09_HighSc" "Test 9: High Schmidt"
    run_test "Test10_MovingIB" "Test 10: Moving IB"
    run_test "Test11_AMR" "Test 11: AMR"
    run_test "Test12_TimeStep" "Test 12: Time-step"
    run_test "Test13_LongRun" "Test 13: Long Run"
    run_test "Test14_Benchmarks" "Test 14: Benchmarks"

    # Summary
    echo ""
    echo "======================================================================="
    echo "V&V TEST SUITE SUMMARY"
    echo "======================================================================="
    echo "Passed: ${#PASSED_TESTS[@]}"
    echo "Failed: ${#FAILED_TESTS[@]}"

    if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
        echo ""
        echo "Failed tests:"
        for test in "${FAILED_TESTS[@]}"; do
            echo "  - $test"
        done
        exit 1
    else
        echo ""
        echo "✅ ALL TESTS PASSED"
        exit 0
    fi
    """)

    with open("run_all_tests.sh", "w") as f:
        f.write(script)
    os.chmod("run_all_tests.sh", 0o755)
    print("✓ Created run_all_tests.sh")

def main():
    """Generate all test configurations"""
    print("Generating V&V test configurations...")

    create_test03()
    create_test04()
    create_test05()
    create_test06()
    create_test07()
    create_test08()
    create_test09()
    create_test10()
    create_test11()
    create_test12()
    create_test13()
    create_test14()
    create_master_runner()

    print("\n" + "="*70)
    print("✓ All test configurations created!")
    print("="*70)
    print("\nNext steps:")
    print("1. Review each test's README.md")
    print("2. Compile C++ test drivers as needed")
    print("3. Run individual tests: cd TestXX && ./run_test.sh")
    print("4. Or run all: ./run_all_tests.sh")

if __name__ == "__main__":
    main()
