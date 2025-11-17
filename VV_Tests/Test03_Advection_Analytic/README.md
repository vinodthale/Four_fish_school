
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
