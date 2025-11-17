
# Test 10: Moving Immersed Body with Scalar BCs

## Purpose
Test coupling between IB motion and scalar (ellipsoid pitching)

## Setup
- Ellipsoid pitching kinematics (from main code)
- Upstream sphere source at fixed location
- Zero-normal-gradient BC on ellipsoid: ∂C/∂n = 0
- Run several cycles until periodic

## What to Measure
- No scalar leakage across IB surface (flux ≈ 0)
- Odor iso-surfaces qualitatively match vortices
- Mass budget conservation
- Comparison with Lei et al. figures

## Pass Criteria
- |∫_{IB} ∂C/∂n dS| < O(Δx²)
- Odor patterns resemble published shapes
- No spurious concentration spikes near IB

## Implementation
Use existing example.cpp with ellipsoid kinematics
