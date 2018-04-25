export SHREDDER_INPUT={{ wano["General Options"]["Morphology (CML)"] }}
export CMLFILE={{ wano["General Options"]["Morphology (CML)"] }}
export CMLFILE_1={{ wano["General Options"]["Morphology (CML)"] }}
export SHREDDER_INPUT={{ wano["General Options"]["Morphology (CML)"] }}

export DFTENGINE="{{ wano["DFT Settings"]["Engine"] }}"
export BASIS="{{ wano["DFT Settings"]["Basis"] }}"
export FUNCTIONAL="{{ wano["DFT Settings"]["Functional"] }}"
export PARTIAL_CHARGE_METHOD="{{ wano["DFT Settings"]["Partial Charge Method"] }}"
export SCREENEDITERATIONS="{{ wano["Self-consistency parameters"]["Screened Iterations"] }}"

DAMPINGTRUEFALSE="{{ wano["Self-consistency parameters"]["Damping"] }}"

if [ "$DAMPINGTRUEFALSE" == "True" ]
then
    export USE_DAMPING="on"
else
    export USE_DAMPING="off"
fi

export DAMPING="{{ wano["Self-consistency parameters"]["Damping Factor"] }}"
export INNER_PART_CUT="{{ wano["Cutoffs"]["Inner Part Cutoff"] }}"
export PAIRCUTOFF="{{ wano["Cutoffs"]["Pair Cutoff"] }}"
export ENVIRONMENT_RADIUS="{{ wano["Cutoffs"]["Environment Radius"] }}"
export DFT_MEMORY="{{ wano["Hardware Parameters"]["DFT Memory [MB]"] | int }}"

export CALCULATE_JS="{{ wano["General Options"]["Calculate Js"] }}"
export CALCULATE_LS="{{ wano["General Options"]["Calculate Lambdas"] }}"

export LAMBDABASIS="{{ wano["DFT Settings"]["LambdaBasis"] }}"
export LAMBDAFUNCTIONAL="{{ wano["DFT Settings"]["LambdaFunctional"] }}"
export GAUSSIAN_SCFHEADER="{{ wano["DFT Settings"]["GaussianSCFHeader"] }}"

#if [ "$CALCULATE_JS" == "True" ]
#then
#    export CALCULATE_JS="on"
#else
#    export CALCULATE_JS="off"
#fi

source $NANOMATCH/configs/quantumpatch.config

QuantumPatch.sh
