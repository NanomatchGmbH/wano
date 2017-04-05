#!/bin/bash

source $EXTMOS/KIT/config

$SHREDDERBIN/AnaMobyExe.py temperature={{ wano["Temperature [K]"] | float }}\
                           lambda_lumo={{ wano["Lambda LUMO [eV]"] | float }}\
                           lambda_homo={{ wano["Lambda HOMO [eV]"] | float }}\
                           lumo_edge={{ wano["LUMO Edge File"] }}\
                           homo_edge={{ wano["HOMO Edge File"] }}\
                           homo\
                           lumo

