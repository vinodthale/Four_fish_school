#!/usr/bin/env python3
"""
Phase-Resolved Odor Plume Analysis for Lei et al. (2021) Study

This script analyzes odor concentration fields from IBAMR simulations
of flapping foils, computing phase-resolved statistics following
Lei et al. AIAA 2021-2817.

Key analyses:
1. Phase-resolved averaging: <C>(x, y, φ)
2. Conditional statistics: <C | vortex sign>
3. Plume width evolution
4. Centerline concentration profiles
5. Intermittency and variance

Author: Generated for Four Fish School project
Date: 2025-11-16
"""

import numpy as np
import matplotlib.pyplot as plt
import pyvista as pv
from scipy.interpolate import griddata
from pathlib import Path
import argparse
from typing import Tuple, List, Dict
import json


class OdorPlumeAnalyzer:
    """Analyzer for odor plume data from IBAMR simulations."""

    def __init__(self, data_dir: str, frequency: float, dt_output: float):
        """
        Initialize analyzer.

        Parameters
        ----------
        data_dir : str
            Path to visualization data directory
        frequency : float
            Flapping frequency (Hz)
        dt_output : float
            Time interval between output frames (s)
        """
        self.data_dir = Path(data_dir)
        self.frequency = frequency
        self.omega = 2.0 * np.pi * frequency
        self.dt_output = dt_output

        # Storage for loaded data
        self.frames = []
        self.phases = []

    def load_frame(self, frame_idx: int) -> Dict[str, np.ndarray]:
        """
        Load velocity, vorticity, and concentration from VTK files.

        Parameters
        ----------
        frame_idx : int
            Frame number to load

        Returns
        -------
        data : dict
            Dictionary containing:
            - 'points': (N, 3) array of grid points
            - 'u_x': x-velocity
            - 'u_y': y-velocity
            - 'omega': vorticity
            - 'C': odor concentration
        """
        frame_dir = self.data_dir / f"visit_dump_{frame_idx:04d}"

        if not frame_dir.exists():
            raise FileNotFoundError(f"Frame directory not found: {frame_dir}")

        # Load velocity components
        u_x_mesh = pv.read(str(frame_dir / "U_x.vtk"))
        u_y_mesh = pv.read(str(frame_dir / "U_y.vtk"))

        # Load vorticity
        omega_mesh = pv.read(str(frame_dir / "Omega.vtk"))

        # Load concentration
        C_mesh = pv.read(str(frame_dir / "C.vtk"))

        # Extract data
        data = {
            'points': u_x_mesh.points,
            'u_x': u_x_mesh["U_x"],
            'u_y': u_y_mesh["U_y"],
            'omega': omega_mesh["Omega"],
            'C': C_mesh["C"]
        }

        return data

    def compute_phase(self, frame_idx: int) -> float:
        """
        Compute flapping phase for given frame.

        Parameters
        ----------
        frame_idx : int
            Frame number

        Returns
        -------
        phase : float
            Phase in [0, 2π]
        """
        time = frame_idx * self.dt_output
        phase = (self.omega * time) % (2.0 * np.pi)
        return phase

    def load_all_frames(self, num_frames: int):
        """
        Load all frames and compute phases.

        Parameters
        ----------
        num_frames : int
            Number of frames to load
        """
        print(f"Loading {num_frames} frames...")

        self.frames = []
        self.phases = []

        for i in range(num_frames):
            try:
                data = self.load_frame(i)
                phase = self.compute_phase(i)

                self.frames.append(data)
                self.phases.append(phase)

                if (i + 1) % 10 == 0:
                    print(f"  Loaded {i + 1}/{num_frames} frames")

            except FileNotFoundError:
                print(f"  Frame {i} not found, stopping at {i} frames")
                break

        self.phases = np.array(self.phases)
        print(f"Successfully loaded {len(self.frames)} frames")

    def phase_resolved_average(self, num_bins: int = 8) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute phase-resolved average concentration.

        Parameters
        ----------
        num_bins : int
            Number of phase bins

        Returns
        -------
        C_avg : ndarray
            (num_bins, N_points) array of averaged concentration
        phase_bins : ndarray
            Phase bin edges
        """
        if len(self.frames) == 0:
            raise ValueError("No frames loaded. Call load_all_frames() first.")

        print(f"Computing phase-resolved average with {num_bins} bins...")

        # Create phase bins
        phase_bins = np.linspace(0, 2 * np.pi, num_bins + 1)

        # Get number of grid points from first frame
        N_points = len(self.frames[0]['C'])

        # Initialize storage
        C_sum = np.zeros((num_bins, N_points))
        counts = np.zeros(num_bins)

        # Bin by phase
        for frame, phase in zip(self.frames, self.phases):
            bin_idx = np.digitize(phase, phase_bins) - 1

            # Handle edge case (phase = 2π → bin_idx = num_bins)
            if bin_idx >= num_bins:
                bin_idx = num_bins - 1

            if 0 <= bin_idx < num_bins:
                C_sum[bin_idx] += frame['C']
                counts[bin_idx] += 1

        # Compute average
        C_avg = np.zeros_like(C_sum)
        for i in range(num_bins):
            if counts[i] > 0:
                C_avg[i] = C_sum[i] / counts[i]
            else:
                print(f"  Warning: No frames in bin {i} (phase {phase_bins[i]:.2f})")

        print(f"  Average samples per bin: {counts.mean():.1f}")

        return C_avg, phase_bins

    def conditional_statistics(self) -> Dict[str, float]:
        """
        Compute concentration conditioned on vortex sign.

        Returns
        -------
        stats : dict
            Dictionary with:
            - 'C_positive_vortex': <C | ω > 0>
            - 'C_negative_vortex': <C | ω < 0>
            - 'C_irrotational': <C | |ω| ≈ 0>
        """
        print("Computing conditional statistics...")

        C_all = []
        omega_all = []

        for frame in self.frames:
            C_all.append(frame['C'])
            omega_all.append(frame['omega'])

        C_all = np.concatenate(C_all)
        omega_all = np.concatenate(omega_all)

        # Threshold for "irrotational"
        omega_threshold = 0.1 * np.std(omega_all)

        # Conditional averages
        mask_pos = omega_all > omega_threshold
        mask_neg = omega_all < -omega_threshold
        mask_irr = np.abs(omega_all) <= omega_threshold

        stats = {
            'C_positive_vortex': C_all[mask_pos].mean() if mask_pos.any() else 0.0,
            'C_negative_vortex': C_all[mask_neg].mean() if mask_neg.any() else 0.0,
            'C_irrotational': C_all[mask_irr].mean() if mask_irr.any() else 0.0,
            'fraction_positive': mask_pos.sum() / len(omega_all),
            'fraction_negative': mask_neg.sum() / len(omega_all),
            'fraction_irrotational': mask_irr.sum() / len(omega_all)
        }

        print(f"  <C | ω > 0> = {stats['C_positive_vortex']:.4f}")
        print(f"  <C | ω < 0> = {stats['C_negative_vortex']:.4f}")
        print(f"  <C | |ω| ≈ 0> = {stats['C_irrotational']:.4f}")

        return stats

    def compute_plume_width(self, x_location: float = 2.0) -> List[float]:
        """
        Compute plume width at specified downstream location.

        Parameters
        ----------
        x_location : float
            Downstream location to measure width

        Returns
        -------
        widths : list
            Plume width (std dev in y) for each frame
        """
        print(f"Computing plume width at x = {x_location}...")

        widths = []

        for frame in self.frames:
            points = frame['points']
            C = frame['C']

            # Extract points near x_location
            tolerance = 0.1
            mask = np.abs(points[:, 0] - x_location) < tolerance

            if mask.sum() < 10:
                widths.append(np.nan)
                continue

            y_values = points[mask, 1]
            C_values = C[mask]

            # Compute weighted standard deviation
            if C_values.sum() > 1e-10:
                y_mean = np.average(y_values, weights=C_values)
                y_var = np.average((y_values - y_mean) ** 2, weights=C_values)
                width = np.sqrt(y_var)
            else:
                width = np.nan

            widths.append(width)

        return widths

    def extract_centerline(self, frame_idx: int, y_center: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract concentration along centerline (y ≈ 0).

        Parameters
        ----------
        frame_idx : int
            Frame to extract from
        y_center : float
            Y-coordinate of centerline

        Returns
        -------
        x : ndarray
            X-coordinates along centerline
        C : ndarray
            Concentration values
        """
        frame = self.frames[frame_idx]
        points = frame['points']
        C = frame['C']

        # Extract points near centerline
        tolerance = 0.1
        mask = np.abs(points[:, 1] - y_center) < tolerance

        x = points[mask, 0]
        C_centerline = C[mask]

        # Sort by x
        sort_idx = np.argsort(x)

        return x[sort_idx], C_centerline[sort_idx]

    def plot_phase_resolved(self, C_avg: np.ndarray, phase_bins: np.ndarray, output_dir: str = "plots"):
        """
        Plot phase-resolved concentration fields.

        Parameters
        ----------
        C_avg : ndarray
            Phase-averaged concentration
        phase_bins : ndarray
            Phase bin edges
        output_dir : str
            Directory to save plots
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        num_bins = len(C_avg)

        # Get grid from first frame
        points = self.frames[0]['points']

        # Create 2x4 subplot grid for 8 phases
        fig, axes = plt.subplots(2, 4, figsize=(16, 8))
        axes = axes.flatten()

        for i in range(num_bins):
            ax = axes[i]

            # Create scatter plot
            sc = ax.tricontourf(points[:, 0], points[:, 1], C_avg[i], levels=20, cmap='viridis')

            phase_deg = phase_bins[i] * 180 / np.pi
            ax.set_title(f'φ = {phase_deg:.0f}°')
            ax.set_xlabel('x/L')
            ax.set_ylabel('y/L')
            ax.set_aspect('equal')
            plt.colorbar(sc, ax=ax, label='C')

        plt.tight_layout()
        plt.savefig(output_path / "phase_resolved_concentration.png", dpi=150)
        print(f"  Saved phase-resolved plot to {output_path / 'phase_resolved_concentration.png'}")
        plt.close()

    def plot_plume_width_evolution(self, widths: List[float], output_dir: str = "plots"):
        """
        Plot plume width evolution over time.

        Parameters
        ----------
        widths : list
            Plume widths over time
        output_dir : str
            Directory to save plot
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        times = np.arange(len(widths)) * self.dt_output

        plt.figure(figsize=(10, 5))
        plt.plot(times, widths, 'b-', linewidth=2)
        plt.xlabel('Time (s)')
        plt.ylabel('Plume Width σ_y')
        plt.title('Plume Width Evolution')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path / "plume_width_evolution.png", dpi=150)
        print(f"  Saved width evolution plot to {output_path / 'plume_width_evolution.png'}")
        plt.close()

    def save_statistics(self, stats: Dict, output_file: str = "odor_plume_stats.json"):
        """
        Save statistics to JSON file.

        Parameters
        ----------
        stats : dict
            Statistics dictionary
        output_file : str
            Output filename
        """
        with open(output_file, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"  Saved statistics to {output_file}")


def main():
    """Main analysis pipeline."""
    parser = argparse.ArgumentParser(description="Analyze odor plume from IBAMR simulation")
    parser.add_argument("--data_dir", type=str, default="viz_odor_plume",
                        help="Path to visualization data directory")
    parser.add_argument("--frequency", type=float, default=0.5,
                        help="Flapping frequency (Hz)")
    parser.add_argument("--dt_output", type=float, default=0.04,
                        help="Time interval between frames (s)")
    parser.add_argument("--num_frames", type=int, default=200,
                        help="Number of frames to analyze")
    parser.add_argument("--num_phase_bins", type=int, default=8,
                        help="Number of phase bins for averaging")
    parser.add_argument("--output_dir", type=str, default="plots",
                        help="Output directory for plots")

    args = parser.parse_args()

    # Create analyzer
    analyzer = OdorPlumeAnalyzer(args.data_dir, args.frequency, args.dt_output)

    # Load frames
    analyzer.load_all_frames(args.num_frames)

    if len(analyzer.frames) == 0:
        print("ERROR: No frames loaded. Check data_dir path.")
        return

    # Phase-resolved averaging
    C_avg, phase_bins = analyzer.phase_resolved_average(num_bins=args.num_phase_bins)

    # Conditional statistics
    cond_stats = analyzer.conditional_statistics()

    # Plume width evolution
    widths = analyzer.compute_plume_width(x_location=2.0)

    # Plot results
    print("\nGenerating plots...")
    analyzer.plot_phase_resolved(C_avg, phase_bins, args.output_dir)
    analyzer.plot_plume_width_evolution(widths, args.output_dir)

    # Extract and plot centerline (middle frame)
    mid_frame = len(analyzer.frames) // 2
    x_cl, C_cl = analyzer.extract_centerline(mid_frame)

    plt.figure(figsize=(10, 5))
    plt.plot(x_cl, C_cl, 'b-', linewidth=2)
    plt.xlabel('x/L')
    plt.ylabel('Concentration C')
    plt.title(f'Centerline Concentration (frame {mid_frame})')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(Path(args.output_dir) / "centerline_concentration.png", dpi=150)
    print(f"  Saved centerline plot to {Path(args.output_dir) / 'centerline_concentration.png'}")
    plt.close()

    # Compile and save all statistics
    all_stats = {
        "simulation_parameters": {
            "frequency": args.frequency,
            "dt_output": args.dt_output,
            "num_frames_analyzed": len(analyzer.frames)
        },
        "conditional_statistics": cond_stats,
        "plume_width": {
            "mean": np.nanmean(widths),
            "std": np.nanstd(widths),
            "max": np.nanmax(widths),
            "min": np.nanmin(widths)
        }
    }

    analyzer.save_statistics(all_stats, Path(args.output_dir) / "odor_plume_stats.json")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Results saved to: {args.output_dir}/")
    print("\nKey findings:")
    print(f"  Average plume width: {all_stats['plume_width']['mean']:.3f} ± {all_stats['plume_width']['std']:.3f}")
    print(f"  Concentration in positive vortices: {cond_stats['C_positive_vortex']:.4f}")
    print(f"  Concentration in negative vortices: {cond_stats['C_negative_vortex']:.4f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
