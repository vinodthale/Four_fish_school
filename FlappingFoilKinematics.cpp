// ---------------------------------------------------------------------
//
// Copyright (c) 2024 by the IBAMR developers
// All rights reserved.
//
// This file is part of IBAMR.
//
// IBAMR is free software and is distributed under the 3-clause BSD
// license. The full text of the license can be found in the file
// COPYRIGHT at the top level directory of IBAMR.
//
// ---------------------------------------------------------------------

/////////////////////////////// INCLUDES /////////////////////////////////////

#include "FlappingFoilKinematics.h"

#include <ibamr/namespaces.h>
#include <ibtk/LDataManager.h>

#include <cmath>
#include <iostream>

/////////////////////////////// STATIC ///////////////////////////////////////

namespace
{
// Convert degrees to radians
inline double deg_to_rad(double deg)
{
    return deg * M_PI / 180.0;
}
} // namespace

/////////////////////////////// PUBLIC ///////////////////////////////////////

FlappingFoilKinematics::FlappingFoilKinematics(
    const std::string& object_name,
    Pointer<Database> input_db,
    LDataManager* l_data_manager,
    Pointer<CartesianGridGeometry<NDIM>> grid_geometry,
    bool register_for_restart)
    : ConstraintIBKinematics(object_name, input_db, l_data_manager, register_for_restart),
      d_frequency(0.0),
      d_omega(0.0),
      d_heave_amplitude(0.0),
      d_pitch_amplitude(0.0),
      d_phase_offset(0.0),
      d_pivot_point_x(0.25), // Default: quarter-chord
      d_pivot_point_y(0.0),
      d_initial_offset_x(0.0),
      d_initial_offset_y(0.0),
      d_current_time(0.0),
      d_new_kinematics_vel(NDIM + (NDIM == 2 ? 1 : 3), 0.0), // [V_x, V_y, ω_z] in 2D
      d_l_data_manager(l_data_manager),
      d_grid_geometry(grid_geometry)
{
    // Read parameters from input database
    getFromInput(input_db);

    // Compute angular frequency
    d_omega = 2.0 * M_PI * d_frequency;

    // Initialize kinematics velocity and shape storage
    const int coarsest_ln = 0;
    const int finest_ln = d_l_data_manager->getFinestPatchLevelNumber();

    d_kinematics_vel.resize(finest_ln + 1);
    d_shape.resize(finest_ln + 1);

    // Print configuration
    pout << "\n";
    pout << "FlappingFoilKinematics configuration:\n";
    pout << "  Frequency (f):        " << d_frequency << " Hz\n";
    pout << "  Angular freq (ω):     " << d_omega << " rad/s\n";
    pout << "  Heave amplitude:      " << d_heave_amplitude << " (chords)\n";
    pout << "  Pitch amplitude:      " << d_pitch_amplitude * 180.0 / M_PI << " degrees\n";
    pout << "  Phase offset:         " << d_phase_offset * 180.0 / M_PI << " degrees\n";
    pout << "  Pivot point:          (" << d_pivot_point_x << ", " << d_pivot_point_y << ")\n";
    pout << "  Initial offset:       (" << d_initial_offset_x << ", " << d_initial_offset_y << ")\n";

    // Compute Strouhal number (approximate, assumes U_inf = 1)
    double St_approx = d_frequency * (2.0 * d_heave_amplitude); // St = f*A/U
    pout << "  Approx. Strouhal (U=1): " << St_approx << "\n";
    pout << "\n";

    return;
}

FlappingFoilKinematics::~FlappingFoilKinematics()
{
    // Empty destructor
    return;
}

void
FlappingFoilKinematics::setKinematicsVelocity(
    const double time,
    const std::vector<double>& /*incremented_angle_from_reference_axis*/,
    const std::vector<double>& center_of_mass,
    const std::vector<double>& /*tagged_pt_position*/)
{
    d_current_time = time;
    d_center_of_mass = center_of_mass;

    // Compute heave kinematics
    double h, h_dot;
    computeHeaveKinematics(time, h, h_dot);

    // Compute pitch kinematics
    double theta, theta_dot;
    computePitchKinematics(time, theta, theta_dot);

    // Set translational velocity (COM motion)
    // V = (V_x, V_y) where V_x = 0 (no horizontal motion), V_y = ḣ
    d_new_kinematics_vel[0] = 0.0;      // No horizontal translation
    d_new_kinematics_vel[1] = h_dot;    // Heaving velocity

    // Set rotational velocity (about z-axis in 2D)
    if (NDIM == 2)
    {
        d_new_kinematics_vel[2] = theta_dot;  // Pitching angular velocity
    }
    else // NDIM == 3
    {
        d_new_kinematics_vel[2] = 0.0;        // ω_x
        d_new_kinematics_vel[3] = 0.0;        // ω_y
        d_new_kinematics_vel[4] = theta_dot;  // ω_z
    }

    // Store in all levels (same velocity for all levels in prescribed kinematics)
    const int finest_ln = d_l_data_manager->getFinestPatchLevelNumber();
    for (int ln = 0; ln <= finest_ln; ++ln)
    {
        d_kinematics_vel[ln] = d_new_kinematics_vel;
    }

    return;
}

void
FlappingFoilKinematics::setShape(
    const double time,
    const std::vector<double>& /*incremented_angle_from_reference_axis*/)
{
    // For rigid body (no deformation), shape is empty
    const int finest_ln = d_l_data_manager->getFinestPatchLevelNumber();
    for (int ln = 0; ln <= finest_ln; ++ln)
    {
        d_shape[ln].clear();
    }

    return;
}

/////////////////////////////// PRIVATE //////////////////////////////////////

void
FlappingFoilKinematics::computeHeaveKinematics(
    double time,
    double& h,
    double& h_dot) const
{
    // Heave position: h(t) = h_0 sin(ωt)
    h = d_heave_amplitude * std::sin(d_omega * time);

    // Heave velocity: ḣ(t) = h_0 ω cos(ωt)
    h_dot = d_heave_amplitude * d_omega * std::cos(d_omega * time);

    return;
}

void
FlappingFoilKinematics::computePitchKinematics(
    double time,
    double& theta,
    double& theta_dot) const
{
    // Pitch angle: θ(t) = θ_0 sin(ωt + φ)
    theta = d_pitch_amplitude * std::sin(d_omega * time + d_phase_offset);

    // Pitch rate: θ̇(t) = θ_0 ω cos(ωt + φ)
    theta_dot = d_pitch_amplitude * d_omega * std::cos(d_omega * time + d_phase_offset);

    return;
}

void
FlappingFoilKinematics::getFromInput(Pointer<Database> input_db)
{
    // Frequency (required)
    if (input_db->keyExists("frequency"))
    {
        d_frequency = input_db->getDouble("frequency");
    }
    else
    {
        TBOX_ERROR("FlappingFoilKinematics::getFromInput(): "
                   << "Key 'frequency' not found in input database." << std::endl);
    }

    // Heave amplitude (required)
    if (input_db->keyExists("heave_amplitude"))
    {
        d_heave_amplitude = input_db->getDouble("heave_amplitude");
    }
    else
    {
        TBOX_ERROR("FlappingFoilKinematics::getFromInput(): "
                   << "Key 'heave_amplitude' not found in input database." << std::endl);
    }

    // Pitch amplitude in degrees (required)
    if (input_db->keyExists("pitch_amplitude"))
    {
        double pitch_deg = input_db->getDouble("pitch_amplitude");
        d_pitch_amplitude = deg_to_rad(pitch_deg);
    }
    else
    {
        TBOX_ERROR("FlappingFoilKinematics::getFromInput(): "
                   << "Key 'pitch_amplitude' not found in input database." << std::endl);
    }

    // Phase offset in degrees (optional, default 90°)
    if (input_db->keyExists("phase_offset"))
    {
        double phase_deg = input_db->getDouble("phase_offset");
        d_phase_offset = deg_to_rad(phase_deg);
    }
    else
    {
        d_phase_offset = deg_to_rad(90.0); // Default: 90° (pitch leads heave)
        pout << "FlappingFoilKinematics: Using default phase_offset = 90 degrees\n";
    }

    // Pivot point (optional)
    if (input_db->keyExists("pivot_point_x"))
    {
        d_pivot_point_x = input_db->getDouble("pivot_point_x");
    }
    if (input_db->keyExists("pivot_point_y"))
    {
        d_pivot_point_y = input_db->getDouble("pivot_point_y");
    }

    // Initial offset (optional)
    if (input_db->keyExists("initial_offset_x"))
    {
        d_initial_offset_x = input_db->getDouble("initial_offset_x");
    }
    if (input_db->keyExists("initial_offset_y"))
    {
        d_initial_offset_y = input_db->getDouble("initial_offset_y");
    }

    return;
}
