
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
