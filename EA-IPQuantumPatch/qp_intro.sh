#!/bin/bash

source $NANOMATCH/configs/quantumpatch.config
source $NANOMATCH/configs/dftb.config


function varisset {
        if [ -z ${!1+x} ]
        then
                echo "false"
        else
                echo "true"
        fi
}


function prune_hosts_percpu {
	#$1 is hostfile (HOSTFF)
	HOSTFF=$1
	#$2 is CPU_PER_JOB (CPU_PER_JOB_FF)
	CPU_PER_JOB_FF=$2
	cat $HOSTFF | sort | uniq -c > counted_hosts

	gawk -v CPU_PER_JOB_FF=$CPU_PER_JOB_FF '{
		if ($1 % CPU_PER_JOB_FF != 0)
		{
			printf("Node %s number of allocated cpus is %d, which is not divisible by the number of cpus per job %d.\n",$2,$1,CPU_PER_JOB_FF);
			printf("ABORT_DUE_TO_CPUCOUNT\n");
		}
		else
		{
			for (i = 0; i < $1/CPU_PER_JOB_FF; ++i)
			{
				printf("%s\n",$2);
			}
		}
	}' counted_hosts > new_hostfile
	rm -f counted_hosts
	if [ "$(grep ABORT_DUE_TO_CPUCOUNT new_hostfile | wc -l)" != "0" ]
	then
		echo "Error condition found, CPU count setup incorrectly. Check new_hostfile."
		exit 6
	fi
}

function tolower {
    IN=$1
    echo -n $IN | tr '[:upper:]' '[:lower:]'
}


echo "EA-IP QuantumPatchWrapper v3.1"



# ----------------            Setting convenience exports for later ---------------#

export SHREDDER_INPUT="{{ wano["General Options"]["Morphology (CML)"] }}"
export BASIS="{{ wano["DFT Settings"]["Basis"] }}"
export FUNCTIONAL="{{ wano["DFT Settings"]["Functional"] }}"
export LASTITERFUNCTIONAL="{{ wano["DFT Settings"]["Last Iteration Functional"] }}"
export PARTIAL_CHARGE_METHOD="{{ wano["DFT Settings"]["Partial Charge Method"] }}"
export CHARGESTATES="{{ wano["DFT Settings"]["Charge States"] }}"
export SCREENEDITERATIONS="{{ wano["Self-consistency parameters"]["Screened Iterations"] }}"
export CALCULATE_LS="{{ wano["General Options"]["Calculate Lambdas"] }}"


export DAMPINGTRUEFALSE="{{ wano["Self-consistency parameters"]["Damping"] }}"

if [ "$DAMPINGTRUEFALSE" == "True" ]
then
    export USE_DAMPING="on"
else
    export USE_DAMPING="off"
fi

export DAMPING="{{ wano["Self-consistency parameters"]["Damping Factor"] }}"

export INNER_PART_METHOD="$(tolower {{ wano["Cutoffs"]["Inner Part Method"] }} )"
if [ "$INNER_PART_METHOD" == "Number of Molecules" ]
then
    export INNER_PART_METHOD="Number"
fi
export INNER_PART_CUT="{{ wano["Cutoffs"]["Inner Part Cutoff"] }}"
export INNER_PART_NUMMOL="{{ wano["Cutoffs"]["Number of Molecules"] }}"

export PAIRCUTOFF="{{ wano["Cutoffs"]["Pair Cutoff"] }}"
export ENVIRONMENT_RADIUS="{{ wano["Cutoffs"]["Environment Radius"] }}"
export DFT_MEMORY="{{ wano["Hardware Parameters"]["DFT Memory [MB]"] | int }}"

export LAMBDABASIS="{{ wano["DFT Settings"]["LambdaBasis"] }}"
export LAMBDAFUNCTIONAL="{{ wano["DFT Settings"]["LambdaFunctional"] }}"
export CHARGE_STATES="{{ wano["DFT Settings"]["Charge States"] }}"

# ----------------            Setting convenience exports for later ---------------#

WORKING_DIR=`pwd`

#echo "Running on $UC_PROCESSORS_PER_NODE processors for every $UC_"
export OMP_NUM_THREADS=$UC_PROCESSORS_PER_NODE

export PATH=$SHREDDERBIN:$PATH



echo "Running QuantumPatch for \"${SHREDDER_INPUT}\""
 
pcm="$(tolower {{ wano["DFT Settings"]["Partial Charge Method"] }} )"
if [ "$pcm" == "esp" ]
then
    tm_pcm="ESP"
else
    tm_pcm=$pcm
fi

if [ "$USE_DAMPING" == "on" ]
then
    USE_DAMPING_BOOL=True
else
    USE_DAMPING_BOOL=False
fi

if [ "AA$SCRATCH" == "AA" ]
then
    echo "Not using Scratch, please setup scratch. Exiting."
    use_scratch=False
    exit 5
else
    use_scratch=True
fi

if [ "AA$CALCULATE_LS" == "AA" ]
then
    CALCULATE_LS="False"
fi

if [ "AA$LAMBDABASIS" == "AA" ]
then
    LAMBDABASIS=$BASIS
fi

if [ "AA$LAMBDAFUNCTIONAL" == "AA" ]
then
    LAMBDAFUNCTIONAL=$FUNCTIONAL
fi


#Now we check how many CPUs we require per DFT job and prune the hostfile accordingly:
if [ "$(varisset CPUS_PER_JOB)" == "true" ]
then
	prune_hosts_percpu $HOSTFILE $CPUS_PER_JOB
	export HOSTFILE=`pwd`/new_hostfile
else
        export CPUS_PER_JOB=1
fi

$SHREDDERPATH/QuantumPatchPreprocessor.py 2>&1 >/dev/null #this creates the default config

$SHREDDERPATH/QuantumPatchPreprocessor.py INPUT=$SHREDDER_INPUT \
                dft_engine=turbomole \
                basisset_ridft_charged=$BASIS basisset_ridft_uncharged=$BASIS basis_gaussian=$BASIS basis_lambda_gaussian=$LAMBDABASIS basisset_lambda=$LAMBDABASIS \
                functional_lambda_gaussian=$LAMBDAFUNCTIONAL functional_gaussian=$FUNCTIONAL functional_ridft_charged=$FUNCTIONAL functional_ridft_uncharged=$FUNCTIONAL functional_lambda=$LAMBDAFUNCTIONAL \
                use_inner_part_only=True cutoff_distance_to_edge_x=$INNER_PART_CUT cutoff_distance_to_edge_y=$INNER_PART_CUT cutoff_distance_to_edge_z=$INNER_PART_CUT \
                inner_part_method=$INNER_PART_METHOD \
                inner_part_number=$INNER_PART_NUMMOL \
                use_screened_orbitals_for_pairs=True use_environment_for_pairs=True \
                gaussian_charges=$pcm partial_charges_method=$tm_pcm \
                cutoff=$PAIRCUTOFF \
                partial_charges_steps=$SCREENEDITERATIONS \
                polarization_iterations=$SCREENEDITERATIONS \
                damping=$DAMPING use_damping=$USE_DAMPING_BOOL \
                calculate_Js=False \
                calculate_lambda=$CALCULATE_LS \
                lambda_calculate_unique_mols=True \
                debug_mode=0 \
                gaussian_memory=$DFT_MEMORY \
                memory_ridft=$DFT_MEMORY \
                gaussian_numcpu=$CPUS_PER_JOB \
                use_crystal_shredder=False \
                polarization_cutoff=$ENVIRONMENT_RADIUS \
                shredder_type=EAIP \
                use_hybrid_shredder={{ wano["DFT Settings"]["Hybrid"] }} \
                use_scratch=$use_scratch \
                use_cpc=True \
                dftbplus_skfiles_path=$DFTBPARAMETERS \
                charge_states="$CHARGE_STATES" \
                change_functional_last_itr=True \
                functional_last_itr=$LASTITERFUNCTIONAL


if [ "$UC_TOTAL_PROCESSORS" == "1" ]
then
 echo "QuantumPatch needs at least 2 processors to run, because the first processor only handles communication, exiting"
 exit 9
fi

#Here we check, whether variables are set and add them to the mpirun exports. This is not required for mpirun with PBS/Torque, but required with everything else.
#We could also specify only the required ones, but we do not know that a priori (i.e. whether Turbomole or Gaussian is to be used.
#To avoid warnings, we therefore check first whether something is set and only then add it to the command.
environmentvariables=( "BASIS" "CALCULATE_JS" "CMLFILE" "CMLFILE_1" "DAMPING" "DFTENGINE" "DFT_MEMORY" "CPUS_PER_JOB" "FUNCTIONAL" "INPUT" "MMMCPS" "MMM_REPO" "MOLE_CONTROL" "OMP_NUM_THREADS" "PAIRCUTOFF" "PARTIAL_CHARGE_METHOD" "PATH" "HOSTFILE" "PYTHONPATH" "SCRATCH" "SCREENER" "SCREENEDITERATIONS" "SHREDDERBIN" "SHREDDERPATH" "SHREDDERPYTHON" "SHREDDER_INPUT" "SHREDDER_OUTPUT" "SHREDDER_OUTPUT_1" "TURBODIR" "TURBOMOLE_SYSNAME" "TURBOTMPDIR" "USE_DAMPING" "USE_INNER_PART_ONLY" "USE_ENVIRONMENT_FOR_PAIRS" "USE_SCREENED_ORBITALS_FOR_PAIRS"  "GAUSS_SCRDIR" "g09root" "G09BASIS" "GAUSS_ARCHDIR" "GAUSS_BSDDIR" "GAUSS_EXEDIR" "GAUSS_LEXEDIR" "GV_DIR" "PGI_TERM" "_DSM_BARRIER" "NM_LICENSE_SERVER" "LD_LIBRARY_PATH" "GAUSSIAN_SCFHEADER" "CRYSTAL_IMAGEFILE" "ENVIRONMENT_RADIUS" "USE_CRYSTAL_SHREDDER" "CENTRAL_UNIT_CELL" "SHREDDERTYPE" "HYBRIDSHREDDER" "DFTBPATH" "DFTBSLKO" "INNER_PART_CUT" "CHARGE_STATE" )

ENVCOMMAND=""
for var in "${environmentvariables[@]}"
do
  #echo "${var}"
  if [ "$(varisset ${var})" == "true" ]
  then
        ENVCOMMAND="$ENVCOMMAND -x $var"
        #echo "${var} is set"
  fi
done

echo "Running $MPI_PATH/bin/mpirun --mca btl ^openib $ENVCOMMAND -hostfile $HOSTFILE $SHREDDERPATH/QuantumPatch.py jobs/joblist"
$MPI_PATH/bin/mpirun --mca btl ^openib $ENVCOMMAND -hostfile $HOSTFILE $SHREDDERPATH/QuantumPatch.py jobs/joblist >> progress.txt 2> shredder_mpi_stderr

$SHREDDERPATH/bin/plot.py

rm -rf cpu_*

$SHREDDERBIN/convert_data_for_kmc.py

#zip -r output.zip 02output dimer environment *.cml monomers settings.yml -x environment/iteration\*/mol\*/gaussian.log environment/iteration\*/mol\*/gaussian.input environment/iteration\*/mol\*/check.chk monomers/mol\*/gaussian.log monomers/mol\*/gaussian.input  monomers/mol\*/check.chk monomers/\*.out monomers/\*coord
zip -r output.zip 02output data_for_kmc settings.yml
