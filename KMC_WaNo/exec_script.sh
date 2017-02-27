#!/bin/bash

source $EXTMOS/UBAH/config
mpirun -np {{ wano["Simulation method"]["Number of processes"] }} $KMC_dir/KMC_PM simulation.ini {{ wano["Simulation method"]["Number of subgroups"] }} $KMC_inputs/ $KMC_outputs/
