#!/bin/bash

echo "Running QPParametrizer"
QPParametrizer
$DEPTOOLS/add_dihedral_angles.sh output_molecule.mol2 molecule.spf

zip report.zip output_molecule.mol2 molecule.pdb molecule.spf
# cp rendered_wano.yml output_dict.yml
cat mol_data.yml >> output_dict.yml

obabel -imol2 output_molecule.mol2 -osvg > output_molecule.svg
