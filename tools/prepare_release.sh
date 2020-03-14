#!/bin/bash

TODAY=$(date "+%F")
git archive --format zip --prefix=wanos/ --output $TODAY-simstack-wanos.zip master

