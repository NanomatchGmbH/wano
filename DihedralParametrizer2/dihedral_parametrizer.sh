#!/bin/bash

export NANOVER="V2"

source $NANOMATCH/$NANOVER/configs/DihedralParametrizer2.config

HASDHS=$(grep dihedral molecule.spf| wc -l)
if [ "$HASDHS" == "0" ]
then
    python -c 'import yaml, sys; print(yaml.safe_load(sys.stdin))' < molecule.spf > /dev/null 2> /dev/null
    if [ ! $? -eq 0 ]
    then
        echo "Could not read spf file. Exiting. Please check the format."
        exit 1
    fi

    echo "No dihedrals found in pdb. Exiting and renaming input file to dh file."
    mv molecule.spf dihedral_forcefield.spf
    exit 0
fi

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
    dihedral_parametrizer2.py -joblist -pdb molecule.pdb -spf molecule.spf -n "{{ wano["Number of Steps"] | int }}" -engine "{{ wano["evaluation engine"] }}" -relax_engine "FF" -func "{{ wano["DFT Parameters"]["Functional"] }}" -basis "{{ wano["DFT Parameters"]["Basis"] }}" -eval_iter "{{ wano["evaluation points"] }}"  -mc_scale "{{ wano["MC step multiplier"] }}"  -scf_iter "{{ wano["scf iterations"] }}"
    $MPI_PATH/bin/mpirun -np $UC_TOTAL_PROCESSORS python -m mpi4py $DIHEDRAL_PARAMETRIZER_PATH/threadfarm/bin/thread_mpi_exe.py joblist
else
    dihedral_parametrizer2.py -pdb molecule.pdb -spf molecule.spf -n "{{ wano["Number of Steps"] | int }}" -engine "{{ wano["evaluation engine"] }}" -relax_engine "FF" -func "{{ wano["DFT Parameters"]["Functional"] }}" -basis "{{ wano["DFT Parameters"]["Basis"] }}" -eval_iter "{{ wano["evaluation points"] }}"  -mc_scale "{{ wano["MC step multiplier"] }}"  -scf_iter "{{ wano["scf iterations"] }}"
fi 




if [ -d $WORKING_DIR ]
then
    rsync -av $WORKING_DIR/* $DATA_DIR/ --exclude "stdout" --exclude "stderr"
    cd $DATA_DIR
    rm -r $WORKING_DIR
fi
