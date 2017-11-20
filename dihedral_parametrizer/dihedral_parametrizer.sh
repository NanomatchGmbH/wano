#!/bin/bash

source $NANOMATCH/configs/dihedral_parametrizer.config

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
    dihedral_parametrizer.py -j -f "{{ wano["Molecule mol2"] }}" -n "{{ wano["Parameters"]["Number of Steps"] | int }}" -simona -dft "{{ wano["DFT single point"] }}" -func "{{ wano["Parameters"]["Functional"] }}" -basis "{{ wano["Parameters"]["Basis"] }}"
    $MPI_PATH/bin/mpirun -np $UC_TOTAL_PROCESSORS thread_mpi_exe.py joblist
else
    dihedral_parametrizer.py -f "{{ wano["Molecule mol2"] }}" -n "{{ wano["Parameters"]["Number of Steps"] | int }}" -simona -dft "{{ wano["DFT single point"] }}" -func "{{ wano["Parameters"]["Functional"] }}" -basis "{{ wano["Parameters"]["Basis"] }}"
fi 




if [ -d $WORKING_DIR ]
then
    cp -r $WORKING_DIR/* $DATA_DIR/
    cd $DATA_DIR
    rm -r $WORKING_DIR
fi
