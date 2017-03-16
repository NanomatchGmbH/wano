#!/bin/bash

source $EXTMOS/UBAH/config
mkdir kmc_output
mpirun -np {{ wano["Simulation method"]["Number of processes"] }} $KMC_dir/KMC_PM simulation.ini {{ wano["Simulation method"]["Number of subgroups"] }} ./ ./kmc_output
