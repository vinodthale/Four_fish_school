
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
