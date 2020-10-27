#!/usr/bin/env python3
from __future__ import print_function
import os,sys

import yaml
from yaml import CLoader


def merge(user, default):
    if isinstance(user,dict) and isinstance(default,dict):
        for k,v in default.items():
            if k in user:
                user[k] = merge(user[k],v)
            else:
                user[k] = v
    else:
        user=default
    return user

with open(sys.argv[1],'r') as infile:
    fileone = yaml.load(infile, Loader=CLoader)

for otherfile in sys.argv[2:]:
    with open(otherfile,'r') as infile:
        otherf_obj = yaml.load(infile, Loader=CLoader)
    fileone = merge(fileone,otherf_obj)

with open(sys.argv[1],'w') as outfile:
    outfile.write(yaml.dump(fileone,default_flow_style=None))
