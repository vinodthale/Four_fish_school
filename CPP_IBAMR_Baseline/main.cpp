// Baseline C++ IBAMR Implementation - 4 Fish Without Odor Dynamics
// This is a simplified version focusing only on fluid-structure interaction

#include <SAMRAI_config.h>
#include <petscsys.h>

// SAMRAI headers
#include <BergerRigoutsos.h>
#include <CartesianGridGeometry.h>
#include <LoadBalancer.h>
#include <StandardTagAndInitialize.h>

// IBAMR headers
#include <ibamr/ConstraintIBMethod.h>
#include <ibamr/IBExplicitHierarchyIntegrator.h>
#include <ibamr/IBStandardForceGen.h>
#include <ibamr/IBStandardInitializer.h>
#include <ibamr/INSStaggeredHierarchyIntegrator.h>

// IBTK headers
#include <ibtk/AppInitializer.h>
#include <ibtk/IBTKInit.h>
#include <ibtk/muParserCartGridFunction.h>
#include <ibtk/muParserRobinBcCoefs.h>

#include <ibamr/app_namespaces.h>

// Application objects
#include "IBEELKinematics.h"

/*******************************************************************************
 * Baseline Implementation - 4 Undulating Fish WITHOUT Odor Transport
 * 
 * This code simulates fluid-structure interaction with 4 fish using IBAMR.
 * Odor transport has been REMOVED for baseline performance comparison.
 *
 * For full implementation with odor, see ../CPP_IBAMR_With_Odor/
 *******************************************************************************/

int main(int argc, char* argv[])
{
    // Initialize IBAMR and libraries
    IBTKInit ibtk_init(argc, argv, MPI_COMM_WORLD);

    {
        // Initialize application
        Pointer<AppInitializer> app_initializer = new AppInitializer(argc, argv, "IB.log");
        Pointer<Database> input_db = app_initializer->getInputDatabase();

        // Get visualization parameters
        const bool dump_viz_data = app_initializer->dumpVizData();
        const bool uses_visit = dump_viz_data && !app_initializer->getVisItDataWriter().isNull();

        // Create Navier-Stokes integrator
        Pointer<INSHierarchyIntegrator> navier_stokes_integrator = new INSStaggeredHierarchyIntegrator(
            "INSStaggeredHierarchyIntegrator",
            app_initializer->getComponentDatabase("INSStaggeredHierarchyIntegrator"));

        // NOTE: NO AdvDiffHierarchyIntegrator - this is the baseline without odor!

        // Create IB method
        const int num_structures = input_db->getIntegerWithDefault("num_structures", 1);
        Pointer<ConstraintIBMethod> ib_method_ops = new ConstraintIBMethod(
            "ConstraintIBMethod", 
            app_initializer->getComponentDatabase("ConstraintIBMethod"), 
            num_structures);

        // Create IB hierarchy integrator
        Pointer<IBHierarchyIntegrator> time_integrator =
            new IBExplicitHierarchyIntegrator("IBHierarchyIntegrator",
                                              app_initializer->getComponentDatabase("IBHierarchyIntegrator"),
                                              ib_method_ops,
                                              navier_stokes_integrator);

        // Create grid geometry and patch hierarchy
        Pointer<CartesianGridGeometry<NDIM>> grid_geometry = new CartesianGridGeometry<NDIM>(
            "CartesianGeometry", app_initializer->getComponentDatabase("CartesianGeometry"));
        Pointer<PatchHierarchy<NDIM>> patch_hierarchy = new PatchHierarchy<NDIM>("PatchHierarchy", grid_geometry);

        // Create gridding algorithm
        Pointer<StandardTagAndInitialize<NDIM>> error_detector =
            new StandardTagAndInitialize<NDIM>("StandardTagAndInitialize",
                                               time_integrator,
                                               app_initializer->getComponentDatabase("StandardTagAndInitialize"));
        Pointer<BergerRigoutsos<NDIM>> box_generator = new BergerRigoutsos<NDIM>();
        Pointer<LoadBalancer<NDIM>> load_balancer =
            new LoadBalancer<NDIM>("LoadBalancer", app_initializer->getComponentDatabase("LoadBalancer"));
        Pointer<GriddingAlgorithm<NDIM>> gridding_algorithm =
            new GriddingAlgorithm<NDIM>("GriddingAlgorithm",
                                        app_initializer->getComponentDatabase("GriddingAlgorithm"),
                                        error_detector,
                                        box_generator,
                                        load_balancer);

        // Configure IB solver
        Pointer<IBStandardInitializer> ib_initializer = new IBStandardInitializer(
            "IBStandardInitializer", app_initializer->getComponentDatabase("IBStandardInitializer"));
        ib_method_ops->registerLInitStrategy(ib_initializer);
        Pointer<IBStandardForceGen> ib_force_fcn = new IBStandardForceGen();
        ib_method_ops->registerIBLagrangianForceFunction(ib_force_fcn);

        // Set up velocity/pressure initial conditions
        if (input_db->keyExists("VelocityInitialConditions"))
        {
            Pointer<CartGridFunction> u_init = new muParserCartGridFunction(
                "u_init", app_initializer->getComponentDatabase("VelocityInitialConditions"), grid_geometry);
            navier_stokes_integrator->registerVelocityInitialConditions(u_init);
        }

        if (input_db->keyExists("PressureInitialConditions"))
        {
            Pointer<CartGridFunction> p_init = new muParserCartGridFunction(
                "p_init", app_initializer->getComponentDatabase("PressureInitialConditions"), grid_geometry);
            navier_stokes_integrator->registerPressureInitialConditions(p_init);
        }

        // Set up boundary conditions
        const IntVector<NDIM>& periodic_shift = grid_geometry->getPeriodicShift();
        vector<RobinBcCoefStrategy<NDIM>*> u_bc_coefs(NDIM);
        if (periodic_shift.min() > 0)
        {
            for (unsigned int d = 0; d < NDIM; ++d)
            {
                u_bc_coefs[d] = nullptr;
            }
        }
        else
        {
            for (unsigned int d = 0; d < NDIM; ++d)
            {
                const std::string bc_coefs_name = "u_bc_coefs_" + std::to_string(d);
                const std::string bc_coefs_db_name = "VelocityBcCoefs_" + std::to_string(d);
                u_bc_coefs[d] = new muParserRobinBcCoefs(
                    bc_coefs_name, app_initializer->getComponentDatabase(bc_coefs_db_name), grid_geometry);
            }
            navier_stokes_integrator->registerPhysicalBoundaryConditions(u_bc_coefs);
        }

        // Set up visualization
        Pointer<VisItDataWriter<NDIM>> visit_data_writer = app_initializer->getVisItDataWriter();
        Pointer<LSiloDataWriter> silo_data_writer = app_initializer->getLSiloDataWriter();
        if (uses_visit)
        {
            ib_initializer->registerLSiloDataWriter(silo_data_writer);
            ib_method_ops->registerLSiloDataWriter(silo_data_writer);
            time_integrator->registerVisItDataWriter(visit_data_writer);
            // NOTE: No adv_diff_integrator registration - no odor transport!
        }

        // Initialize hierarchy
        time_integrator->initializePatchHierarchy(patch_hierarchy, gridding_algorithm);

        // Create kinematics for 4 fish
        vector<Pointer<ConstraintIBKinematics>> ibkinematics_ops_vec;
        Pointer<ConstraintIBKinematics> ib_kinematics_op;
        
        // Fish 1 (bottom-left)
        ib_kinematics_op = new IBEELKinematics(
            "eel2d_1",
            app_initializer->getComponentDatabase("ConstraintIBKinematics")->getDatabase("eel2d_1"),
            ib_method_ops->getLDataManager(),
            patch_hierarchy);
        ibkinematics_ops_vec.push_back(ib_kinematics_op);

        // Fish 2 (top-left)
        ib_kinematics_op = new IBEELKinematics(
            "eel2d_2",
            app_initializer->getComponentDatabase("ConstraintIBKinematics")->getDatabase("eel2d_2"),
            ib_method_ops->getLDataManager(),
            patch_hierarchy);
        ibkinematics_ops_vec.push_back(ib_kinematics_op);

        // Fish 3 (bottom-right)
        ib_kinematics_op = new IBEELKinematics(
            "eel2d_3",
            app_initializer->getComponentDatabase("ConstraintIBKinematics")->getDatabase("eel2d_3"),
            ib_method_ops->getLDataManager(),
            patch_hierarchy);
        ibkinematics_ops_vec.push_back(ib_kinematics_op);

        // Fish 4 (top-right)
        ib_kinematics_op = new IBEELKinematics(
            "eel2d_4",
            app_initializer->getComponentDatabase("ConstraintIBKinematics")->getDatabase("eel2d_4"),
            ib_method_ops->getLDataManager(),
            patch_hierarchy);
        ibkinematics_ops_vec.push_back(ib_kinematics_op);

        // Register kinematics with IB method
        ib_method_ops->registerConstraintIBKinematics(ibkinematics_ops_vec);

        // Write out initial visualization data
        int iteration_num = time_integrator->getIntegratorStep();
        double loop_time = time_integrator->getIntegratorTime();
        if (dump_viz_data && uses_visit)
        {
            pout << "\n\nWriting visualization files...\n\n";
            time_integrator->setupPlotData();
            visit_data_writer->writePlotData(patch_hierarchy, iteration_num, loop_time);
            silo_data_writer->writePlotData(iteration_num, loop_time);
        }

        // Main time integration loop
        double loop_time_end = time_integrator->getEndTime();
        double dt = 0.0;
        while (!MathUtilities<double>::equalEps(loop_time, loop_time_end) && time_integrator->stepsRemaining())
        {
            iteration_num = time_integrator->getIntegratorStep();
            loop_time = time_integrator->getIntegratorTime();

            pout << "\n";
            pout << "+++++++++++++++++++++++++++++++++++++++++++++++++++\n";
            pout << "At beginning of timestep # " << iteration_num << "\n";
            pout << "Simulation time is " << loop_time << "\n";

            dt = time_integrator->getMaximumTimeStepSize();
            time_integrator->advanceHierarchy(dt);
            loop_time += dt;

            pout << "\n";
            pout << "At end       of timestep # " << iteration_num << "\n";
            pout << "Simulation time is " << loop_time << "\n";
            pout << "+++++++++++++++++++++++++++++++++++++++++++++++++++\n";
            pout << "\n";

            // Write visualization data
            iteration_num += 1;
            const bool last_step = !time_integrator->stepsRemaining();
            if (dump_viz_data && uses_visit && (iteration_num % app_initializer->getVizDumpInterval() == 0 || last_step))
            {
                pout << "\nWriting visualization files...\n\n";
                time_integrator->setupPlotData();
                visit_data_writer->writePlotData(patch_hierarchy, iteration_num, loop_time);
                silo_data_writer->writePlotData(iteration_num, loop_time);
            }

            // Write restart data
            if (app_initializer->dumpRestartData() && (iteration_num % app_initializer->getRestartDumpInterval() == 0 || last_step))
            {
                pout << "\nWriting restart files...\n\n";
                RestartManager::getManager()->writeRestartFile(app_initializer->getRestartDumpDirectory(), iteration_num);
            }

            // Write timer data
            if (app_initializer->dumpTimerData() && (iteration_num % app_initializer->getTimerDumpInterval() == 0))
            {
                pout << "\nWriting timer data...\n\n";
                TimerManager::getManager()->print(plog);
            }
        }

        // Cleanup
        for (unsigned int d = 0; d < NDIM; ++d) delete u_bc_coefs[d];

    } // cleanup dynamically allocated objects prior to shutdown

    return 0;
} // main
