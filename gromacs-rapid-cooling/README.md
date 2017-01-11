# Name

This module simulates cooling down of a liquid from a high temperature `T1` to a final temperature `T2` at a constant cooling rate `R` using molecular dynamics. 

The computational protocol involves following steps:

1. Energy minimization of the initial structure
2. NVT equilibration at `T1` for 10 ps
3. NPT equilibration for `tau1` ns at `T1`
4. NPT cooling from `T1` to `T2` maintaining the cooling rate `R`
5. NPT equilibration for `tau2` ns at `T2` to collect data

where

* NVT = Nose-Hoover thermostate 
* NPT = Parrinello-Rahman barostate + Nose-Hoover thermostate

All NPT simulation apply a constant pressure `P0`.

# Parameter

## Initial configuration and MD-Topology

* initial configuration is a GROMACS `.gro` file
* single molecule GROMACS topology file `molecule.itp` contains all force-field parameters
* system GROMACS topology `.top` file (should include the molecular force filed as `#include "molecule.itp"`)
* before starting the simulation check that the number of molecules in `.gro` and `.top` files do match with each other

## Simulation parameters

* Initial Temperature `T1` [K]
* Equilibration time at initial temperature `tau1` [ns]
* Cooling rate `R` [K/ns]
* Final Temperature `T2` [K]
* Equilibration time at final temperature `tau2` [ns]
* Pressure `P0` [bar]

## Numerical parameters

* Timestep [ps] for MD intergation
* Output frequency for coords, velocities etc [ps]
* Output frequency for energies [ps]
* Random seed: the initial random velocities of atoms in the step 2 will be generated using this values as the seed.


# Expected Output 

* Atomic coordinates after the energy minimization: `01-minimization.gro`
* Atomic coordinates after the NVT step: `02-NVT.gro`
* Atomic coordinates after the NPT equilibration step at `T1`: `03-NPT.gro`
* Atomic coordinates after the NPT cooling step from `T1` to `T2`: `04-cooling.gro`
* Atomic coordinates after the NPT equilibration step at `T2`: `05-NPT.gro`
* Averaged values for the NPT equilibration step at `T2`: `AVERAGED_DATA.txt`

# Ausführungsbeispiel 

Simulation of 50 α-NPD molecules.

* GRO file: 'alpha-NPD.gro'
* ITP file: 'alpha-NPD.itp'
* TOP file: 'alpha-NPD.top'
* Initial Temperature [K]: 800.0
* Equilibration time at initial temperature [ns]: 0.2
* Cooling rate [K/ns]: 500.0
* Final Temperature [K]: 300.0
* Equilibration time at final temperature [ns]: 0.2
* Pressure [bar]: 1.0
* Timestep [ps]: 0.001
* Output frequency for coords, velocities etc [ps]: 5.0
* Output frequency for energies [ps]: 2.0
* Random seed: 1234

Expected walltime at 8 CPUs is 2 hours. Expected averaged values:

    Energy                      Average   Err.Est.       RMSD  Tot-Drift
    -------------------------------------------------------------------------------
    Temperature                 299.992     0.0045    5.33828 -0.00348105  (K)
    Pressure                    1.45002       0.46    1094.86   0.562582  (bar)
    Density                     1109.68       0.16    5.63462  -0.541441  (kg/m^3)


# Lizenz und Bezugsort 

LICENSE AGREEMENT

IMPORTANT: This license Agreement is a legal agreement between you, the end
user (either an individual or an entity), and the Karlsruhe Institute of
Technology. By copying, running, accessing or installing this software you
accept the following:

SOFTWARE LICENSE

GRANT OF LICENSE. Use of this software is prohibited for anyone who is not a
member of the AG Wenzel at the Institute of Nanotechnology at KIT. Members of
the AG Wenzel may only use this software on projects of KIT explicitly
authorized by the group leader. You may not copy, install, distribute or use
this software without explicit written permission by KIT.

OWNERSHIP. This software is owned by KIT and ownership is protected by the
copyright laws of the Federal Republic of Germany and by international treaty
provisions. Upon expiration or termination of this Agreement, you shall
promptly return all copies of the Software and accompanying written materials
to the Karlsruhe Institute of Technology. 

MODIFICATIONS AND DERIVATIVE WORKS. You may not modify the software or use it
to create derivative works. You may not distribute such modified or derivative
software to others outside of your site without written permission. 

ASSIGNMENT RESTRICTIONS. You shall not use the Software (or any part thereof)
in connection with the provision of consultancy, modeling or other services,
whether for value or otherwise, on behalf of any third party who does not hold
a current valid Software License Agreement. You shall not use the Software to
write other software that duplicates the functionality of the Software. You
shall not rent, lease, or otherwise sublet the Software or any part thereof. 

LIMITED WARRANTY. LICENSEE acknowledges that LICENSORS make no warranty,
expressed or implied, that the program will function without error, or in any
particular hardware environment, or so as to generate any particular function
or result, and further excluding any other warranty, as to the condition of the
program, its merchantability, or its fitness for a particular purpose.
LICENSORS shall not be liable for any direct, consequential, or other damages
suffered by the LICENSEE or any others as a result of their use of the program,
whether or not the same could have been foreseen by LICENSORS prior to granting
this License. In no event shall LICENSORS liability for any breach of this
agreement exceed the fee paid for the license. 

KARLSRUHE INSTITUTE OF TECHNOLOGY'S LIABILITY. In no event shall the Karlsruhe
Institute of Technology be liable for any indirect, special, or consequential
damages, such as, but not limited to, loss of anticipated profits or other
economic loss in connection with or arising out of the use of the software by
you or the services provided for in this Agreement, even if the Karlsruhe
Institute of Technology has been advised of the possibility of such damages.
The Karlsruhe Institute of Technology's entire liability and your exclusive
remedy shall be, at the Karlsruhe Institute of Technology's discretion, to
return the Software and proof of purchase to the Karlsruhe Institute of
Technology for either (a) return of any license fee, or (b) correction or
replacement of Software that does not meet the terms of this limited warranty. 

NO OTHER WARRANTIES. The Karlsruhe Institute of Technology disclaims other
implied warranties, including, but not limited to, implied warranties of
merchantability or fitness for any purpose, and implied warranties arising by
usage of trade, course of dealing, or course of performance. Some states do not
allow the limitation of the duration or liability of implied warranties, so the
above restrictions might not apply to you. 

LICENSE FEE. All individuals or organizations wishing to license this software
shall contact: wolfgang.wenzel@kit.edu and request a quote for a license.

This license explicitly does not cover the external and linked software.




# Minimoda 

Für die WaNos ist das fast immer:
[ Box mit Input File (coord) ] -> [ Name des Programms (TM) ] -> [ 
Rohoutput (TM.out) ] -> [ postprocessing output (Partialladungen) ]

