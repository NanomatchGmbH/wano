#!/usr/bin/env python
import yaml
from pprint import pprint

import jinja2


if __name__ == '__main__':

    with open("rendered_wano.yml","r") as input_wano:
        wano = yaml.safe_load(input_wano)

    current_start = 0
    current_end = 0
    material_info = []
    for element in wano["TABS"]["Layer Setup"]["Layers"]:
        mi = {}
        current_end = current_end + element["Thickness"]
        element["start"] = current_start
        element["end"] = current_end
        kmc_template_file = element["KMC Parameters"]
        with open(kmc_template_file,"r") as input_kmc:
            element["kmc"] = yaml.safe_load(input_kmc)
        current_start = current_end

    loader = jinja2.FileSystemLoader( searchpath="./")
    env = jinja2.Environment( loader=loader)
    template = env.get_template( "input.in")
    print(template.render(wano=wano))
