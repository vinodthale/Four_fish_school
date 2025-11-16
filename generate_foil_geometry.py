#!/usr/bin/env python3
"""
Generate foil geometry for IBAMR simulations.

Creates NACA 4-digit airfoil or simple elliptical foil geometry
and saves in IBAMR .vertex format.

Author: Generated for Four Fish School project
Date: 2025-11-16
"""

import numpy as np
import matplotlib.pyplot as plt
import argparse
from pathlib import Path


def naca_4digit(code: str, num_points: int = 128, chord: float = 1.0) -> tuple:
    """
    Generate NACA 4-digit airfoil coordinates.

    Parameters
    ----------
    code : str
        4-digit NACA code (e.g., "0012" for NACA0012)
    num_points : int
        Number of points along surface
    chord : float
        Chord length

    Returns
    -------
    x : ndarray
        X-coordinates (scaled by chord)
    y : ndarray
        Y-coordinates (scaled by chord)
    """
    # Parse NACA code
    m = int(code[0]) / 100.0  # Maximum camber
    p = int(code[1]) / 10.0   # Location of max camber
    t = int(code[2:4]) / 100.0  # Maximum thickness

    # Cosine spacing for better resolution at leading/trailing edges
    beta = np.linspace(0, np.pi, num_points // 2)
    x_upper = (1.0 - np.cos(beta)) / 2.0

    # Thickness distribution (NACA formula)
    yt = 5 * t * (
        0.2969 * np.sqrt(x_upper) -
        0.1260 * x_upper -
        0.3516 * x_upper**2 +
        0.2843 * x_upper**3 -
        0.1015 * x_upper**4
    )

    # Camber line
    if m == 0:  # Symmetric airfoil
        yc = np.zeros_like(x_upper)
        dyc_dx = np.zeros_like(x_upper)
    else:
        yc = np.where(
            x_upper <= p,
            m / p**2 * (2 * p * x_upper - x_upper**2),
            m / (1 - p)**2 * ((1 - 2 * p) + 2 * p * x_upper - x_upper**2)
        )

        dyc_dx = np.where(
            x_upper <= p,
            2 * m / p**2 * (p - x_upper),
            2 * m / (1 - p)**2 * (p - x_upper)
        )

    # Angle of camber line
    theta = np.arctan(dyc_dx)

    # Upper and lower surface coordinates
    x_u = x_upper - yt * np.sin(theta)
    y_u = yc + yt * np.cos(theta)

    x_l = x_upper + yt * np.sin(theta)
    y_l = yc - yt * np.cos(theta)

    # Combine upper and lower surfaces (trailing edge → leading edge → trailing edge)
    x = np.concatenate([x_u[::-1], x_l[1:]])
    y = np.concatenate([y_u[::-1], y_l[1:]])

    # Scale by chord
    x = x * chord
    y = y * chord

    # Shift so leading edge is at x=0
    x = x - x.min()

    return x, y


def elliptical_foil(thickness: float = 0.1, num_points: int = 128, chord: float = 1.0) -> tuple:
    """
    Generate elliptical foil geometry.

    Parameters
    ----------
    thickness : float
        Maximum thickness as fraction of chord
    num_points : int
        Number of points
    chord : float
        Chord length

    Returns
    -------
    x : ndarray
        X-coordinates
    y : ndarray
        Y-coordinates
    """
    # Parametric ellipse
    theta = np.linspace(0, 2 * np.pi, num_points, endpoint=False)

    # Semi-major and semi-minor axes
    a = chord / 2.0
    b = thickness * chord / 2.0

    x = a * np.cos(theta)
    y = b * np.sin(theta)

    # Shift so leading edge is at x=0
    x = x + a

    return x, y


def save_vertex_file(x: np.ndarray, y: np.ndarray, filename: str):
    """
    Save coordinates in IBAMR .vertex format.

    Format:
    Line 1: Number of vertices
    Line 2-N: x y (one point per line)

    Parameters
    ----------
    x, y : ndarray
        Coordinates
    filename : str
        Output filename
    """
    with open(filename, 'w') as f:
        f.write(f"{len(x)}\n")
        for xi, yi in zip(x, y):
            f.write(f"{xi:.10f} {yi:.10f}\n")

    print(f"Saved {len(x)} vertices to {filename}")


def plot_foil(x: np.ndarray, y: np.ndarray, filename: str = None):
    """
    Plot foil geometry.

    Parameters
    ----------
    x, y : ndarray
        Coordinates
    filename : str, optional
        If provided, save plot to file
    """
    plt.figure(figsize=(10, 4))
    plt.plot(x, y, 'b-', linewidth=2)
    plt.plot(x, y, 'ro', markersize=3, alpha=0.5)  # Show vertices
    plt.xlabel('x/L')
    plt.ylabel('y/L')
    plt.title(f'Foil Geometry ({len(x)} vertices)')
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.tight_layout()

    if filename:
        plt.savefig(filename, dpi=150)
        print(f"Saved plot to {filename}")
    else:
        plt.show()

    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Generate foil geometry for IBAMR")

    parser.add_argument("--type", type=str, default="naca",
                        choices=["naca", "ellipse"],
                        help="Foil type: naca or ellipse")

    parser.add_argument("--naca_code", type=str, default="0012",
                        help="NACA 4-digit code (e.g., 0012 for symmetric)")

    parser.add_argument("--thickness", type=float, default=0.1,
                        help="Thickness for elliptical foil (fraction of chord)")

    parser.add_argument("--chord", type=float, default=1.0,
                        help="Chord length")

    parser.add_argument("--num_points", type=int, default=128,
                        help="Number of points along surface")

    parser.add_argument("--output", type=str, default="foil.vertex",
                        help="Output filename")

    parser.add_argument("--plot", action="store_true",
                        help="Show plot of geometry")

    parser.add_argument("--save_plot", type=str, default=None,
                        help="Save plot to file")

    args = parser.parse_args()

    # Generate geometry
    print(f"Generating {args.type} foil geometry...")

    if args.type == "naca":
        print(f"  NACA code: {args.naca_code}")
        x, y = naca_4digit(args.naca_code, args.num_points, args.chord)
    else:  # ellipse
        print(f"  Thickness: {args.thickness * 100:.1f}%")
        x, y = elliptical_foil(args.thickness, args.num_points, args.chord)

    print(f"  Chord: {args.chord}")
    print(f"  Number of points: {len(x)}")

    # Statistics
    print(f"\nGeometry statistics:")
    print(f"  X range: [{x.min():.4f}, {x.max():.4f}]")
    print(f"  Y range: [{y.min():.4f}, {y.max():.4f}]")
    print(f"  Max thickness: {(y.max() - y.min()):.4f} ({(y.max() - y.min())/args.chord*100:.1f}% chord)")

    # Save to file
    save_vertex_file(x, y, args.output)

    # Plot
    if args.plot or args.save_plot:
        plot_foil(x, y, args.save_plot)


if __name__ == "__main__":
    main()
