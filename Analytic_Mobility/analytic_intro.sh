#!/bin/bash

source $NANOMATCH/configs/quantumpatch.config

$SHREDDERBIN/AnaMobyExe.py temperature={{ wano["Temperature [K]"] | float }}\
                           lambda_lumo_file={{ wano["Lambda LUMO Energy File"] }}\
                           lambda_homo_file={{ wano["Lambda HOMO Energy File"] }}\
                           lumo_edge={{ wano["LUMO Edge File"] }}\
                           homo_edge={{ wano["HOMO Edge File"] }}\
                           homo\
                           lumo

