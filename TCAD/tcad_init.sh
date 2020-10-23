#!/bin/bash

export NANOVER="V4"
source $NANOMATCH/$NANOVER/configs/silvaco.config
python ./readwano.py > atlas.input

atlas atlas.input > out.log
