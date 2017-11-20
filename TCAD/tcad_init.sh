#!/bin/bash

source $NANOMATCH/configs/silvaco.config
python ./readwano.py > atlas.input

atlas atlas.input > out.log
