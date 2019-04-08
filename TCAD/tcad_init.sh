#!/bin/bash

export NANOVER="V2"
source $NANOMATCH/$NANOVER/configs/silvaco.config
python ./readwano.py > atlas.input

atlas atlas.input > out.log
