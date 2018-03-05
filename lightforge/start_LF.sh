#!/bin/bash
source $NANOMATCH/configs/lightforge.config

export OMP_NUM_THREADS=1

if [ "$UC_TOTAL_PROCESSORS" -gt 1 ]
then
    $MPI_PATH/bin/mpirun --mca btl ^openib -x PATH -x PYTHONPATH -hostfile $HOSTFILE lightforge.py -s settings
else
    lightforge.py -s settings
fi 
zip -r outpout.zip  material/*.png experiments/*.dat experiments/*.png experiments/*.txt

count=`ls -1 experiments/*.png 2>/dev/null | wc -l`
if [ $count != 0 ];then 
	if [ ! -f DriftDiffusion-in.yml ]; then
    	touch DriftDiffusion-in.yml
	fi
fi 
