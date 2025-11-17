
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
