#!/bin/python

import yaml, sys


s0 = sys.argv[1]
s1 = sys.argv[2]

def converter_eV_to_nm(entry):
    entry= 1240/ entry
    return entry

with open (s0, 'r') as inf:
    data_0 = yaml.load(inf)

with open (s1, 'r') as inf2:
    data_1 = yaml.load(inf2)

s0_entry = data_0['Excitation energy 0']
s1_entry = data_1['Excitation energy 0']

in_dict= {}

in_dict.update({"Stokes shift results:":
                    {"Excitation energy S0-S1 (S0 opt geometry) in eV:" : s0_entry,
                     "Excitation energy S0-S1 (S1 opt geometry) in eV:" : s1_entry,
                    "Stokes shift in eV::" : s0_entry - s1_entry,
                    "Excitation energy S0-S1 (S0 opt geometry) in nm:" : converter_eV_to_nm(s0_entry),
                    "Excitation energy S0-S1 (S1 opt geometry) in nm:" : converter_eV_to_nm(s1_entry),
                    "Stokes shift in nm::" : converter_eV_to_nm(s0_entry) - converter_eV_to_nm(s1_entry)}})

with open('results.yml', 'w') as f:
    yaml.dump(in_dict, f)






