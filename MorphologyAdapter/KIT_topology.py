import numpy as np
import argparse
import os

parser=argparse.ArgumentParser()
parser.add_argument("Filename",help="Filename to load")
parser.add_argument("Out_path",help="Output path")
args=parser.parse_args()
filename=args.Filename
outpath=args.Out_path

if(outpath[-1]!='/'):
	outpath+='/'

SITE_TYPE_ELECTRODE_N=-1
SITE_TYPE_ELECTRODE_P=-2
SITE_TYPE_ALL=4
SITE_TYPE_P_DOPANT=102

morphology_data = np.load(filename)

xyz_coords=morphology_data["arr_0"]
neighbours=morphology_data["arr_2"].astype(np.int64)
transfer_integrals=morphology_data["arr_5"]
pair_separations=morphology_data["arr_6"] #As a single number r
pair_differences=morphology_data["arr_3"] #As componenets in part,nbour,component

HOMO_pure=-5.5
LUMO_pure=-2.4
lambda_hole=0.158
lambda_elec=0.109
sigma_hole=0.087
sigma_elec=0.075
absorption=1.0

N_particles=len(xyz_coords)
print "N_particles=",N_particles
lx=0
ly=0
lz=0

for i in xrange(N_particles):
    if(abs(xyz_coords[i,0])>lx):
        lx=abs(xyz_coords[i,0])
    if(abs(xyz_coords[i,1])>ly):
        ly=abs(xyz_coords[i,1])
    if(abs(xyz_coords[i,2])>lz):
        lz=abs(xyz_coords[i,2])

for i in xrange(N_particles):
    xyz_coords[i,0]=xyz_coords[i,0]+lx
    xyz_coords[i,1]=xyz_coords[i,1]+ly
    xyz_coords[i,2]=xyz_coords[i,2]+lz
lx=lx*2
ly=ly*2
lz=lz*2
print lx,ly,lz

N_neighbours=np.zeros(N_particles,dtype=np.int64)
neighbours=np.reshape(neighbours,(N_particles,-1))
print "Coords=",xyz_coords.shape
print "Neighbours=",neighbours.shape
print "Seps=",pair_separations.shape
print "Integrals=",transfer_integrals.shape
print "Differences=",pair_differences.shape
for i in xrange(N_particles):
    N_neighbours[i]=len(neighbours[i])

#So I'm pretty sure that KIT have given me the transfer integral in Joules^2
transfer_integrals=transfer_integrals/(1.602e-19*1.602e-19)

#Read in the locations of the dopants
dopants_sites=[]
#with open("alphaNPD_F4TCNQ_dopant_data_10",'r') as dopant_file:
#    for line in dopant_file:
#        fields=line.split()
#        #print fields
#        dopants_sites.append(float(fields[0]))
#        dopants_sites.append(float(fields[1]))
#    dopant_file.close

with open(outpath+"geometry.dat",'w') as f_geo:
    for i in xrange(N_particles):
        if(xyz_coords[i,2]<0.05*lz):
            site_type=SITE_TYPE_ELECTRODE_N
        elif(xyz_coords[i,2]>0.95*lz):
            site_type=SITE_TYPE_ELECTRODE_P
        else:
            site_type=SITE_TYPE_ALL
        if(i in dopants_sites):
            site_type=SITE_TYPE_P_DOPANT
        f_geo.write("%i %i %g %g %g\n"%(site_type,N_neighbours[i],xyz_coords[i,0],xyz_coords[i,1],xyz_coords[i,2]))
    f_geo.close

with open(outpath+"positions",'w') as f_pos:
    for i in xrange(N_particles):
        f_pos.write("%g %g %g\n"%(xyz_coords[i,0],xyz_coords[i,1],xyz_coords[i,2]))
    f_pos.close

with open(outpath+"neighbours.dat",'w') as f_neigh:
    for i in xrange(N_particles):
        for j in xrange(N_neighbours[i]):
            f_neigh.write("%g "%neighbours[i,j])
        f_neigh.write("\n")
        for j in xrange(N_neighbours[i]):
            f_neigh.write("%g "%pair_separations[i][j])
        f_neigh.write("\n")
    f_neigh.close

#Calculate Gaussian disorder for the HOMO levels
HOMOs=np.random.normal(HOMO_pure,sigma_elec,N_particles)
LUMOs=np.random.normal(LUMO_pure,sigma_hole,N_particles)

with open(outpath+"energetics.dat",'w') as f_energy:
    for i in xrange(N_particles):
        f_energy.write("%g %g %g\n"%(HOMOs[i],LUMOs[i],absorption))
        for j in xrange(N_neighbours[i]):
            f_energy.write("%e "%transfer_integrals[i,j])
        f_energy.write("\n")
    f_energy.close

#Precalculate the HOMO LUMO differences in a 2D array so its in [site][neighbour] form
E_hole_pairs=[]
E_elec_pairs=[]
for i in xrange(N_particles):
    E_hole_pairs.append([])
    E_elec_pairs.append([])
    for j in xrange(N_neighbours[i]):
        E_hole_pairs[i].append(HOMOs[neighbours[i,j]]-HOMOs[i])
        E_elec_pairs[i].append(LUMOs[neighbours[i,j]]-LUMOs[i])
delta_E_hole_pairs=np.array(E_hole_pairs)
delta_E_elec_pairs=np.array(E_elec_pairs)

with open(outpath+"pair_energies.dat",'w') as f_pairs:
    for i in xrange(N_particles):
        for j in xrange(N_neighbours[i]):
            f_pairs.write("%e %e "%(lambda_hole,lambda_elec))
        f_pairs.write("\n")
        for j in xrange(N_neighbours[i]):
            f_pairs.write("%e %e "%(delta_E_hole_pairs[i,j],delta_E_elec_pairs[i,j]))
        f_pairs.write("\n")
    f_pairs.close

with open(outpath+'coupling_data','w') as coupling:
    coupling.write("#dx dy dz J^2\n")
    for i in xrange(N_particles):
        for j in xrange(N_neighbours[i]):
            coupling.write("%g "%pair_differences[i,j,0])
            coupling.write("%g "%pair_differences[i,j,1])
            coupling.write("%g "%pair_differences[i,j,2])
            coupling.write("%g "%pair_separations[i,j])
            coupling.write("%g "%transfer_integrals[i,j])
            coupling.write("\n")
    coupling.close
