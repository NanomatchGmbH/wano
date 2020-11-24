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
wano["DFT Engine"]["Memory (MB)"] = float(environ["UC_MEMORY_PER_NODE"]) * 0.85


if wano["DFT Engine"]["Turbomole Settings"]["Partial Charge Method"] == "No Charges":
    wano["DFT Engine"]["Turbomole Settings"]["Partial Charge Method"] = "ESP"
    wano["DFT Engine"]["Turbomole Settings"]["partial_charges"] =  False

if wano["DFT Engine"]["Turbomole Settings"]["Analysis options"] == "Generate orbital plots":
    wano["DFT Engine"]["Turbomole Settings"]["plot_orb"] = {"homo" :True,"lumo":True}
elif wano["DFT Engine"]["Turbomole Settings"]["Analysis options"] == "Estimate electrostatic disorder":
    wano["DFT Engine"]["Turbomole Settings"]["ESP_surface"] = {'enabled':True, 'mode': "by element", 'vdw_scale': [1.0,2.0,3.5],'points': 30}
elif  wano["DFT Engine"]["Turbomole Settings"]["Analysis options"]  == "Generate ESP surface plot":
    wano["DFT Engine"]["Turbomole Settings"]["ESP_surface"] = {'enabled':True, 'mode': "by element", 'vdw_scale': 1.0,'points': 50,'plot_grid': True}


del wano["DFT Engine"]["Turbomole Settings"]["Analysis options"]


with open("parametrizer_settings.yml", "w") as ymlout:
    yaml.safe_dump(wano, ymlout)
