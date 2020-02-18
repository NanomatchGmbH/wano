#!/usr/bin/env python3

"""
Script that uses WaNo input to write QuantumPatch input.
"""

from os import environ
import yaml

# Reads rendered WaNo file
with open("rendered_wano.yml", "r") as ymlin:
    wano = yaml.safe_load(ymlin)

wano["Molecule Settings"]["Parameter File"] = 'default'
wano["DFT Engine"]["Threads"] = environ["UC_TOTAL_PROCESSORS"]
wano["DFT Engine"]["Memory (MB)"] = environ["UC_MEMORY_PER_NODE"]

with open("parametrizer_settings.yml", "w") as ymlout:
    yaml.safe_dump(wano, ymlout)
