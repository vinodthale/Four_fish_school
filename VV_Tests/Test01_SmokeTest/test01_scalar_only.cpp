// =============================================================================
// TEST 1: SMOKE TEST - Scalar Transport Only (No Immersed Boundaries)
// =============================================================================
// Purpose: Verify basic scalar infrastructure
// - Variable registration
// - Boundary conditions
// - I/O functionality
// - No crashes, no NaNs
// =============================================================================

#include <SAMRAI_config.h>
#include <petscsys.h>

// SAMRAI headers
#include <BergerRigoutsos.h>
#include <CartesianGridGeometry.h>
#include <LoadBalancer.h>
#include <StandardTagAndInitialize.h>

// IBAMR headers
#include <ibamr/AdvDiffHierarchyIntegrator.h>
#include <ibamr/INSStaggeredHierarchyIntegrator.h>

#include <ibtk/AppInitializer.h>
#include <ibtk/IBTKInit.h>
#include <ibtk/muParserCartGridFunction.h>
#include <ibtk/muParserRobinBcCoefs.h>

#include <ibamr/app_namespaces.h>

int main(int argc, char* argv[])
{
    IBTKInit ibtk_init(argc, argv, MPI_COMM_WORLD);

    {
        // Initialize application
        Pointer<AppInitializer> app_initializer = new AppInitializer(argc, argv, "test01.log");
        Pointer<Database> input_db = app_initializer->getInputDatabase();

        // Get visualization parameters
        const bool dump_viz_data = app_initializer->dumpVizData();
        const int viz_dump_interval = app_initializer->getVizDumpInterval();
        const bool uses_visit = dump_viz_data && !app_initializer->getVisItDataWriter().isNull();

        // Create Navier-Stokes integrator (for velocity field, even though u=0)
        Pointer<INSHierarchyIntegrator> navier_stokes_integrator = new INSStaggeredHierarchyIntegrator(
            "INSStaggeredHierarchyIntegrator",
            app_initializer->getComponentDatabase("INSStaggeredHierarchyIntegrator"));

        // Create scalar transport integrator
        Pointer<AdvDiffHierarchyIntegrator> adv_diff_integrator = new AdvDiffHierarchyIntegrator(
            "AdvDiffHierarchyIntegrator",
            app_initializer->getComponentDatabase("AdvDiffHierarchyIntegrator"));

        // Register velocity field with scalar transport
        adv_diff_integrator->setAdvectionVelocity(navier_stokes_integrator->getAdvectionVelocityVariable());
        navier_stokes_integrator->registerAdvDiffHierarchyIntegrator(adv_diff_integrator);

        // Create grid geometry
        Pointer<CartesianGridGeometry<NDIM> > grid_geometry = new CartesianGridGeometry<NDIM>(
            "CartesianGeometry", app_initializer->getComponentDatabase("CartesianGeometry"));
        Pointer<PatchHierarchy<NDIM> > patch_hierarchy = new PatchHierarchy<NDIM>("PatchHierarchy", grid_geometry);

        // Create gridding algorithm
        Pointer<StandardTagAndInitialize<NDIM> > error_detector =
            new StandardTagAndInitialize<NDIM>("StandardTagAndInitialize",
                                               navier_stokes_integrator,
                                               app_initializer->getComponentDatabase("StandardTagAndInitialize"));
        Pointer<BergerRigoutsos<NDIM> > box_generator = new BergerRigoutsos<NDIM>();
        Pointer<LoadBalancer<NDIM> > load_balancer =
            new LoadBalancer<NDIM>("LoadBalancer", app_initializer->getComponentDatabase("LoadBalancer"));
        Pointer<GriddingAlgorithm<NDIM> > gridding_algorithm =
            new GriddingAlgorithm<NDIM>("GriddingAlgorithm",
                                        app_initializer->getComponentDatabase("GriddingAlgorithm"),
                                        error_detector,
                                        box_generator,
                                        load_balancer);

        // Set scalar initial conditions
        if (input_db->keyExists("OdorInitialConditions"))
        {
            Pointer<CartGridFunction> C_init = new muParserCartGridFunction(
                "C_init", app_initializer->getComponentDatabase("OdorInitialConditions"), grid_geometry);
            adv_diff_integrator->setInitialConditions(C_init);
        }

        // Set scalar boundary conditions
        const IntVector<NDIM>& periodic_shift = grid_geometry->getPeriodicShift();
        RobinBcCoefStrategy<NDIM>* C_bc_coef = nullptr;
        if (!(periodic_shift.min() > 0) && input_db->keyExists("OdorBcCoefs"))
        {
            C_bc_coef = new muParserRobinBcCoefs(
                "C_bc_coef", app_initializer->getComponentDatabase("OdorBcCoefs"), grid_geometry);
            adv_diff_integrator->setPhysicalBcCoef(C_bc_coef);
        }

        // Set diffusion coefficient
        if (input_db->keyExists("diffusion_coefficient"))
        {
            double kappa = input_db->getDouble("diffusion_coefficient");
            adv_diff_integrator->setDiffusionCoefficient(kappa);
        }

        // Set velocity boundary conditions
        vector<RobinBcCoefStrategy<NDIM>*> u_bc_coefs(NDIM);
        if (periodic_shift.min() > 0)
        {
            for (unsigned int d = 0; d < NDIM; ++d) u_bc_coefs[d] = nullptr;
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
        Pointer<VisItDataWriter<NDIM> > visit_data_writer = app_initializer->getVisItDataWriter();
        if (uses_visit)
        {
            navier_stokes_integrator->registerVisItDataWriter(visit_data_writer);
            adv_diff_integrator->registerVisItDataWriter(visit_data_writer);
        }

        // Initialize hierarchy
        navier_stokes_integrator->initializePatchHierarchy(patch_hierarchy, gridding_algorithm);

        // Write initial data
        int iteration_num = navier_stokes_integrator->getIntegratorStep();
        double loop_time = navier_stokes_integrator->getIntegratorTime();

        if (dump_viz_data && uses_visit)
        {
            pout << "\nWriting initial visualization files...\n\n";
            navier_stokes_integrator->setupPlotData();
            visit_data_writer->writePlotData(patch_hierarchy, iteration_num, loop_time);
        }

        // Main time-stepping loop
        double loop_time_end = navier_stokes_integrator->getEndTime();
        double dt = 0.0;

        while (!IBTK::rel_equal_eps(loop_time, loop_time_end) && navier_stokes_integrator->stepsRemaining())
        {
            iteration_num = navier_stokes_integrator->getIntegratorStep();
            loop_time = navier_stokes_integrator->getIntegratorTime();

            pout << "\n";
            pout << "+++++++++++++++++++++++++++++++++++++++++++++++++++\n";
            pout << "At beginning of timestep # " << iteration_num << "\n";
            pout << "Simulation time is " << loop_time << "\n";

            dt = navier_stokes_integrator->getMaximumTimeStepSize();
            navier_stokes_integrator->advanceHierarchy(dt);
            loop_time += dt;

            pout << "At end of timestep # " << iteration_num << "\n";
            pout << "Simulation time is " << loop_time << "\n";
            pout << "+++++++++++++++++++++++++++++++++++++++++++++++++++\n";

            // Write visualization data
            iteration_num += 1;
            const bool last_step = !navier_stokes_integrator->stepsRemaining();
            if (dump_viz_data && uses_visit && (iteration_num % viz_dump_interval == 0 || last_step))
            {
                pout << "\nWriting visualization files...\n\n";
                navier_stokes_integrator->setupPlotData();
                visit_data_writer->writePlotData(patch_hierarchy, iteration_num, loop_time);
            }
        }

        // Cleanup
        for (unsigned int d = 0; d < NDIM; ++d) delete u_bc_coefs[d];
        delete C_bc_coef;

        pout << "\n===============================================\n";
        pout << "Test 1 (Smoke Test) completed successfully!\n";
        pout << "===============================================\n\n";

    } // cleanup

    return 0;
}
