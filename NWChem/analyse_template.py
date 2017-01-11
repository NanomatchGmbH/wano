import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from nwchem import GetMullikens
from nwchem import GetESPs
from nwchem import GetEnergies
from nwchem import getXYZ

def GetMullikens(elements):
    mullikens=[]
    infile=open("nwchem.out","r")
    read=False
    for line in infile:
        linesplit=line.split()
        if len(linesplit)>3:
            if read:
                mullikens.append(float(line.split()[3]))
            if "gross population on atoms" in line:
                read=True
        if read and len(linesplit)==0 and len(mullikens)>0:
            break
    infile.close()
    mullikens=np.array(mullikens)
    #noElectrons={"H":1.0,"C":4.0,"O":6.0,"N":5.0,"Mg":2.0,"F":7.0,"Cl":7.0,"Br":7.0,"S":6.0,"P":5.0,"Cu":0.0,"Zn":0.0}
    noElectrons={"H":1.0,"C":6.0,"O":8.0,"N":7.0,"Al":0.0}
    idx=0
    for element in elements:
        mullikens[idx]-=noElectrons[element]
        idx+=1
    return(mullikens)

def GetESPs():
    esps=[]
    infile=open("nwchem.out","r")
    read=False
    idx=0
    for line in infile:
        linesplit=line.split()
        if len(linesplit)>1 and read:
                esps.append(float(line.split()[5]))
                idx+=1
        if len(linesplit)>0:
            if line.split()[0]=="ESP":
                read=True
        if read and len(linesplit)==1 and len(esps)>0:
            break
    infile.close()
    esps=np.array(esps)
    return(esps)

def GetEnergies():
    HToEV=27.21138505
    HOMO=0.0
    LUMO=0.0
    Total=0.0
    infile=open("nwchem.out","r")
    idx=0
    found_LUMO=False
    for line in infile:
        linesplit=line.split()
        if len(linesplit)>3:
            if linesplit[0]=="Total" and linesplit[1]=="DFT" and linesplit[2]=="energy":
                Total_str=linesplit[4]
                if "D" in Total_str:
                    Total=float(Total_str.split("D")[0])*10**float(Total_str.split("D")[1])*HToEV
                else:
                    Total=float(Total_str)*HToEV
            if linesplit[0]=="Vector":
                if "2.0" in linesplit[2]:
                    if linesplit[3]=="E=":
                        HOMO_str=linesplit[4]
                    else:
                        HOMO_str=linesplit[3].split("=")[1]
                    #print HOMO_str
                    if "D" in HOMO_str:
                        #print "HOMO string contains D"
                        HOMO=float(HOMO_str.split("D")[0])*10**float(HOMO_str.split("D")[1])*HToEV
                    else:
                        #print "no D in HOMO"
                        HOMO=float(HOMO_str)*HToEV
                    found_LUMO=False
                if "0.0" in linesplit[2] and not found_LUMO:
                    if linesplit[3]=="E=":
                        LUMO_str=linesplit[4]
                    else:
                        LUMO_str=linesplit[3].split("=")[1]
                    if "D" in LUMO_str:
                        #print "LUMO string contains D"
                        LUMO=float(LUMO_str.split("D")[0])*10**float(LUMO_str.split("D")[1])*HToEV
                        found_LUMO=True
                    else:
                        #print "no D in LUMO"
                        LUMO=float(LUMO_str)*HToEV
                        found_LUMO=True
    infile.close()
    return [HOMO,LUMO,Total]


def getXYZ():
    infile=open("nwchem.out","r")
    xyz=[]
    read1=False
    read2=False
    for line in infile:
        if len(line.split())!=0:
            if read1==True and "1" in line.split()[0]:
                read2=True
                read1=False
            if line.split()[0]=="Geometry":
                read1=True
                xyz=[]
        if read2==True:
            if len(line.split())==0:
                read2=False
            elif len(line.split())==6:
                xyz.append([float(line.split()[3]),float(line.split()[4]),float(line.split()[5]),line.split()[1]])
    infile.close()
    return xyz

def writeXYZ(xyz):
    infile=open("optimized.xyz","w")
    infile.write("%i\n\n"%len(xyz))
    for coordinate in xyz:
        infile.write("%s %f %f %f\n"%(coordinate[3],coordinate[0],coordinate[1],coordinate[2]))
    infile.close()
    return

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

basis="{{ wano["Simulation parameters"]["Basis-set"] }}"
functional="{{ wano["Simulation parameters"]["Functional"] }}"

get_mullikens={{ wano["Analysis"]["Partial charges"]["Mulliken charges"] }}
get_esps={{ wano["Analysis"]["Partial charges"]["ESP fit"] }}

optimize={{ wano["Geometry optimization"]["enabled"] }}

coords,elements=readXYZ()


if get_mullikens:
    mullikens=GetMullikens(elements)
    np.savetxt("mulliken_charges.dat",mullikens)
    print(mullikens)

if get_esps:
    esps=GetESPs()
    np.savetxt("esp_charges.dat",esps)
    print(esps)

energies=GetEnergies()
print(energies)

if optimize:
    new_geometry=getXYZ()
    writeXYZ(new_geometry)
    print(new_geometry)






#outfile=open("report.tex","w")
#outfile.write("")
