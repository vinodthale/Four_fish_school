
# Test 7: Boundary Condition Tests

## Purpose
Verify Dirichlet, Neumann, and Robin BCs for scalar

## Test Cases

### 7a: Dirichlet Inlet
- Constant C=1 at inlet
- Outflow at outlet
- Verify profile develops downstream

### 7b: Neumann on IB Surface
- Small sphere with ∂C/∂n = 0
- Compute normal flux across surface
- Should be ≈ 0

### 7c: Robin (Flux) BC
- Prescribed flux on patch
- Verify global mass increase = ∫ flux dt

## Pass Criteria
- Dirichlet: |C_surface - C_prescribed| < 1e-6
- Neumann: |∫ ∂C/∂n dS| < O(Δx)
- Robin: Mass balance within numerical error

## Implementation
Run 3 sub-tests with different BC configurations
