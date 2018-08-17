#!/bin/bash
source $NANOMATCH/configs/lightforge.config

cp settings autorun_settings
echo "analysis_autorun: True" >> autorun_settings
mkdir experiments
mkdir experiments/replay_0
unzip replay.zip
unzip QP_inputs.zip
mv part*.npz experiments/replay_0/
mkdir material
cp material.npz material/material_0.npz
echo "job_id: 0 settings_id: 0 mat_id: 0 field_direction: [1.0, 0.0, 0.0] field_strength: 0.03 initial_charges: [0, 0] Temperature: 300.0\n" > experiments/experiment_inventory_0.txt

export OMP_NUM_THREADS=1

if [ "$UC_TOTAL_PROCESSORS" -gt 1 ]
then
    $MPI_PATH/bin/mpirun --mca btl ^openib -x PATH -x PYTHONPATH -x SCRATCH -hostfile $HOSTFILE lightforge.py -s autorun_settings
else
    $MPI_PATH/bin/mpirun -np 1 lightforge.py -s autorun_settings
fi 
#zip -r outpout.zip  material/*.png experiments/*.dat experiments/*.png experiments/*.txt

