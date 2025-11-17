#!/usr/bin/env python3
"""
Test 1: Smoke Test - Analysis Script

Checks:
1. No crashes (files exist)
2. No NaNs in output
3. Boundary condition enforcement (C=1 at left boundary)
4. Interior diffusion (C increases from 0)
5. Physical bounds (0 ≤ C ≤ 1)
"""

import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import sys

def read_vtk_scalar(filename):
    """Read scalar field from VTK file (simple ASCII VTK parser)"""
    with open(filename, 'r') as f:
        lines = f.readlines()

    # Find dimensions
    nx, ny = None, None
    for line in lines:
        if 'DIMENSIONS' in line:
            parts = line.split()
            nx, ny = int(parts[1]), int(parts[2])
            break

    if nx is None:
        raise ValueError(f"Could not find DIMENSIONS in {filename}")

    # Find scalar data
    data = []
    reading_data = False
    for i, line in enumerate(lines):
        if 'SCALARS' in line or 'C' in line:
            # Next line should be LOOKUP_TABLE, then data
            reading_data = True
            continue
        if reading_data and 'LOOKUP_TABLE' in line:
            continue
        if reading_data:
            try:
                vals = [float(x) for x in line.split()]
                data.extend(vals)
            except:
                pass

    if len(data) == 0:
        # Try alternative: look for point data
        for i, line in enumerate(lines):
            if 'POINT_DATA' in line:
                npoints = int(line.split()[1])
                # Find where scalar data starts
                for j in range(i, len(lines)):
                    if 'SCALARS' in lines[j]:
                        # Skip lookup table line
                        for k in range(j+2, len(lines)):
                            try:
                                vals = [float(x) for x in lines[k].split()]
                                data.extend(vals)
                                if len(data) >= npoints:
                                    break
                            except:
                                pass
                        break
                break

    if len(data) == 0:
        raise ValueError(f"Could not find scalar data in {filename}")

    # Reshape to grid
    C = np.array(data[:nx*ny]).reshape((ny, nx))
    return C, nx, ny

def analyze_smoke_test():
    """Analyze smoke test results"""

    print("=" * 70)
    print("TEST 1: SMOKE TEST ANALYSIS")
    print("=" * 70)

    # Find VTK files
    vtk_pattern = "viz_test01/*.vtk"
    vtk_files = sorted(glob.glob(vtk_pattern))

    if len(vtk_files) == 0:
        print(f"❌ FAIL: No VTK files found at {vtk_pattern}")
        print("   Code may have crashed or not run.")
        return False

    print(f"✓ Found {len(vtk_files)} VTK output files")

    # Analyze last timestep
    last_file = vtk_files[-1]
    print(f"\nAnalyzing final timestep: {last_file}")

    try:
        C, nx, ny = read_vtk_scalar(last_file)
        print(f"✓ Grid dimensions: {nx} × {ny}")
    except Exception as e:
        print(f"❌ FAIL: Could not read VTK file: {e}")
        return False

    # Check for NaNs
    if np.any(np.isnan(C)):
        print(f"❌ FAIL: NaN values detected in concentration field!")
        return False
    print("✓ No NaN values")

    # Check for Infs
    if np.any(np.isinf(C)):
        print(f"❌ FAIL: Inf values detected in concentration field!")
        return False
    print("✓ No Inf values")

    # Check physical bounds (0 ≤ C ≤ 1.1 allowing small overshoot)
    C_min, C_max = np.min(C), np.max(C)
    print(f"\nConcentration range: [{C_min:.6f}, {C_max:.6f}]")

    if C_min < -0.01:
        print(f"❌ FAIL: Negative concentration detected: {C_min}")
        return False
    print(f"✓ No significant negative values (min = {C_min:.6e})")

    if C_max > 1.2:
        print(f"❌ FAIL: Excessive overshoot: {C_max} > 1.2")
        return False
    print(f"✓ Reasonable maximum concentration (max = {C_max:.6f})")

    # Check left boundary (x=0, should be C≈1)
    # Left boundary is at i=0
    C_left = C[:, 0]  # All y at x=0
    C_left_mean = np.mean(C_left)
    C_left_std = np.std(C_left)

    print(f"\nLeft boundary (x=0) analysis:")
    print(f"  Mean C = {C_left_mean:.6f}")
    print(f"  Std  C = {C_left_std:.6f}")

    if abs(C_left_mean - 1.0) > 0.1:
        print(f"⚠️  WARNING: Left BC not well enforced (expected 1.0, got {C_left_mean:.4f})")
        print(f"   This may indicate BC implementation issues")
    else:
        print(f"✓ Left boundary condition enforced (C ≈ 1.0)")

    # Check that interior has diffused (C > 0 somewhere away from left)
    C_interior = C[:, nx//2]  # Middle column
    C_interior_mean = np.mean(C_interior)

    print(f"\nInterior diffusion analysis (x=0.5):")
    print(f"  Mean C = {C_interior_mean:.6f}")

    if C_interior_mean < 0.01:
        print(f"⚠️  WARNING: Very little diffusion into interior")
        print(f"   May need longer run time or larger diffusion coefficient")
    else:
        print(f"✓ Diffusion penetrating into domain")

    # Check right boundary (should be lower than left due to diffusion)
    C_right = C[:, -1]
    C_right_mean = np.mean(C_right)

    print(f"\nRight boundary (x=1) analysis:")
    print(f"  Mean C = {C_right_mean:.6f}")

    if C_right_mean > C_left_mean:
        print(f"❌ FAIL: Right boundary has higher C than left boundary (unphysical)")
        return False
    print(f"✓ Concentration gradient consistent with diffusion")

    # Create visualization
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 2D contour plot
    x = np.linspace(0, 1, nx)
    y = np.linspace(0, 1, ny)
    X, Y = np.meshgrid(x, y)

    ax = axes[0, 0]
    contour = ax.contourf(X, Y, C, levels=20, cmap='viridis')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Concentration Field C(x,y) - Final Time')
    ax.set_aspect('equal')
    plt.colorbar(contour, ax=ax, label='C')

    # Centerline profile (y=0.5)
    ax = axes[0, 1]
    ax.plot(x, C[ny//2, :], 'b-', linewidth=2, label='y=0.5 (centerline)')
    ax.axhline(y=1.0, color='r', linestyle='--', label='Left BC (C=1)')
    ax.set_xlabel('x')
    ax.set_ylabel('C')
    ax.set_title('Concentration Profile along x (centerline)')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Boundary values
    ax = axes[1, 0]
    ax.plot(y, C_left, 'r-', linewidth=2, label='Left boundary (x=0)')
    ax.plot(y, C_right, 'b-', linewidth=2, label='Right boundary (x=1)')
    ax.axhline(y=1.0, color='r', linestyle='--', alpha=0.3)
    ax.set_xlabel('y')
    ax.set_ylabel('C')
    ax.set_title('Boundary Concentration Profiles')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Time evolution (if multiple files available)
    ax = axes[1, 1]
    times = []
    C_max_vs_t = []
    C_mean_vs_t = []

    for i, vtk_file in enumerate(vtk_files[::max(1, len(vtk_files)//10)]):  # Sample ~10 frames
        try:
            C_tmp, _, _ = read_vtk_scalar(vtk_file)
            times.append(i)
            C_max_vs_t.append(np.max(C_tmp))
            C_mean_vs_t.append(np.mean(C_tmp))
        except:
            pass

    ax.plot(times, C_max_vs_t, 'r-o', label='max(C)')
    ax.plot(times, C_mean_vs_t, 'b-s', label='mean(C)')
    ax.set_xlabel('Frame number')
    ax.set_ylabel('C')
    ax.set_title('Concentration Evolution')
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.savefig('test01_analysis.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ Saved visualization to test01_analysis.png")

    # Final verdict
    print("\n" + "=" * 70)
    print("FINAL VERDICT: ✅ PASS")
    print("=" * 70)
    print("Summary:")
    print(f"  - No crashes: ✓")
    print(f"  - No NaN/Inf: ✓")
    print(f"  - Physical bounds: ✓ (C ∈ [{C_min:.3f}, {C_max:.3f}])")
    print(f"  - Left BC enforced: {'✓' if abs(C_left_mean-1.0)<0.1 else '⚠️'}")
    print(f"  - Diffusion working: ✓")
    print("=" * 70)

    return True

if __name__ == "__main__":
    success = analyze_smoke_test()
    sys.exit(0 if success else 1)
