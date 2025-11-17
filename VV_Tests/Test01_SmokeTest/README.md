# Test 1: Code Smoke Test - Scalar Infrastructure

## Purpose
Ensure scalar variable registration, I/O, boundary condition hooks, and output work correctly.

## Setup
- **Domain**: 1×1 (2D square)
- **Grid**: Uniform coarse grid 32×32
- **Velocity**: u = 0 (no flow)
- **Initial Condition**: C = 0 everywhere
- **Boundary Conditions**:
  - Left (x=0): Dirichlet C = 1.0 (constant)
  - All other boundaries: Neumann ∂C/∂n = 0 (zero-gradient)
- **Diffusion**: κ = 1e-3 (small but nonzero)
- **Time**: Run for 10 time steps (short test)

## What to Measure
1. **No crashes**: Code runs to completion
2. **No NaNs**: All output values are finite
3. **BC enforcement**: C ≈ 1.0 at left boundary
4. **Interior evolution**: C transitions from 0 → 1 due to diffusion from left boundary
5. **File I/O**: VTK files written successfully

## Pass Criteria
✅ **Pass** if:
- Code runs without crash
- Output files created in viz directory
- Left boundary maintains C ≈ 1.0 (within 1e-3)
- Interior shows smooth increase from 0 toward 1
- No NaN or Inf values in output
- Max concentration ≤ 1.0 (no overshoot)

❌ **Fail** if:
- Crash or segmentation fault
- NaN/Inf values appear
- Boundary condition not enforced
- Unphysical oscillations

## Expected Output
At final time, expect:
- C(x=0, y) ≈ 1.0 (left boundary)
- C(x=1, y) > 0 (diffusion penetration)
- Smooth gradient from left to right
- Symmetry in y-direction

## Implementation Notes
This test uses:
- No immersed boundaries (pure Eulerian)
- Single AMR level (coarsest only)
- Short run time (quick verification)
