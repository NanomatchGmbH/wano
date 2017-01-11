#/bin/sh

# exit the script if any statement returns a non-true return value
set -e

export GMX_NO_QUOTES=1

if [ -z $1 ]; then
	PREV=init
else
	PREV=$1
fi

STEPS=`ls *mdp`

for X in $STEPS; do
	NAME=`basename $X .mdp`
	GROMPP="grompp_d -f $NAME.mdp -po $NAME-full.mdp -o $NAME.tpr -c $PREV.gro"
	if [ -f $PREV.trr ]; then
		GROMPP=$GROMPP" -t $PREV.trr"
	fi
	$GROMPP -maxwarn 2  2>&1 | tee $NAME-grompp.out
	mdrun_d -v -deffnm $NAME 2>&1 | tee $NAME-mdrun.out
	PREV=$NAME
done

#
echo 14 16 21 | g_energy -f 05-NPT > AVERAGED_DATA.txt

