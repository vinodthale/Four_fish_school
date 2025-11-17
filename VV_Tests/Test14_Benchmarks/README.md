
# Test 14: Comparison with Published Benchmarks

## Purpose
Cross-check solver vs published CFD validations

## Benchmarks

### 14a: Lei et al. (2021) - Odor in plumes
- Sphere + pitching airfoil
- Compare iso-surfaces and PDFs
- Schmidt number effects

### 14b: Kamran et al. (2024) - Undulating bodies
- Wake-odor coupling
- Vortex dynamics enhancing spread
- Qualitative feature comparison

### 14c: Yan & Zu - Heat transfer
- Rotating cylinder
- Temperature/scalar distribution
- (Used by Lei as validation)

## Pass Criteria
- Reproduce main qualitative features
- Quantitative agreement 10-20% (coarse)
- Closer agreement on refined grids

## Implementation
Extract published data points and compare
