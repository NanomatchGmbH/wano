#!/bin/bash

export NANOVER="V3"

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
    rsync -a $DATA_DIR/* $WORKING_DIR/ --exclude "*.stderr" --exclude "*.stdout"
    cd $WORKING_DIR
fi

export OMP_NUM_THREADS=1


if [ "$UC_TOTAL_PROCESSORS" -gt 1 ]
then
    dihedral_parametrizer2.py -joblist -pdb molecule.pdb -spf molecule.spf -n "{{ wano["Number of Steps"] | int }}" -engine "{{ wano["evaluation engine"] }}" -relax_engine "FF" -func "{{ wano["DFT Parameters"]["Functional"] }}" -basis "{{ wano["DFT Parameters"]["Basis"] }}" -mc_scale "{{ wano["algorithm settings"]["MC step multiplier"] }}"  -scf_iter "{{ wano["algorithm settings"]["scf iterations"] }}" {% if wano["intra forcefield settings"]["optimize forcefield"] == True %} -pp -cb -do -st {% if wano["intra forcefield settings"]["Trainingsset"] == "Set of Vac Mols" %} -eval_iter "{{ wano["intra forcefield settings"]["Trainingsset settings"]["evaluation points"] }}" -tcat "{{ wano["intra forcefield settings"]["Trainingsset settings"]["train set acc temp"] }}" {% endif %} {% if wano["intra forcefield settings"]["Trainingsset"] == "From Files" %} -led -eaf evaluation_angles.dat -eef evaluation_energies.dat {% endif %} {% endif %} > $DATA_DIR/dhparm_preprocessing.stdout 2> $DATA_DIR/dhparm_preprocessing.stderr
    $MPI_PATH/bin/mpirun -genvall -machinefile $HOSTFILE python -m mpi4py $DIHEDRAL_PARAMETRIZER_PATH/threadfarm/bin/thread_mpi_exe.py joblist  > $DATA_DIR/dhparm_run.stdout 2> $DATA_DIR/dhparm_run.stderr
else
    dihedral_parametrizer2.py -pdb molecule.pdb -spf molecule.spf -n "{{ wano["Number of Steps"] | int }}" -engine "{{ wano["evaluation engine"] }}" -relax_engine "FF" -func "{{ wano["DFT Parameters"]["Functional"] }}" -basis "{{ wano["DFT Parameters"]["Basis"] }}" -mc_scale "{{ wano["algorithm settings"]["MC step multiplier"] }}"  -scf_iter "{{ wano["algorithm settings"]["scf iterations"] }}" {% if wano["intra forcefield settings"]["optimize forcefield"] == True %} -pp -cb -do -st {% if wano["intra forcefield settings"]["Trainingsset"] == "Set of Vac Mols" %} -eval_iter "{{ wano["intra forcefield settings"]["Trainingsset settings"]["evaluation points"] }}" -tcat "{{ wano["intra forcefield settings"]["Trainingsset settings"]["train set acc temp"] }}" {% endif %} {% if wano["intra forcefield settings"]["Trainingsset"] == "From Files" %} -led -eaf evaluation_angles.dat -eef evaluation_energies.dat {% endif %} {% endif %}
fi 




if [ -d $WORKING_DIR ]
then
    rsync -a $WORKING_DIR/* $DATA_DIR/ --exclude "DihedralParametrizer2.stderr" --exclude "DihedralParametrizer2.stdout"
    cd $DATA_DIR
    rm -r $WORKING_DIR
fi
