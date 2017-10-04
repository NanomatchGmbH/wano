#!/bin/bash

source $NANOMATCH/configs/parameterizer.config

WORKING_DIR=`pwd`

if [ $OMP_NUM_THREADS -gt 1 ]
then
    if [ -d $TURBODIR ]
    then
        #Turbomole config for multi cpu runs
        export PARA_ARCH=SMP
        export PARNODES=$OMP_NUM_THREADS
        export PATH=$TURBODIR/bin/`sysname`:$PATH
    fi
fi

export MOLECULE="{{ wano["Molecule (Mol2)"] }}"
INPUTBASE="${MOLECULE%.mol2}"
export SHREDDER_INPUT="$INPUTBASE.cml"

babel $MOLECULE $SHREDDER_INPUT
babel $MOLECULE ${INPUTBASE}_2dsketch.png

export DFTENGINE="{{ wano["Hardware Parameters"]["Engine"] }}"
export DFT_MEMORY="{{ wano["Hardware Parameters"]["DFT Memory [MB]"] | int }}"

export DO_GEOOPT="{{ wano["Geometrical Optimization"]["Optimize"] }}"
export BASIS="{{ wano["Geometrical Optimization"]["Basis"] }}"
export FUNCTIONAL="{{ wano["Geometrical Optimization"]["Functional"] }}"

if [ "$DO_GEOOPT" == "True" ]
then
    python2 $SHREDDERBIN/exe_generate_settings.py
    echo "python2 $SHREDDERBIN/geometrical_optimization.py $SHREDDER_INPUT"
    python2 $SHREDDERBIN/geometrical_optimization.py $SHREDDER_INPUT
    babel opt_${INPUTBASE}.xyz $MOLECULE
    babel opt_${INPUTBASE}.xyz $SHREDDER_INPUT    
fi

export PARTIAL_CHARGE_METHOD="{{ wano["Partial Charge Settings"]["Partial Charge Method"] }}"
export BASIS="{{ wano["Partial Charge Settings"]["Basis"] }}"
export FUNCTIONAL="{{ wano["Partial Charge Settings"]["Functional"] }}"

rm -f settings.yml

Deposit.py -calc-charges $MOLECULE $MOLECULE
Deposit.py -generate_spf_from_mol2 $MOLECULE $INPUTBASE.spf
Deposit.py -render-tachyon $MOLECULE

packReport.py $MOLECULE
nanoReporter.py --input=report.zip --type=odt
