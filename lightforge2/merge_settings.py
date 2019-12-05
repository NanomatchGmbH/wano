#!/usr/bin/env python3
from __future__ import print_function
import os,sys

import yaml


def merge(user, default):
    if isinstance(user,dict) and isinstance(default,dict):
        for k,v in default.items():
            user[k] = merge(user[k],v)
    else:
        user=default
    return user

with open(sys.argv[1],'r') as infile:
    fileone = yaml.load(infile)

for otherfile in sys.argv[2:]:
    with open(otherfile,'r') as infile:
        otherf_obj = yaml.load(infile)
    fileone = merge(fileone,otherf_obj)

with open(sys.argv[1],'w') as outfile:
    outfile.write(yaml.dump(fileone))
