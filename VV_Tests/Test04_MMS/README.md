
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
