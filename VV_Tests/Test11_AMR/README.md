
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
