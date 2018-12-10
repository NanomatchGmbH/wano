#!/usr/bin/env python

"""
Script that uses WaNo input to generate emission data
"""

from DFTBase.Turbomole import Turbomole
from Shredder.MoleculeSystem import TemporaryMol
from Shredder.Parsers.XYZParser import XYZParser
from os import environ
from zipfile import ZipFile

import numpy as np
import yaml


if __name__ == "__main__":

    exec_dir = "calculations"
    opts = {
        "threads": int(environ["UC_TOTAL_PROCESSORS"]),
    }
    # Indirection to check if a functional is a hybrid
    hybrids = ["b3-lyp", "b2-plyp"]


    # Write report file
    with ZipFile("report.zip", "w") as archive:
        archive.write("detailed.yml")
