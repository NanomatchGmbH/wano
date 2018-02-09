#!/bin/bash
source $NANOMATCH/configs/lightforge.config

export OMP_NUM_THREADS=1

if [ "$UC_TOTAL_PROCESSORS" -gt 1 ]
then
    $MPI_PATH/bin/mpirun -np $UC_TOTAL_PROCESSORS lightforge.py -s settings
else
    lightforge.py -s settings
fi 
zip -r outpout.zip  material/*.png experiments/*.dat experiments/*.png experiments/*.txt

