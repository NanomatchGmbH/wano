#!/usr/bin/env python

"""
Script that uses WaNo input to generate emission data
"""

from DFTBase.DaltonEngine import DaltonEngine
from DFTBase.Turbomole import Turbomole
from QPAnalysis.DFTBaseData import DFTBaseData
from Shredder.MoleculeSystem import TemporaryMol
from Shredder.Parsers.XYZParser import XYZParser
from os import environ
from zipfile import ZipFile

import numpy as np
import yaml



def get_ecp_atoms(elements):
    """Returns a list of atoms that need to be calculated with ECPs.

    @params elements: List of elements in molecule
    @returns List of element identifier strings
    """
    heavies = {"Rb", "Sr",  "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag",
               "Cd", "In", "Sn", "Sb", "Te",  "I", "Cs", "Ba", "La", "Ce", "Pr",
               "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",
               "Lu", "Hf", "Ta",  "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl",
               "Pb", "Bi", "Po"}
    checked = {"C", "H", "N", "O"}
    ecp_atoms = []
    for elem in elements:
        if elem in checked:
            continue
        else:
            if elem in heavies:
                ecp_atoms.append(elem)
            else:
                checked.add(elem)
    return ecp_atoms


def is_triplet(input_dict):
    """Checks whether singlet or triplet excitation were requested.

    @param input_dict: YAML dict snippet for linear response calculation.
    @returns boolean for options dictionary for Turbomole or Dalton engine.
    """
    ret = False
    if input_dict["Multiplicity"] == "Triplet":
        ret = True
    return ret


def get_atom_closest_to_center(coordinates):
    """Returns atom closest to the center of positions vector.

    @param coordinates: NumPy Nx3 matrix.
    @returns NumPy length 3 array CoP vector.
    """
    cop = np.average(coordinates, axis=0)  # center of positions
    i = 0  # atom indexer
    atom = 0  # index of closest atom
    smallest = None  # smallest distance found
    while i < coordinates.shape[0]:
        vec = coordinates[i] - cop
        length = np.linalg.norm(vec)
        if smallest:
            if length < smallest:
                smallest = length
                atom = i
        else:
            smallest = length
            atom = i
        i += 1
    return atom


def get_formatted_vector(vec):
    """Formats a vector so it is writeable with YAML.

    @param vec: NumPy length 3 array vector.
    @returns list of floats
    """
    return [float(vec[0]), float(vec[1]), float(vec[2])]


if __name__ == "__main__":
    with open("rendered_wano.yml", "r") as inyml:
        wano = yaml.safe_load(inyml)

    xyz = XYZParser()
    sys = xyz.parse_to_system(wano["Molecule"])
    mol = sys.molecule(0)

    exec_dir = "calculations"
    opts = {
        "threads": int(environ["UC_TOTAL_PROCESSORS"]),
        "charge": 0
    }

    # If wanted, a geometry optimization of the input molecule is executed
    if wano["Optimize Geometry"] is True:
        inputs = wano["Geometry Optimization Options"]
        options = opts.copy()
        options["optimize"] = True
        options["basis"] = inputs["Basis"]
        options["functional"] = inputs["Functional"]
        dfte = Turbomole("%s/geometry_optimization" % exec_dir, options)
        dfte.write_input_for_molecules([mol], [])
        dfte.run()
        lp = dfte.get_output_parser()
        coords, elems = lp.get_geometry()
        # Write optimized molecule
        lines = ["%d\n" % len(elems), "Optimized with QuantumPatch.\n"]
        i = 0
        line_template = "%s   %.6f   %.6f   %.6f\n"
        while i < len(elems):
            x = coords[i][0]
            y = coords[i][1]
            z = coords[i][2]
            lines.append(line_template % (elems[i], x, y, z))
            i += 1
        with open("optimized_molecule.xyz", "w") as outfile:
            for line in lines:
                outfile.write(line)
    else:
        coords = mol.coordinates
        elems = mol.elements
    mol = TemporaryMol(coords, elems, mol.moltype)
    # Create atomic basis if requested
    user_dict = {}
    is_orientation_analysis = False
    if wano["Orientation Analysis Output"] is True:
        is_orientation_analysis = True
        at0 = int(wano["Center Atom"])
        at1 = int(wano["Internal Atomic Basis"]["Atom 1"])
        at2 = int(wano["Internal Atomic Basis"]["Atom 2"])
        at3 = int(wano["Internal Atomic Basis"]["Atom 3"])
        user_dict["atoms"] = [at0, at1, at2, at3]
    elif wano["Automatic Center Atom"] is False:
        at0 = int(wano["Center Atom"])
        user_dict["atoms"] = [at0]
    else:
        at0 = get_atom_closest_to_center(mol.coordinates)
        user_dict["atoms"] = [at0]

    if wano["Optimize Geometry"]:
        molname = "optimized_molecule.xyz"
    else:
        molname = "molecule.xyz"
    detailed_yml = dict()
    # Execute excited state calculations
    if wano["Emission Type"] == "Phosphorescence":
        inputs = wano["Phosphorescence Calculation Options"]
        options = opts.copy()
        options["quad_resp"] = True
        options["roots"] = inputs["Excitations"]
        options["basis"] = inputs["Basis"]
        options["functional"] = inputs["Functional"]
        options["ecp_atoms"] = get_ecp_atoms(mol.elements)
        if len(options["ecp_atoms"]) > 0:
            options["ecp_basis"] = "ecp-sdd-dz"
        dfte = DaltonEngine("%s/quadratic_response" % exec_dir, options)
        dfte.write_input_generic(coords, elems, [])
        dfte.run()
        lp = dfte.get_output_parser()
        dftbd = DFTBaseData(user_dict, lp, mol, xyzfile=molname)
        dftbd.create_static_dipole_vmdstate()
        dftbd.create_second_order_moment_vmdstate(0)
        dftbd.write_vmd_state_file("dipole_and_phosphorescence")
        if is_orientation_analysis:
            orientation_yml = dict()
            orientation_yml["0"] = dftbd.orientation_analysis_static_dipole_input()
            phos_vecs = dftbd.orientation_analysis_quadratic_response_input()
            i = 0
            while i < 3:
                orientation_yml["%d" % (i + 1)] = phos_vecs[i].copy()
                i += 1
            with open("orientation_analysis.yml", "w") as outfile:
                yaml.safe_dump(orientation_yml, outfile)
        # Creating standard YAML output
        # Phosphorescence moments
        som_norms = lp.get_second_order_moment_norms()
        som = lp.second_order_moments
        component = ["x", "y", "z"]
        tmp = dict()
        i = 1  # Excitation index
        while i <= lp.second_order_moments.shape[0]:
            tmp[i] = dict()
            k = 0  # ZFS component index
            while k < 3:
                tmp[i][component[k]] = dict()
                tmp[i][component[k]]["Norm"] = float(som_norms[i - 1, k])
                tmp[i][component[k]]["Vector"] = get_formatted_vector(
                    som[i - 1, k])
                k += 1
            i += 1
        detailed_yml["Second Order Transition Moments"] = tmp.copy()
    elif wano["Emission Type"] == "Fluorescence":
        inputs = wano["Fluorescence Calculation Options"]
        options = opts.copy()
        options["lin_resp"] = True
        options["triplet"] = is_triplet(inputs)
        options["roots"] = inputs["Excitations"]
        options["basis"] = inputs["Basis"]
        options["functional"] = inputs["Functional"]
        dfte = Turbomole("%s/linear_response" % exec_dir, options)
        dfte.write_input_generic(coords, elems, [])
        dfte.run()
        lp = dfte.get_output_parser()
        dftbd = DFTBaseData(user_dict, lp, mol, xyzfile=molname)
        dftbd.create_static_dipole_vmdstate()
        dftbd.create_first_order_moment_vmdstate(0)
        dftbd.write_vmd_state_file("dipole_and_fluorescence")
        if is_orientation_analysis:  # Orientation analysis output generation
            orientation_yml = dict()
            orientation_yml["0"] = dftbd.orientation_analysis_static_dipole_input()
            orientation_yml["1"] = dftbd.orientation_analysis_linear_response_input()
            with open("orientation_analysis.yml", "w") as outfile:
                yaml.safe_dump(orientation_yml, outfile)
        # Creating standard YAML output
        # Fluorescence moments
        fom_norms = lp.get_first_order_moment_norms()
        tmp = dict()
        i = 1  # Excitation index
        while i <= lp.first_order_moments.shape[0]:
            tmp[i] = dict()
            tmp[i]["Norm"] = float(fom_norms[i - 1])
            tmp[i]["Vector"] = get_formatted_vector(lp.first_order_moments[i - 1])
            tmp[i]["Excitation Energy"] = float(lp.excitation_energies[i - 1])
            i += 1
        detailed_yml["First Order Transition Moments"] = tmp.copy()
    # Dipole vector
    detailed_yml["Static Dipole"] = dict()
    detailed_yml["Static Dipole"][0] = dict()
    detailed_yml["Static Dipole"][0]["Norm"] = float(lp.get_dipole_norm())
    detailed_yml["Static Dipole"][0]["Vector"] = get_formatted_vector(lp.dipole)
    with open("detailed.yml", "w") as outfile:
        yaml.safe_dump(detailed_yml, outfile)
    with ZipFile("report.zip", "w") as archive:
        archive.write("detailed.yml")
        if wano["Optimize Geometry"] is True:
            archive.write("optimized_molecule.xyz")
        if is_orientation_analysis:
            archive.write("orientation_analysis.yml")
        if wano["Emission Type"] == "Fluorescence":
            archive.write("vmd_output/dipole_and_fluorescence.tcl")
        elif wano["Emission Type"] == "Phosphorescence":
            archive.write("vmd_output/dipole_and_phosphorescence.tcl")
        archive.write("vmd_output/%s" % molname)

