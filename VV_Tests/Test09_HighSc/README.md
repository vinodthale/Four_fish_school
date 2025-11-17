
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
