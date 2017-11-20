#!/bin/bash
source $NANOMATCH/configs/lightforge.config

export OMP_NUM_THREADS=1

if [ "$UC_TOTAL_PROCESSORS" -gt 1 ]
then
    $MPI_PATH/bin/mpirun -np $UC_TOTAL_PROCESSORS lightforge.py -s settings
else
    lightforge.py -s settings
fi 
#zip -r outpout.zip range_expander/nearest_neighbour_distance_type1.png range_expander/nearest_neighbour_distance_type2.png material/energy_crosssection_*x.png material/transfer_integrals experiments/*.png experiments/current_density_* experiments/IQE* experiments/mobilities_* range_expander/*PBC.xyz