#!/bin/bash

export NANOVER="V2"
source $NANOMATCH/$NANOVER/configs/quantumpatch.config

/usr/bin/env python3 init_parametrizer.py

echo "Running $NANOMATCH/$NANOVER/QuantumPatch/MolecularTools/Parametrizer.py"
$NANOMATCH/$NANOVER/QuantumPatch/MolecularTools/Parametrizer.py


DEPTOOLS=$NANOMATCH/$NANOVER/deposit3/Tools
SIMPY=$NANOMATCH/$NANOVER/simona/python
export PYTHONPATH=$SIMPY:$PYTHONPATH

python3 $DEPTOOLS/SPFgeneratorV2.py output_molecule.mol2 temporary_molecule_with_dhs.spf
python3 ./merge_dh.py molecule.spf temporary_molecule_with_dhs.spf > molecule_with_dh.spf

rm temporary_molecule_with_dhs.spf
mv molecule_with_dh.spf molecule.spf
zip report.zip output_molecule.mol2 molecule.pdb molecule.spf

