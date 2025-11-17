
# Test 12: Time-Step & CFL Sensitivity

## Purpose
Ensure Δt is stable and accurate

## Setup
- Advection-dominant case (high U)
- Run with Δt halved 2-3 times

## What to Measure
- Stability (no blow-up)
- Temporal convergence order
- Mass conservation vs Δt

## Pass Criteria
- Δt_prod sits on converged plateau (further reduction changes <1%)
- Temporal order matches scheme (1st for BE, 2nd for CN)

## Implementation
Repeat sphere case with Δt = Δt₀, Δt₀/2, Δt₀/4
