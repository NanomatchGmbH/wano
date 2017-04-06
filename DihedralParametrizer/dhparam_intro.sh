#!/bin/bash

source $EXTMOS/KIT/config

WORKING_DIR=`pwd`

export OMP_NUM_THREADS=1

export DFTENGINE="{{ wano["Hardware Parameters"]["Engine"] }}"
export DFT_MEMORY="{{ wano["Hardware Parameters"]["DFT Memory [MB]"] | int }}"

export BASIS="{{ wano["Parameters"]["Basis"] }}"
export FUNCTIONAL="{{ wano["Parameters"]["Functional"] }}"

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
