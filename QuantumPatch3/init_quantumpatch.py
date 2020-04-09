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
    wano_shells = wano["Tabs"]["Shells"]
    wano_core = wano_shells["Core Shell"]
    wano_general = wano["Tabs"]["General"]["General Settings"]
    qp_run = wano_general["QuantumPatch Type"]
    max_iter = wano_core["Screened Iterations"]
    # Indirection arrays to translate settings from WaNo expression to input
    qp_type = {"Polarized": "uncharged_equilibration",
               "Polaron/Exciton": "charged_equilibration",
               "Matrix EAIP": "matrix_eaip",
               "Excitonic Preprocessing": "excitonic_preprocessing"}
    shelltype = {"dynamic": "scf",
                 "static": "static"}
    # settings_ng "QuantumPatch" Category
    cfg["QuantumPatch"]["type"] = qp_type[qp_run]
    cfg["QuantumPatch"]["number_of_equilibration_steps"] = max_iter
    cfg["QuantumPatch"]["calculateJs"] = wano_general["Calculate Js"]
    cfg["Analysis"]["HigherOrder"] = {}
    cfg["Analysis"]["HigherOrder"]["ExtraJs"] = int(wano_general["Higher Order Js"])
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
        elif engine_name == "XTBEngine":
            print("here I am")
            entry = {
                "engine": engine_name,
                "threads": settings["Threads"],
                "memory": settings["Memory (MB)"],
                "charge_model": settings["Partial Charge Method"],
            }
        else:
            raise QuantumPatchWaNoError("Unknown DFT engine %s" % engine_name)
        if engine_name == "Turbomole":
            entry["scf_convergence"] = settings["SCF Convergence"]
        if engine["Fallback"]:
            entry["fallback"] = engine["Fallback Engine"]
        cfg["DFTEngine"]["user"][name] = entry
    # settings_ng "System" Category
    cfg["System"]["Core"] = dict()
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
    elif wano_core["Inner Part Method"] == "Number of Random Pairs":
        cfg["System"]["Core"]["type"] = "random_molstate_pairs"
        cfg["System"]["Core"]["number"] = wano_core["Number of Molecules"]
    elif wano_core["Inner Part Method"] == "Number of Random Crosspairs":
        cfg["System"]["Core"]["type"] = "random_molstate_crosspairs"
        cfg["System"]["Core"]["number"] = wano_core["Number of Molecules"]
    elif wano_core["Inner Part Method"] == "list of Molecule IDs":
        cfg["System"]["Core"]["type"] = "list"
        cfg["System"]["Core"]["list"] = wano_core["list of Molecule IDs"]
    by_iter = dict()  # Inserts engine_by_iter section
    if wano_core["Different Engine on Last Iteration"]:
        by_iter["LastUncharged"] = wano_core["Last Iteration Engine"]
        by_iter["LastCharged"] = wano_core["Last Iteration Engine"]
        by_iter["Dimer"] = wano_core["Last Iteration Engine"]
    cfg["System"]["Core"]["engine_by_iter"] = by_iter
    cfg["System"]["Core"]["engine"] = wano_core["Used Engine"]
    cfg["System"]["Core"]["default_molstates"] = wano_core["Default Molecular States"]
    cfg["System"]["Core"]["GeometricalOptimizationSteps"] = []
    i = 0
    cfg["System"]["Shells"] = dict()
    for shell in wano_shells["Outer Shells"]:
        cfg["System"]["Shells"][str(i)] = {
            "cutoff": shell["Shell"]["Cutoff Radius"],
            "type": shelltype[shell["Shell"]["Shelltype"]],
            "engine": shell["Shell"]["Used Engine"]
        }
        by_iter = dict()  # Inserts engine_by_iter section
        if shell["Shell"]["Different Engine on Last Iteration"]:
            by_iter["LastUncharged"] = shell["Shell"]["Last Iteration Engine"]
            by_iter["LastCharged"] = shell["Shell"]["Last Iteration Engine"]
            by_iter["Dimer"] = shell["Shell"]["Last Iteration Engine"]
        cfg["System"]["Shells"][str(i)]["engine_by_iter"] = by_iter
        i += 1
    cfg["System"]["MolStates"] = dict()
    i = 0
    for molstate in wano["Tabs"]["General"]["Molecular States"]:
        cfg["System"]["MolStates"][str(i)] = {
            "charge": molstate["State"]["Charge"],
            "multiplicity": molstate["State"]["Multiplicity"],
            "excited_state_of_interest": molstate["State"]["Excited State of Interest"],
            "roots": molstate["State"]["Roots"]
        }
        i += 1
    # Analysis section options
    if wano_general["QuantumPatch Type"] == "Matrix EAIP":
        if wano_general["Include in-matrix Lambda Calculation"]:
            cfg["Analysis"]["MatrixEAIP"]["do_lambda"] = True
        else:
            cfg["Analysis"]["MatrixEAIP"]["do_lambda"] = False
    # Write modified settings file to disk.
    with open("settings_ng.yml", "w") as qpngout:
        yaml.dump(cfg, qpngout, default_flow_style=False)
