#!/bin/bash

source $NANOMATCH/configs/quantumpatch.config

/usr/bin/env python3 init_parametrizer.py

echo "Running $NANOMATCH/QuantumPatch/MolecularTools/Parametrizer.py"
$NANOMATCH/QuantumPatch/MolecularTools/Parametrizer.py


DEPTOOLS=$NANOMATCH/deposit3/Tools
SIMPY=$NANOMATCH/simona/python
export PYTHONPATH=$SIMPY:$PYTHONPATH

python3 $DEPTOOLS/SPFgeneratorV2.py output_molecule.mol2 temporary_molecule_with_dhs.spf
python3 ./merge_dh.py molecule.spf temporary_molecule_with_dhs.spf > molecule_with_dh.spf

rm temporary_molecule_with_dhs.spf
mv molecule_with_dh.spf molecule.spf
zip report.zip output_molecule.mol2 molecule.pdb molecule.spf

