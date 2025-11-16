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

#ifndef included_FlappingFoilKinematics
#define included_FlappingFoilKinematics

/////////////////////////////// INCLUDES /////////////////////////////////////

#include <ibamr/ConstraintIBKinematics.h>
#include <ibtk/ibtk_utilities.h>
#include <tbox/Pointer.h>
#include <CartesianGridGeometry.h>

#include <iostream>
#include <vector>

/////////////////////////////// CLASS DEFINITION /////////////////////////////

/*!
 * \brief FlappingFoilKinematics implements prescribed heaving and pitching motion
 * for a flapping foil, following Lei et al. (2021) AIAA 2021-2817.
 *
 * Kinematics:
 *   h(t) = h_0 sin(ωt)           [heaving motion]
 *   θ(t) = θ_0 sin(ωt + φ)       [pitching motion]
 *
 * where:
 *   h_0   = heave amplitude
 *   θ_0   = pitch amplitude
 *   ω     = 2πf (angular frequency)
 *   f     = flapping frequency
 *   φ     = phase offset between heave and pitch
 *
 * Strouhal number: St = f·A/U_∞
 *   where A is the peak-to-peak amplitude (≈ 2h_0)
 */
class FlappingFoilKinematics : public IBAMR::ConstraintIBKinematics
{
public:
    /*!
     * \brief Constructor.
     *
     * \param object_name Name of the object
     * \param input_db Input database with parameters:
     *   - frequency: flapping frequency (Hz)
     *   - heave_amplitude: heave amplitude (normalized by chord)
     *   - pitch_amplitude: pitch amplitude (degrees)
     *   - phase_offset: phase between heave and pitch (degrees, default 90)
     *   - pivot_point_x: x-coordinate of pitch pivot (default 0.25 chord - quarter-chord)
     *   - pivot_point_y: y-coordinate of pitch pivot (default 0.0)
     *   - initial_offset_x: initial x-offset (default 0.0)
     *   - initial_offset_y: initial y-offset (default 0.0)
     */
    FlappingFoilKinematics(
        const std::string& object_name,
        SAMRAI::tbox::Pointer<SAMRAI::tbox::Database> input_db,
        IBTK::LDataManager* l_data_manager,
        SAMRAI::tbox::Pointer<SAMRAI::geom::CartesianGridGeometry<NDIM>> grid_geometry,
        bool register_for_restart = true);

    /*!
     * \brief Destructor.
     */
    virtual ~FlappingFoilKinematics();

    /*!
     * \brief Set kinematics velocity of the body (prescribed motion).
     *
     * This function computes translational and rotational velocities:
     *   V_trans = (0, ḣ, 0)  - heaving velocity
     *   ω_rot = (0, 0, θ̇)    - pitching angular velocity
     */
    virtual void setKinematicsVelocity(
        const double time,
        const std::vector<double>& incremented_angle_from_reference_axis,
        const std::vector<double>& center_of_mass,
        const std::vector<double>& tagged_pt_position);

    /*!
     * \brief Get the kinematics velocity on the specified level.
     */
    virtual const std::vector<std::vector<double>>& getKinematicsVelocity(const int level) const;

    /*!
     * \brief Set shape of the body (deformation).
     * For rigid body flapping, no shape deformation is needed.
     */
    virtual void setShape(
        const double time,
        const std::vector<double>& incremented_angle_from_reference_axis);

    /*!
     * \brief Get the shape of the body.
     */
    virtual const std::vector<std::vector<double>>& getShape(const int level) const;

private:
    /*!
     * \brief Copy constructor (not implemented).
     */
    FlappingFoilKinematics(const FlappingFoilKinematics& from) = delete;

    /*!
     * \brief Assignment operator (not implemented).
     */
    FlappingFoilKinematics& operator=(const FlappingFoilKinematics& that) = delete;

    /*!
     * \brief Compute current heave position and velocity.
     */
    void computeHeaveKinematics(double time, double& h, double& h_dot) const;

    /*!
     * \brief Compute current pitch angle and angular velocity.
     */
    void computePitchKinematics(double time, double& theta, double& theta_dot) const;

    /*!
     * \brief Read parameters from input database.
     */
    void getFromInput(SAMRAI::tbox::Pointer<SAMRAI::tbox::Database> input_db);

    // Member data

    /*!
     * \brief Flapping frequency (Hz).
     */
    double d_frequency;

    /*!
     * \brief Angular frequency ω = 2πf (rad/s).
     */
    double d_omega;

    /*!
     * \brief Heave amplitude h_0 (normalized by chord length).
     */
    double d_heave_amplitude;

    /*!
     * \brief Pitch amplitude θ_0 (radians).
     */
    double d_pitch_amplitude;

    /*!
     * \brief Phase offset between heave and pitch (radians).
     * Convention: φ > 0 means pitch leads heave.
     * Typical: φ = 90° (π/2 rad) for thrust production.
     */
    double d_phase_offset;

    /*!
     * \brief Pivot point for pitching rotation (relative to initial COM).
     */
    double d_pivot_point_x, d_pivot_point_y;

    /*!
     * \brief Initial offset of the foil COM.
     */
    double d_initial_offset_x, d_initial_offset_y;

    /*!
     * \brief Current time.
     */
    double d_current_time;

    /*!
     * \brief New kinematics velocity (computed in setKinematicsVelocity).
     * Format: [V_x, V_y, ω_z]
     */
    std::vector<double> d_new_kinematics_vel;

    /*!
     * \brief Kinematics velocity for each level.
     */
    std::vector<std::vector<double>> d_kinematics_vel;

    /*!
     * \brief Shape (deformation) for each level.
     * For rigid foil, this is empty.
     */
    std::vector<std::vector<double>> d_shape;

    /*!
     * \brief Current COM position.
     */
    std::vector<double> d_center_of_mass;

    /*!
     * \brief Data manager.
     */
    IBTK::LDataManager* d_l_data_manager;

    /*!
     * \brief Grid geometry.
     */
    SAMRAI::tbox::Pointer<SAMRAI::geom::CartesianGridGeometry<NDIM>> d_grid_geometry;
};

/////////////////////////////// INLINE ///////////////////////////////////////

inline const std::vector<std::vector<double>>&
FlappingFoilKinematics::getKinematicsVelocity(const int /*level*/) const
{
    return d_kinematics_vel;
}

inline const std::vector<std::vector<double>>&
FlappingFoilKinematics::getShape(const int /*level*/) const
{
    return d_shape;
}

#endif // included_FlappingFoilKinematics
