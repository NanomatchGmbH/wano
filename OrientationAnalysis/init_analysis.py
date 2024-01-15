#!/usr/bin/env python3

"""
Script that uses WaNo input to write QuantumPatch input.
"""

import yaml
from QuantumPatch.QPAnalysis.AnalysisSettings import AnalysisSettings


class QuantumPatchWaNoError(Exception):
    pass


def string_to_bool(tdanalysis_enabled):
    if isinstance(tdanalysis_enabled,str):
        if tdanalysis_enabled == "True":
            tdanalysis_enabled = True
        else:
            tdanalysis_enabled = False
    return tdanalysis_enabled

if __name__ == "__main__":
    anasettings = AnalysisSettings()
    cfg = anasettings.as_dict()
    #with open("qpanalysis_settings_template.yml", "r") as qpngin:
    #    cfg = yaml.safe_load(qpngin)  # Script will modify this and re-write it
    # Orientation Analysis dict created by Emission WaNo
    with open("rendered_wano.yml",'rt') as wano_in:
        rendered_wano = yaml.safe_load(wano_in)
    cfg["Morphology"]["structure"] = rendered_wano["Morphology"]
    tdanalysis_enabled = string_to_bool(rendered_wano["Enable TD Analysis"])
    if tdanalysis_enabled:
        with open("orientation_analysis_input.yml", "r") as oain:
            orientation_analysis = yaml.safe_load(oain)
        orientation_analysis["enabled"] = True
        cfg["Analysis"]["Orientation"]["complex_axis"] = orientation_analysis
    axis_enabled = string_to_bool(rendered_wano["Enable Axes Analysis"])
    outdict = {}
    if axis_enabled:
        outdict["axis"] = {}
        outdict["axis"]["enabled"] = True
        outdict["axis"]["bins"] = int(rendered_wano["number of bins"])
        axes = rendered_wano["Axes"]
        for axis_id,axdef in enumerate(axes):
            id1 = int(axdef["atomid 1"])
            id2 = int(axdef["atomid 2"])
            ids_ar = [id1,id2]
            outdict["axis"][str(axis_id)] = {}
            outdict["axis"][str(axis_id)]["Ids"] = ids_ar
            outdict["axis"][str(axis_id)]["moltype"] = axdef["moltype"]
            outdict["axis"][str(axis_id)]["label"] = axdef["label"]
    cfg["Analysis"]["Orientation"].update(outdict)
    # Write modified settings file to disk.
    with open("analysis_settings.yml", "w") as qpngout:
        yaml.dump(cfg, qpngout, default_flow_style=False)
