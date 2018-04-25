#!/bin/bash

source $NANOMATCH/configs/parameterizer.config

WORKING_DIR=`pwd`
DATA_DIR=$WORKING_DIR

if [ -d $SCRATCH ]
then
    WORKING_DIR=$SCRATCH/`whoami`/`uuidgen`
    mkdir -p $WORKING_DIR
    rsync --exclude=stdout --exclude=stderr -a $DATA_DIR/*  $WORKING_DIR/
    cd $WORKING_DIR
fi

export OMP_NUM_THREADS=1

export DFTENGINE="{{ wano["Hardware Parameters"]["Engine"] }}"
export DFT_MEMORY="{{ wano["Hardware Parameters"]["DFT Memory [MB]"] | int }}"
export GAUSSIAN_SCFHEADER="{{ wano["Hardware Parameters"]["GaussianSCFHeader"] }}"

export BASIS="{{ wano["Parameters"]["Basis"] }}"
export FUNCTIONAL="{{ wano["Parameters"]["Functional"] }}"

MYPDB="{{ wano["Deposit PDB"] }}"
MYSPF="{{ wano["Deposit SPF"] }}"


DH_PRESENT=$(cat $MYSPF | grep dihedral | wc -l)

if [ $DH_PRESENT -lt 1 ]
then
    echo "$MYSPF did not contain dihedral angles, not starting parametrization"
    mv molecule.pdb molecule_dh.pdb
    mv molecule.spf molecule_dh.spf
    exit 0
fi

Deposit.py -prepare-dihedral-files "{{ wano["Deposit PDB"] }}" "{{ wano["Deposit SPF"] }}" "{{ wano["Parameters"]["Number of Steps"] | int }}"

rm -f *.sml *.cml

for xmlfile in $(find . -maxdepth 1 -mindepth 1 -type f -name "*.xml.gz")
do
    mybase=${xmlfile%.xml.gz}
    mkdir -p $mybase
    mv $xmlfile $mybase
done

OLDPWD=$PWD
find . -maxdepth 2 -mindepth 2 -type f -name "*.xml.gz" | parallel -j $UC_PROCESSORS_PER_NODE 'cd {//} && pwd && Deposit.py -run-dihedral-file {/} 1 > {/.}.out'
cd $OLDPWD

find . -name "*_snap.pdb" | xargs mv -t .

Deposit.py -assemble-potential "{{ wano["Deposit SPF"] }}"

rm molecule.spf
mv molecule.pdb molecule_dh.pdb
mv dihedral_forcefield.spf molecule_dh.spf

if [ -d $WORKING_DIR ]
then
    cp -r $WORKING_DIR/* $DATA_DIR/
    cd $DATA_DIR
    rm -r $WORKING_DIR
fi

