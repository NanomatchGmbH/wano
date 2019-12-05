#!/bin/bash

export NANOVER="V2"
source $NANOMATCH/$NANOVER/configs/parametrizer.config

/usr/bin/env python3 init_parametrizer.py

echo "Running $NANOMATCH/$NANOVER/QuantumPatch/MolecularTools/Parametrizer.py"
$NANOMATCH/$NANOVER/QuantumPatch/MolecularTools/Parametrizer.py

add_dihedral_angles.sh output_molecule.mol2 molecule.spf

zip report.zip output_molecule.mol2 molecule.pdb molecule.spf

