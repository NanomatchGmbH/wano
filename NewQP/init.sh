#!/bin/bash

source $NANOMATCH/configs/quantumpatch.config
source $NANOMATCH/configs/dftb.config


# SANITY CHECKS

if [ "$UC_TOTAL_PROCESSORS" == "1" ]
then
 echo "QuantumPatch needs at least 2 processors to run, because the first processor only handles communication, exiting"
 exit 9012
fi

if [ "AA$SCRATCH" == "AA" ]
then
    echo "Not using Scratch, please setup scratch. Exiting."
    use_scratch=False
    exit 5012
else
    use_scratch=True
fi

# End of SANITY CHECKS

function varisset {
        if [ -z ${!1+x} ]
        then
                echo "false"
        else
                echo "true"
        fi
}

export OMP_NUM_THREADS=1

# Here we check, whether variables are set and add them to the mpirun exports. This is not required for mpirun with PBS/Torque, but required with everything else.
# We could also specify only the required ones, but we do not know that a priori (i.e. whether Turbomole or Gaussian is to be used.
# To avoid warnings, we therefore check first whether something is set and only then add it to the command.
environmentvariables=( "OMP_NUM_THREADS" "PATH" "HOSTFILE" "PYTHONPATH" "SCRATCH" "SHREDDERPATH" "SHREDDERPYTHON" "TURBODIR" "TURBOMOLE_SYSNAME" "TURBOTMPDIR" "GAUSS_SCRDIR" "g09root" "G09BASIS" "GAUSS_ARCHDIR" "GAUSS_BSDDIR" "GAUSS_EXEDIR" "GAUSS_LEXEDIR" "GV_DIR" "PGI_TERM" "_DSM_BARRIER" "NM_LICENSE_SERVER" "LD_LIBRARY_PATH" "DFTBPATH" "DFTBSLKO" )

ENVCOMMAND=""
for var in "${environmentvariables[@]}"
do
  if [ "$(varisset ${var})" == "true" ]
  then
        ENVCOMMAND="$ENVCOMMAND -x $var"
  fi
done

export QP_RUN="{{ wano["Tabs"]["General"]["General Settings"]["Run QuantumPatch"] }}"
export LAMBDA_RUN="{{ wano["Tabs"]["General"]["General Settings"]["Include Lambda/EA/IP Calculation"] }}"

echo "Creating input files."
if [ "$LAMBDA_RUN" == "True" ]
then
    /usr/bin/env python3 init_lambda.py
fi

if [ "$QP_RUN" == "True" ]
then
    /usr/bin/env python3 init_quantumpatch.py
fi

if [ "$LAMBDA_RUN" == "True" ]
then
    echo "Running $NANOMATCH/QuantumPatch/MolecularTools/LambdaEAIP.py"
    $NANOMATCH/QuantumPatch/MolecularTools/LambdaEAIP.py
fi
if [ "$QP_RUN" == "True" ]
then
    echo "Running $MPI_PATH/bin/mpirun -genvall -machinefile $HOSTFILE python -m mpi4py $SHREDDERPATH/QuantumPatchNG.py >> progress.txt 2> shredder_mpi_stderr"
    $MPI_PATH/bin/mpirun -genvall -machinefile $HOSTFILE python -m mpi4py $SHREDDERPATH/QuantumPatchNG.py >> progress.txt 2> shredder_mpi_stderr
fi

zip -r report.zip Analysis
