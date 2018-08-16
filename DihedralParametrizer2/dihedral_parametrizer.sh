#!/bin/bash

source $NANOMATCH/configs/DihedralParametrizer2.config

WORKING_DIR=`pwd`
DATA_DIR=$WORKING_DIR

if [ -d $SCRATCH ]
then
    WORKING_DIR=$SCRATCH/`whoami`/`uuidgen`
    mkdir -p $WORKING_DIR
    cp -r $DATA_DIR/* $WORKING_DIR/
    cd $WORKING_DIR
fi

export OMP_NUM_THREADS=1



if [ "$UC_TOTAL_PROCESSORS" -gt 1 ]
then
    dihedral_parametrizer2.py -joblist -pdb molecule.pdb -spf molecule.spf -n "{{ wano["Number of Steps"] | int }}" -engine "{{ wano["evaluation engine"] }}" -relax_engine "{{ wano["relax engine"] }}" -func "{{ wano["DFT Parameters"]["Functional"] }}" -basis "{{ wano["DFT Parameters"]["Basis"] }}" -eval_iter "{{ wano["evaluation points"] }}"  -mc_scale "{{ wano["MC step multiplier"] }}"  -scf_iter "{{ wano["scf iterations"] }}"
    $MPI_PATH/bin/mpirun -np $UC_TOTAL_PROCESSORS thread_mpi_exe.py joblist
else
    dihedral_parametrizer2.py -pdb molecule.pdb -spf molecule.spf -n "{{ wano["Number of Steps"] | int }}" -engine "{{ wano["evaluation engine"] }}" -relax_engine "{{ wano["relax engine"] }}" -func "{{ wano["DFT Parameters"]["Functional"] }}" -basis "{{ wano["DFT Parameters"]["Basis"] }}" -eval_iter "{{ wano["evaluation points"] }}"  -mc_scale "{{ wano["MC step multiplier"] }}"  -scf_iter "{{ wano["scf iterations"] }}"
fi 




if [ -d $WORKING_DIR ]
then
    cp -r $WORKING_DIR/* $DATA_DIR/
    cd $DATA_DIR
    rm -r $WORKING_DIR
fi
