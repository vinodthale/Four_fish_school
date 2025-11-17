#!/usr/bin/env python3
"""
Master Analysis Script for V&V Test Suite

This script aggregates results from all tests and generates
a comprehensive summary report.
"""

import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

class VVTestResult:
    """Container for individual test results"""
    def __init__(self, test_num, name):
        self.test_num = test_num
        self.name = name
        self.status = "NOT_RUN"  # NOT_RUN, PASS, FAIL, WARNING
        self.errors = {}
        self.convergence_rates = {}
        self.notes = []

    def set_pass(self, notes=""):
        self.status = "PASS"
        if notes:
            self.notes.append(notes)

    def set_fail(self, reason):
        self.status = "FAIL"
        self.notes.append(f"FAILURE: {reason}")

    def set_warning(self, warning):
        self.status = "WARNING"
        self.notes.append(f"WARNING: {warning}")

    def add_error(self, error_type, value):
        self.errors[error_type] = value

    def add_convergence_rate(self, metric, rate):
        self.convergence_rates[metric] = rate

def collect_test_results():
    """Scan all test directories and collect results"""
    results = []

    test_list = [
        (1, "Smoke Test"),
        (2, "Pure Diffusion"),
        (3, "Pure Advection"),
        (4, "MMS"),
        (5, "Discontinuous"),
        (6, "Mass Conservation"),
        (7, "Boundary Conditions"),
        (8, "Sphere Source"),
        (9, "High Schmidt"),
        (10, "Moving IB"),
        (11, "AMR"),
        (12, "Time-step"),
        (13, "Long Run"),
        (14, "Benchmarks"),
    ]

    for test_num, test_name in test_list:
        result = VVTestResult(test_num, test_name)

        # Check if test directory exists
        test_dir = f"../Test{test_num:02d}_*"
        matching_dirs = glob.glob(test_dir)

        if not matching_dirs:
            result.status = "NOT_RUN"
            result.notes.append("Test directory not found")
        else:
            # Check for result files
            test_path = matching_dirs[0]
            result_file = os.path.join(test_path, "result.txt")

            if os.path.exists(result_file):
                # Parse result file
                with open(result_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if "PASS" in line:
                            result.set_pass()
                        elif "FAIL" in line:
                            result.set_fail(line.strip())
                        elif "L2_error" in line:
                            value = float(line.split("=")[1])
                            result.add_error("L2", value)
                        elif "convergence_rate" in line:
                            value = float(line.split("=")[1])
                            result.add_convergence_rate("spatial", value)
            else:
                result.status = "NOT_RUN"
                result.notes.append("Result file not found (test may not have been run)")

        results.append(result)

    return results

def generate_summary_table(results):
    """Generate markdown summary table"""
    lines = []
    lines.append("# V&V Test Suite - Summary Results\n")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    lines.append("| Test # | Test Name | Status | Notes |\n")
    lines.append("|--------|-----------|--------|-------|\n")

    pass_count = 0
    fail_count = 0
    warning_count = 0
    not_run_count = 0

    for result in results:
        status_symbol = {
            "PASS": "✅",
            "FAIL": "❌",
            "WARNING": "⚠️",
            "NOT_RUN": "⏸️"
        }.get(result.status, "❓")

        notes_str = "; ".join(result.notes[:2]) if result.notes else "-"
        if len(notes_str) > 50:
            notes_str = notes_str[:47] + "..."

        lines.append(f"| {result.test_num} | {result.name} | {status_symbol} {result.status} | {notes_str} |\n")

        if result.status == "PASS":
            pass_count += 1
        elif result.status == "FAIL":
            fail_count += 1
        elif result.status == "WARNING":
            warning_count += 1
        else:
            not_run_count += 1

    lines.append("\n## Summary Statistics\n\n")
    lines.append(f"- **Passed**: {pass_count}/{len(results)}\n")
    lines.append(f"- **Failed**: {fail_count}/{len(results)}\n")
    lines.append(f"- **Warnings**: {warning_count}/{len(results)}\n")
    lines.append(f"- **Not Run**: {not_run_count}/{len(results)}\n")

    overall_status = "✅ ALL TESTS PASSED" if fail_count == 0 and not_run_count == 0 else \
                     "❌ SOME TESTS FAILED" if fail_count > 0 else \
                     "⚠️ TESTS INCOMPLETE"

    lines.append(f"\n**Overall Status**: {overall_status}\n")

    return "".join(lines)

def generate_detailed_report(results):
    """Generate detailed markdown report"""
    lines = []
    lines.append("\n---\n\n# Detailed Test Results\n\n")

    for result in results:
        lines.append(f"## Test {result.test_num}: {result.name}\n\n")
        lines.append(f"**Status**: {result.status}\n\n")

        if result.errors:
            lines.append("### Errors\n\n")
            for error_type, value in result.errors.items():
                lines.append(f"- {error_type}: {value:.6e}\n")
            lines.append("\n")

        if result.convergence_rates:
            lines.append("### Convergence Rates\n\n")
            for metric, rate in result.convergence_rates.items():
                lines.append(f"- {metric}: {rate:.3f}\n")
            lines.append("\n")

        if result.notes:
            lines.append("### Notes\n\n")
            for note in result.notes:
                lines.append(f"- {note}\n")
            lines.append("\n")

        lines.append("---\n\n")

    return "".join(lines)

def plot_overview(results):
    """Generate overview visualization"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Status pie chart
    ax = axes[0]
    statuses = [r.status for r in results]
    status_counts = {
        "PASS": statuses.count("PASS"),
        "FAIL": statuses.count("FAIL"),
        "WARNING": statuses.count("WARNING"),
        "NOT_RUN": statuses.count("NOT_RUN")
    }

    colors = {"PASS": "green", "FAIL": "red", "WARNING": "orange", "NOT_RUN": "gray"}
    labels = [f"{k}\n({v})" for k, v in status_counts.items() if v > 0]
    sizes = [v for v in status_counts.values() if v > 0]
    plot_colors = [colors[k] for k in status_counts.keys() if status_counts[k] > 0]

    ax.pie(sizes, labels=labels, colors=plot_colors, autopct='%1.1f%%', startangle=90)
    ax.set_title('Test Results Summary', fontsize=14, fontweight='bold')

    # Status by test number
    ax = axes[1]
    test_nums = [r.test_num for r in results]
    status_numeric = [{"PASS": 1, "WARNING": 0.5, "FAIL": -1, "NOT_RUN": 0}[r.status] for r in results]

    colors_bar = [{"PASS": "green", "WARNING": "orange", "FAIL": "red", "NOT_RUN": "gray"}[r.status] for r in results]

    bars = ax.bar(test_nums, [1]*len(test_nums), color=colors_bar, alpha=0.7, edgecolor='black')
    ax.set_xlabel('Test Number', fontsize=12)
    ax.set_ylabel('Status', fontsize=12)
    ax.set_title('Test Status by Number', fontsize=14, fontweight='bold')
    ax.set_ylim([0, 1.2])
    ax.set_yticks([])
    ax.set_xticks(test_nums)
    ax.grid(axis='x', alpha=0.3)

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', label='Pass'),
        Patch(facecolor='orange', label='Warning'),
        Patch(facecolor='red', label='Fail'),
        Patch(facecolor='gray', label='Not Run')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    plt.savefig('../Results/vv_summary.png', dpi=150, bbox_inches='tight')
    print("✓ Saved summary plot to Results/vv_summary.png")

def main():
    """Main analysis routine"""
    print("=" * 70)
    print("V&V MASTER ANALYSIS")
    print("=" * 70)

    # Collect results
    print("\nCollecting test results...")
    results = collect_test_results()

    # Generate reports
    print("Generating summary report...")
    summary = generate_summary_table(results)
    detailed = generate_detailed_report(results)

    # Write to file
    os.makedirs("../Results", exist_ok=True)
    with open("../Results/VV_Summary_Report.md", "w") as f:
        f.write(summary)
        f.write(detailed)

    print("✓ Saved report to Results/VV_Summary_Report.md")

    # Generate plots
    print("Generating visualizations...")
    plot_overview(results)

    # Print summary to console
    print("\n" + "=" * 70)
    print(summary)
    print("=" * 70)

    # Determine exit code
    fail_count = sum(1 for r in results if r.status == "FAIL")
    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
