from __future__ import print_function 
#for get_mol2_charge_report
import os,sys, glob, subprocess
import numpy as np
env = os.environ
DEP_PATH=env["SIMONAPATH"]+"/deposit/deposit-grid/tools"
sys.path.append(DEP_PATH)
tools_path = os.environ["SIMONAPATH"]+'/tools/python'
sys.path.append(tools_path)

from merge_mol2_ridft_charges import get_mol2_plain_charges
from molecule_data_collector import *
from mol22tachyon import mol22tachyon
from Deposit.DihedralParametrization.DihedralParametrize import dihedral_parametrize

def readXYZ():
    infile=open("molecule.xyz","r")
    lines=infile.readlines()
    infile.close()
    elements=[]
    coords=[]
    for line in lines[2:]:
        elements.append(line.split()[0])
        coords.append([float(line.split()[1]),float(line.split()[2]),float(line.split()[3])])
    return(coords,elements)



get_mullikens={{ wano["Analysis"]["Partial charges"]["Mulliken charges"] }}
get_esps={{ wano["Analysis"]["Partial charges"]["ESP fit"] }}
optimize={{ wano["Geometry optimization"]["enabled"] }}

if optimize:
    basename="optimized"
else:
    basename="input"


coords,elements=readXYZ()

if get_mullikens:
    mullikens=np.loadtxt("mulliken_charges.dat")

if get_esps:
    esps=np.loadtxt("esp_charges.dat")

if optimize:
    dihedral_parametrize.babel_convert_to_mol2("optimized.xyz","%s.mol2"%(basename))
else:
    dihedral_parametrize.babel_convert_to_mol2("molecule.xyz","%s.mol2"%(basename))


if get_mullikens:
    dihedral_parametrize.rewrite_partial_charges_in_mol2("%s.mol2"%(basename),mullikens)
    os.system("cp %s.mol2 %s_mullikens.mol2"%(basename, basename))

if get_esps:
    dihedral_parametrize.rewrite_partial_charges_in_mol2("%s.mol2"%(basename),esps)
    os.system("cp %s.mol2 %s_esps.mol2"%(basename, basename))

if not get_mullikens and not get_esps:
    dihedral_parametrize.rewrite_partial_charges_in_mol2("%s.mol2"%(basename),np.zeros((len(elements))))
    os.system("cp %s.mol2 %s_no_charges.mol2"%(basename, basename))

os.system("rm %s.mol2"%(basename))


zip_filename = "report.zip"

dc = MoleculeDataCollector()



for filename in glob.glob("*.mol2"):
    filebase = filename[:-5]
    charges_list,min_charge_tuple,max_charge_tuple,net_charge = get_mol2_plain_charges(filename)

    print ("Raytracing %s" %filename)
    outstring = mol22tachyon(filename,1280,1024)
    tach_file = open("render_file.tach",'w')
    print (outstring,file=tach_file)
    tach_file.close()
    subprocess.call(["tachyon","render_file.tach","-normalize","-aasamples","4","-o","out.tga"])
    subprocess.call(["convert","out.tga","-trim",filename[:-5]+".png"]) 

    os.system("cp %s.png %s_2dsketch.png"%(filebase,filebase))

    dc.add_molecule(
        Molecule(filebase.title(),
            [Calculation('Partial charge calculation',
                [('Net Charge', net_charge),
                    ('Largest positive charge', '(%s,%d,%g)' % max_charge_tuple,
                        '(%s,%d,%g)' % min_charge_tuple
                        )
                    ],
                [
                    Image(filebase+".png",
                        'Result of the partial charge calculation:\nRed colors: positive charge\nBlue colors: negative charge\nGray colors: big charge, check the value'),
                    Image(filebase+"_2dsketch.png",
                        'Sketch of molecule as input into DFT')
                    ],
                charges_list
                )]
            ),
        [filename, filebase+"_2dsketch.png", filebase+".png"]
        )

dc.export_zip(zip_filename)




