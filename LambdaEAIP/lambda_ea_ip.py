#!/usr/bin/env python3

"""
Script that uses WaNo input to calculate Lambdas, EAs, and IPs.
"""

from MolecularTools.LambdaEAIP import LambdaEAIP

from os import environ
from os.path import exists
from zipfile import ZipFile


if __name__ == "__main__":
    threads = int(environ["UC_TOTAL_PROCESSORS"])
    memory = int(environ["UC_MEMORY_PER_NODE"])
    args = ["Geometry Optimization Options.Threads=%d" % threads,
            "Geometry Optimization Options.Memory=%d" % memory,
            "Single Point Options.Threads=%d" % threads,
            "Single Point Options.Memory=%d" % memory]
    # Write report file
    tool = LambdaEAIP(args, "rendered_wano.yml")
    tool.run()
    with ZipFile("report.zip", "w") as archive:
        archive.write("detailed.yml")
        charges = [0, 1, -1]
        for q in charges:
            molname = "optimized_molecule_charge%d.xyz" % q
            if exists(molname):
                archive.write(molname)
