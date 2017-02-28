#!/bin/bash

source $EXTMOS/KIT/config

Deposit.py {% for element in wano["TABS"]["Molecules"]["Molecules"] %} molecule.{{ loop.index - 1 }}.pdb={{ element["Molecule"] }}  molecule.{{ loop.index - 1 }}.spf={{ element["Forcefield"] }} molecule.{{ loop.index - 1 }}.conc={{ element["Mixing Ratio"] }} {% endfor %}  simparams.Thi={{ wano["TABS"]["Simulation Parameters"]["Simulation Parameters"]["Initial Temperature [K]"] }}  simparams.Tlo={{ wano["TABS"]["Simulation Parameters"]["Simulation Parameters"]["Final Temperature [K]"] }} simparams.sa.Tacc={{ wano["TABS"]["Simulation Parameters"]["Simulation Parameters"]["SA Acc Temp"] }} simparams.sa.cycles={{ wano["TABS"]["Simulation Parameters"]["Simulation Parameters"]["Number of SA cycles"] }} simparams.sa.steps={{ wano["TABS"]["Simulation Parameters"]["Simulation Parameters"]["Number of Steps"] }} simparams.Nmol={{ wano["TABS"]["Simulation Parameters"]["Simulation Parameters"]["Number of Molecules"] }} simparams.moves.dihedralmoves={{ wano["TABS"]["Simulation Parameters"]["Simulation Parameters"]["Dihedral Moves"] }}  Box.Lx={{ wano["TABS"]["Simulation Parameters"]["Simulation Box"]["Lx"] }}  Box.Ly={{ wano["TABS"]["Simulation Parameters"]["Simulation Box"]["Ly"] }}  Box.Lz={{ wano["TABS"]["Simulation Parameters"]["Simulation Box"]["Lz"] }}  Box.pbc_cutoff={{ wano["TABS"]["Simulation Parameters"]["Simulation Box"]["PBC"]["Cutoff"] }}  simparams.PBC={{ wano["TABS"]["Simulation Parameters"]["Simulation Box"]["PBC"]["enabled"] }} machineparams.ncpu=${UC_PROCESSORS_PER_NODE}
babel structure.cml structure.mol2
