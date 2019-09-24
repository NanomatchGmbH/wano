#!/bin/bash

export NANOVER="V2"
source $NANOMATCH/$NANOVER/configs/lightforge.config

if [ -f lf_output.zip ]; then
	unzip -d ./ lf_output.zip
	sleep 2
	rm lf_output.zip
fi

export OMP_NUM_THREADS=1

if [ -f override_settings.yml ]
then
    python ./merge_settings.py settings override_settings.yml
fi

if [ "$UC_TOTAL_PROCESSORS" -gt 1 ]
then
    $MPI_PATH/bin/mpirun -genvall -machinefile $HOSTFILE python -m mpi4py $LFPATH/lightforge.py -s settings
else
    lightforge.py -s settings
fi 
zip -r results.zip  results
zip -r lightforge_data.zip lightforge_data


if [ ! -f DriftDiffusion-in.yml ]; then
    touch DriftDiffusion-in.yml
fi
