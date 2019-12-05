#!/bin/bash
export NANOVER=V2
source $NANOMATCH/$NANOVER/configs/lightforge.config
unzip lightforge_data_subset.zip
awk '$1!="analysis_autorun:" {print $0}' settings > autorun_settings
echo "analysis_autorun: True" >> autorun_settings

export OMP_NUM_THREADS=1

if [ "$UC_TOTAL_PROCESSORS" -gt 1 ]
then
    $MPI_PATH/bin/mpirun -genvall -machinefile $HOSTFILE lightforge.py -s autorun_settings
else
    $MPI_PATH/bin/mpirun -n 1 lightforge.py -s autorun_settings
fi 
#zip -r outpout.zip  material/*.png experiments/*.dat experiments/*.png experiments/*.txt

