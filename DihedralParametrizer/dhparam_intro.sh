#!/bin/bash

source $EXTMOS/KIT/config

WORKING_DIR=`pwd`

export OMP_NUM_THREADS=1

export DFTENGINE="{{ wano["Hardware Parameters"]["Engine"] }}"
export DFT_MEMORY="{{ wano["Hardware Parameters"]["DFT Memory [MB]"] | int }}"

export BASIS="{{ wano["Parameters"]["Basis"] }}"
export FUNCTIONAL="{{ wano["Parameters"]["Functional"] }}"

Deposit.py -prepare-dihedral-files "{{ wano["Deposit PDB"] }}" "{{ wano["Deposit SPF"] }}" "{{ wano["Parameters"]["Number of Steps"] | int }}"

find . -maxdepth 1 -mindepth 1 -type f -name "*.xml.gz" | parallel -j $UC_PROCESSORS_PER_NODE 'Deposit.py -run-dihedral-file "{}" 1 > "{.}".out'

Deposit.py -assemble-potential "{{ wano["Deposit SPF"] }}"
