# Test 2: Pure Diffusion of Gaussian - Analytic Validation

## Purpose
Verify diffusion operator (implicit/Crank-Nicolson) against exact analytic solution.

## Analytic Solution
For diffusion of an initial Gaussian in infinite domain:

```
C(x,t) = C₀ / √(1 + 4αt/σ₀²) × exp(-x² / (2σ₀²(1 + 4αt/σ₀²)))
```

where:
- C₀ = initial amplitude
- σ₀ = initial width
- α = diffusion coefficient
- Spreading: σ(t) = σ₀√(1 + 4αt/σ₀²)

## Setup
- **Domain**: Large 2D domain [-5, 5] × [-5, 5] to approximate infinite domain
- **Grid**: Three levels for convergence: 64×64, 128×128, 256×256
- **Velocity**: u = 0 (no advection)
- **Initial Condition**: Gaussian centered at (0,0) with σ₀ = 0.5
  ```
  C(x,y,0) = exp(-(x² + y²)/(2σ₀²))
  ```
- **Diffusion**: α = 0.01
- **Boundary**: Dirichlet C=0 at far-field (domain large enough)
- **Time**: Integrate to t=1.0

## What to Measure
1. **L² error**: `||C_numerical - C_analytic||₂`
2. **L∞ error**: `max|C_numerical - C_analytic|`
3. **Grid convergence**: Repeat with Δx halved twice
4. **Peak concentration decay**: Check C_max vs time
5. **Spreading rate**: Measure σ(t) vs analytic

## Pass Criteria
✅ **Pass** if:
- **Convergence order ≈ 2** (within ±15%) for both L² and L∞
- L² error < 1e-3 on finest grid
- No spurious oscillations
- Mass conservation (if BCs appropriate)

❌ **Fail** if:
- Convergence order < 1.5 or > 2.5
- Large errors indicating implementation bugs
- Oscillations or instabilities

## Expected Results
For Crank-Nicolson or Backward Euler with centered differences:
- **Spatial accuracy**: 2nd order
- **Temporal accuracy**: 1st order (BE) or 2nd order (CN)
- **Combined**: L² error slope ≈ 2.0 ± 0.3

## Grid Refinement Study
Run three grids:
1. Coarse: N=64 (Δx ≈ 0.156)
2. Medium: N=128 (Δx ≈ 0.078)
3. Fine: N=256 (Δx ≈ 0.039)

Keep time step proportional: Δt = C_CFL × Δx²

## Analysis Output
- Convergence plot: log(error) vs log(Δx)
- Contour comparison: numerical vs analytic
- Centerline profile comparison
- Temporal evolution of peak and width
