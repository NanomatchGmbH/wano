#!/usr/bin/env python3

"""
Script that uses WaNo input to write QuantumPatch input.
"""

import yaml, copy
from yaml import CLoader
from treewalker.TreeWalker.TreeWalker import TreeWalker
from treewalker.TreeWalker.flatten_dict import flatten_dict

class WaNoSettingsReplacements:
    key_exchanges = {
       # Core Shell settings
       "Inner Part Method": "System.Core.type",

       "Inner Box Cutoff.Cutoff x direction": "System.Core.distance.cutoff_x",
       "Inner Box Cutoff.Cutoff y direction": "System.Core.distance.cutoff_y",
       "Inner Box Cutoff.Cutoff z direction": "System.Core.distance.cutoff_z",

       "list of Molecule IDs": "System.Core.list",
       "Number of Molecules": "System.Core.number",
       "Morphology": "QuantumPatch.morphology",

       # TM Settings
       "SinglePoint Settings.Basis" : "DFTEngine.user.Turbomole 1.basis",
       "SinglePoint Settings.Functional": "DFTEngine.user.Turbomole 1.functional",
       "SinglePoint Settings.SCF Convergence" : "DFTEngine.user.Turbomole 1.scf_convergence",
       "SinglePoint Settings.Geometry Convergence" : "DFTEngine.user.Turbomole 1.geometry_convergence",
       "SinglePoint Settings.Memory (MB)": "DFTEngine.user.Turbomole 1.memory",
       "SinglePoint Settings.Threads": "DFTEngine.user.Turbomole 1.threads",

       "Optimization Settings.Basis" : "DFTEngine.geo_opt.basis",
       "Optimization Settings.Functional": "DFTEngine.geo_opt.functional",
       "Optimization Settings.SCF Convergence" : "DFTEngine.geo_opt.scf_convergence",
       "Optimization Settings.Geometry Convergence" : "DFTEngine.geo_opt.geometry_convergence",
       "Optimization Settings.Memory (MB)": "DFTEngine.geo_opt.memory",
       "Optimization Settings.Threads": "DFTEngine.geo_opt.threads",
    }
    val_exchanges = {
       "Inner Box Cutoff": "distance",
       "Number of Molecules": "number",
       "list of Molecule IDs": "list",
    }
    def val_exchange_visitor(self, value, call_info):
        if value in self.val_exchanges.keys():
            return self.val_exchanges[value] 
        else:
            return value


if __name__ == "__main__":
    with open("rendered_wano.yml", "r") as wanoin:
        wano = yaml.load(wanoin, Loader=CLoader)
    with open("settings_ng.yml", "r") as qpngin:
        cfg = yaml.load(qpngin, Loader=CLoader)

    tw_wano = TreeWalker(wano)
    replace = WaNoSettingsReplacements()
    outdict = tw_wano.walker(path_visitor_function = None, data_visitor_function=replace.val_exchange_visitor, subdict_visitor_function = None, capture = True)

    tw_cfg = TreeWalker(cfg)
    flattened_outdict = flatten_dict(outdict)

    replaced_key_outdict = {}
    for key, val in flattened_outdict.items():
        if key in replace.key_exchanges:
            replaced_key_outdict[replace.key_exchanges[key]] = val
        else:
            replaced_key_outdict[key] = val

    for pointpath, value in replaced_key_outdict.items():
        tw_cfg[pointpath.split(".")] = value

    # Here are the hardcoded changes:
    tw_cfg['System.Shells'.split(".")] = {'0':tw_cfg.resolve('System.Shells.0'.split("."))}
    tw_cfg['System.Core.engine'.split(".")] = "Turbomole 1"
    tw_cfg['System.Shells.0.cutoff'.split(".")] = 0.001
    tw_cfg['System.Shells.0.engine'.split(".")] = "Turbomole 1"
    tw_cfg['Analysis.MatrixEAIP.do_lambda'.split(".")] = True
    tw_cfg['QuantumPatch.partial_charge_cutoff'.split(".")] = 0.0
    tw_cfg['QuantumPatch.number_of_equilibration_steps'.split(".")] = 2
    tw_cfg['QuantumPatch.type'.split(".")] = "matrix_eaip"

    final_outdict = tw_cfg.walker(path_visitor_function = None, data_visitor_function=None, subdict_visitor_function = None, capture = True)

    with open("settings_ng.yml", "wt") as outfile:
        yaml.safe_dump(final_outdict, outfile, default_flow_style = False)
