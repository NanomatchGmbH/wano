export SHREDDER_INPUT={{ wano["Morphology (CML)"] }}

export DFTENGINE="{{ wano["DFT Settings"]["Engine"] }}"
export BASIS="{{ wano["DFT Settings"]["Basis"] }}"
export FUNCTIONAL="{{ wano["DFT Settings"]["Functional"] }}"
export DFT_MEMORY="{{ wano["Hardware Parameters"]["DFT Memory [MB]"] | int }}"

source $NANOMATCH/configs/quantumpatch.config

LambdaWrapper.sh
