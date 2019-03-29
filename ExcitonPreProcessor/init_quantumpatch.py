#!/usr/bin/env python3

"""
Script that uses WaNo input to write QuantumPatch input.
"""

import yaml


class QuantumPatchWaNoError(Exception):
    pass


if __name__ == "__main__":
    with open("rendered_wano.yml", "r") as wanoin:
        wano = yaml.load(wanoin)
    with open("qp_settings_template.yml", "r") as qpngin:
        cfg = yaml.load(qpngin)  # Script will modify this and re-write it
    # Shorthands
    wano_general = wano["Tabs"]["General"]["General Settings"]
    wano_shells = wano["Tabs"]["Shells"]
    wano_core = wano_shells["Core Shell"]
    # settings_ng "DFTEngine" Category
    cfg["DFTEngine"]["user"] = dict()
    for engine in wano["Tabs"]["Engines"]["DFT Engines"]:
        # Reformats engine output from NewQP rendered WaNo
        engine_name = engine["Engine"]
        name = engine["Name"]
        settings = engine["%s Settings" % engine_name]
        if engine_name == "Turbomole" or engine_name == "Psi4":
            entry = {
                "engine": engine_name,
                "basis": settings["Basis"],
                "functional": settings["Functional"],
                "threads": settings["Threads"],
                "memory": settings["Memory (MB)"],
                "dispersion": settings["D3(BJ) Dispersion Correction"],
                "charge_model": settings["Partial Charge Method"],
            }
        elif engine_name == "DFTB+":
            entry = {
                "engine": "DFTBplus",
                "threads": settings["Threads"],
                "memory": settings["Memory (MB)"],
                "dispersion": settings["D3(BJ) Dispersion Correction"],
                "charge_model": settings["Partial Charge Method"],
            }
        elif engine_name == "Dalton":
            entry = {
                "engine": "Dalton",
                "threads": settings["Threads"],
                "memory": settings["Memory (MB)"]
            }
        else:
            raise QuantumPatchWaNoError("Unknown DFT engine %s" % engine_name)
        if engine_name == "Turbomole":
            entry["scf_convergence"] = settings["SCF Convergence"]
        if engine["Fallback"]:
            entry["fallback"] = engine["Fallback Engine"]
        cfg["DFTEngine"]["user"][name] = entry
    cfg["DFTEngine"]["last_iter"] = dict()
    # settings_ng "System" Category
    if wano_core["Inner Part Method"] == "Number of Molecules":
        cfg["System"]["Core"]["type"] = "number"
        cfg["System"]["Core"]["number"] = wano_core["Number of Molecules"]
    elif wano_core["Inner Part Method"] == "Inner Box Cutoff":
        cfg["System"]["Core"]["type"] = "distance"
        cfg["System"]["Core"]["distance"] = {
            "cutoff_x": wano_core["Inner Box Cutoff"]["Cutoff x direction"],
            "cutoff_y": wano_core["Inner Box Cutoff"]["Cutoff y direction"],
            "cutoff_z": wano_core["Inner Box Cutoff"]["Cutoff z direction"]
        }
    elif wano_core["Inner Part Method"] == "List of Molecule IDs":
        cfg["System"]["Core"]["type"] = "list"
        cfg["System"]["Core"]["list"] = wano_core["list of Molecule IDs"]
    by_iter = dict()  # Inserts engine_by_iter section
    if wano_core["Different Engine on Last Iteration"]:
        by_iter["LastUncharged"] = wano_core["Last Iteration Engine"]
        by_iter["LastCharged"] = wano_core["Last Iteration Engine"]
    cfg["System"]["Core"]["engine_by_iter"] = by_iter
    cfg["System"]["Core"]["engine"] = wano_core["Used Engine"]
    cfg["System"]["Core"]["GeometricalOptimizationSteps"] = []
    # Analysis section options
    general = wano["Tabs"]["General"]
    if general["Fluorescence"]["enabled"]:
        cfg["Analysis"]["Excitonic"]["Fluorescence"]["enabled"] = True
        cfg["Analysis"]["Excitonic"]["Fluorescence"]["DFTEngine"] = general["Fluorescence"]["Engine"]
    if general["Phosphorescence"]["enabled"]:
        cfg["Analysis"]["Excitonic"]["Phosphorescence"]["enabled"] = True
        cfg["Analysis"]["Excitonic"]["Phosphorescence"]["DFTEngine"] = general["Phosphorescence"]["Dalton Engine"]
    if general["TTA Rates"]["enabled"]:
        cfg["Analysis"]["Excitonic"]["TTA"]["enabled"] = True
        cfg["Analysis"]["Excitonic"]["TTA"]["DFTEngine"] = general["TTA Rates"]["Engine"]
        cfg["Analysis"]["Excitonic"]["TTA"]["roots"] = general["TTA Rates"]["roots"]
    if general["TPQ Rates"]["enabled"]:
        cfg["Analysis"]["Excitonic"]["TPQ"]["enabled"] = True
        cfg["Analysis"]["Excitonic"]["TPQ"]["anion"] = general["TPQ Rates"]["anion"]
        cfg["Analysis"]["Excitonic"]["TPQ"]["cation"] = general["TPQ Rates"]["cation"]
        cfg["Analysis"]["Excitonic"]["TPQ"]["DFTEngine"] = general["TPQ Rates"]["Engine"]
        cfg["Analysis"]["Excitonic"]["TPQ"]["roots"] = general["TPQ Rates"]["roots"]
    # Write modified settings file to disk.
    with open("settings_ng.yml", "w") as qpngout:
        yaml.dump(cfg, qpngout, default_flow_style=False)
