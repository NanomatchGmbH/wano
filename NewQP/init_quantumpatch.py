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
               "Polaron/Exciton": "charged_equilibration"}
    shelltype = {"dynamic": "scf",
                 "static": "static"}
    # settings_ng top level settings
    cfg["calculate_Js"] = wano_general["Calculate Js"]
    # settings_ng "QuantumPatch" Category
    cfg["QuantumPatch"]["type"] = qp_type[qp_run]
    cfg["QuantumPatch"]["number_of_equilibration_steps"] = max_iter
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
                "charge_model": settings["Partial Charge Method"],
            }
        elif engine_name == "DFTB+":
            entry = {
                "engine": engine_name,
                "thirdorder": True,
                "threads": settings["Threads"],
                "memory": settings["Memory (MB)"],
                "charge_model": settings["Partial Charge Method"],
            }
        else:
            raise QuantumPatchWaNoError("Unknown DFT engine %s" % engine_name)
        cfg["DFTEngine"]["user"][name] = entry
    cfg["DFTEngine"]["last_iter"] = dict()
    if wano_core["Different Engine on Last Iteration"]:
        name = wano_core["Last Iteration Engine"]
        cfg["DFTEngine"]["last_iter"]["settings"] = "sameas:DFTEngine.user.%s" % name
        engine_name = None
        for engine in wano["Tabs"]["Engines"]["DFT Engines"]:
            if engine["Name"] == name:
                engine_name = engine["Engine"]
                break
        if not engine_name:
            msg = "Unknown engine %s in Last Iteration Engine." % name
            raise QuantumPatchWaNoError(msg)
        cfg["DFTEngine"]["last_iter"]["name"] = engine_name
        cfg["DFTEngine"]["last_iter"]["enable_switch"] = True
    else:
        cfg["DFTEngine"]["last_iter"] = {
            "settings": "sameas:DFTEngine.defaults.Turbomole",
            "name": "Turbomole",
            "enable_switch": False
        }
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
    i = 0
    cfg["System"]["Shells"] = dict()
    for shell in wano_shells["Outer Shells"]:
        cfg["System"]["Shells"][str(i)] = {
            "cutoff": shell["Shell"]["Cutoff Radius"],
            "type": shelltype[shell["Shell"]["Shelltype"]],
            "engine": shell["Shell"]["Used Engine"]
        }
        i += 1
    cfg["System"]["MolStates"] = dict()
    i = 0
    for molstate in wano["Tabs"]["General"]["Molecular States"]:
        cfg["System"]["MolStates"][str(i)] = {
            "charge": molstate["State"]["Charge"],
            "multiplicity": molstate["State"]["Multiplicity"],
            "excitation": molstate["State"]["Excitation"]
        }
        i += 1
    # Write modified settings file to disk.
    with open("settings_ng.yml", "w") as qpngout:
        yaml.dump(cfg, qpngout, default_flow_style=False)
