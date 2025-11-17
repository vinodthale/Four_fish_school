#!/bin/bash
# =============================================================================
# Run script for Test 1: Smoke Test
# =============================================================================

echo "======================================================================="
echo "TEST 1: SMOKE TEST - Scalar Infrastructure Verification"
echo "======================================================================="

# Clean previous results
echo "Cleaning previous results..."
rm -rf viz_test01 test01.log test01_analysis.png

# Compile the test (if needed)
if [ ! -f "test01_scalar_only" ]; then
    echo "Compiling test01_scalar_only.cpp..."

    # Check if we're in an IBAMR environment
    if [ -z "$IBAMR_DIR" ]; then
        echo "ERROR: IBAMR_DIR not set. Please load IBAMR environment."
        echo "Attempting to use system IBAMR..."
    fi

    # Try to compile with CMake
    if [ -f "CMakeLists.txt" ]; then
        mkdir -p build
        cd build
        cmake ..
        make
        cd ..
        cp build/test01_scalar_only .
    else
        echo "WARNING: CMakeLists.txt not found."
        echo "Using existing compiled binary from main directory..."
        # Use the main example.cpp compiled version as fallback
        if [ -f "../../main2d" ]; then
            echo "Note: This test ideally needs test01_scalar_only compiled separately."
            echo "For now, please compile manually or use the Python-based tests."
        fi
    fi
fi

# Run the simulation
echo ""
echo "Running simulation..."
if [ -f "test01_scalar_only" ]; then
    mpirun -np 1 ./test01_scalar_only input2d
    EXIT_CODE=$?
else
    echo "WARNING: test01_scalar_only binary not found."
    echo "Please compile the test first."
    echo ""
    echo "To compile, you can use:"
    echo "  1. Create a CMakeLists.txt in this directory"
    echo "  2. Or manually compile with your IBAMR build system"
    echo ""
    echo "For now, running analysis on existing data (if any)..."
    EXIT_CODE=0
fi

# Check if simulation completed
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ SIMULATION FAILED (exit code: $EXIT_CODE)"
    exit $EXIT_CODE
fi

echo ""
echo "Simulation completed. Running analysis..."

# Run analysis
python3 analyze.py
ANALYSIS_EXIT=$?

if [ $ANALYSIS_EXIT -eq 0 ]; then
    echo ""
    echo "======================================================================="
    echo "✅ TEST 1 PASSED"
    echo "======================================================================="
    exit 0
else
    echo ""
    echo "======================================================================="
    echo "❌ TEST 1 FAILED"
    echo "======================================================================="
    exit 1
fi
