
#!/bin/bash
# Master script to run all V&V tests

echo "======================================================================="
echo "V&V TEST SUITE - SCALAR TRANSPORT VALIDATION"
echo "======================================================================="

FAILED_TESTS=()
PASSED_TESTS=()

run_test() {
    local test_dir=$1
    local test_name=$2

    echo ""
    echo "-----------------------------------------------------------------------"
    echo "Running $test_name"
    echo "-----------------------------------------------------------------------"

    if [ -d "$test_dir" ] && [ -f "$test_dir/run_test.sh" ]; then
        cd "$test_dir"
        ./run_test.sh
        if [ $? -eq 0 ]; then
            PASSED_TESTS+=("$test_name")
            echo "✓ $test_name PASSED"
        else
            FAILED_TESTS+=("$test_name")
            echo "✗ $test_name FAILED"
        fi
        cd ..
    else
        echo "⚠️  $test_name not implemented yet"
    fi
}

# Run tests in order
run_test "Test01_SmokeTest" "Test 1: Smoke Test"
run_test "Test02_Diffusion_Analytic" "Test 2: Pure Diffusion"
run_test "Test03_Advection_Analytic" "Test 3: Pure Advection"
run_test "Test04_MMS" "Test 4: MMS"
run_test "Test05_Discontinuous" "Test 5: Discontinuous"
run_test "Test06_MassConservation" "Test 6: Mass Conservation"
run_test "Test07_BCs" "Test 7: Boundary Conditions"
run_test "Test08_SphereSource" "Test 8: Sphere Source"
run_test "Test09_HighSc" "Test 9: High Schmidt"
run_test "Test10_MovingIB" "Test 10: Moving IB"
run_test "Test11_AMR" "Test 11: AMR"
run_test "Test12_TimeStep" "Test 12: Time-step"
run_test "Test13_LongRun" "Test 13: Long Run"
run_test "Test14_Benchmarks" "Test 14: Benchmarks"

# Summary
echo ""
echo "======================================================================="
echo "V&V TEST SUITE SUMMARY"
echo "======================================================================="
echo "Passed: ${#PASSED_TESTS[@]}"
echo "Failed: ${#FAILED_TESTS[@]}"

if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
    echo ""
    echo "Failed tests:"
    for test in "${FAILED_TESTS[@]}"; do
        echo "  - $test"
    done
    exit 1
else
    echo ""
    echo "✅ ALL TESTS PASSED"
    exit 0
fi
