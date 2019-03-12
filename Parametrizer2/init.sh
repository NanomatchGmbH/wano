#!/bin/bash

### REMOVE FOR RELEASE, WORKAROUND FOR NMC DEV ENVIRONMENT ###
export NANOMATCH=/home/nanodev_build/nanomatch/
### REMOVE FOR RELEASE, WORKAROUND FOR NMC DEV ENVIRONMENT ###

source $NANOMATCH/configs/quantumpatch.config

/usr/bin/env python3 init_parametrizer.py

echo "Running $NANOMATCH/QuantumPatch/MolecularTools/Parametrizer.py"
$NANOMATCH/QuantumPatch/MolecularTools/Parametrizer.py

zip report.zip output_molecule.mol2 molecule.pdb molecule.spf