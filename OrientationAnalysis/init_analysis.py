#!/usr/bin/env python3

"""
Script that uses WaNo input to write QuantumPatch input.
"""

import yaml


class QuantumPatchWaNoError(Exception):
    pass


if __name__ == "__main__":
    with open("qpanalysis_settings_template.yml", "r") as qpngin:
        cfg = yaml.load(qpngin)  # Script will modify this and re-write it
    # Orientation Analysis dict created by Emission WaNo
    with open("orientation_analysis.yml", "r") as oain:
        orientation_analysis = yaml.load(oain)
    orientation_analysis["enabled"] = True
    cfg["Analysis"]["Orientation"]["complex_axis"] = orientation_analysis
    # Write modified settings file to disk.
    with open("analysis_settings.yml", "w") as qpngout:
        yaml.dump(cfg, qpngout, default_flow_style=False)
