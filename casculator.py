#/usr/bin/python
'''
CASculator Version 1.01
Results Visualizer for ORCA CASSCF Results
Doug Crandell-Indiana University-Bloomington, IN 47401
8/2/2014
'''

import sys, os, re
import argparse
from decimal import *

def main(args):
    data = open_file(args.calcid)
    LCO = get_LCO(data)
    orb_dict = create_OrbDict(LCO)
    resolution = 40
    orb_list = []
    if args.resolution:
        resolution = 80
    if not args.active and not args.d_orbitals and not args.atom and not args.range and not args.spin and not args.charge and args.plot == None:
        get_total_orbs(data)
        start, end, nel, norb = get_active(data)
        print_composition(get_d_orbitals(LCO, args.threshold))
    if args.active:
        get_total_orbs(data)
        start, end, nel, norb = get_active(data)
        orb_list += list(range(int(start),int(end)+1))
        for orbital in range(int(start),int(end)+1):
                print "Orbital %s: " %str(orbital) + "Occupation #: " + orb_dict[str(orbital)][1]
    if args.d_orbitals:
        composition = get_d_orbitals(LCO,args.threshold)
	print_composition(composition)
	for keys in composition.keys():
	    orb_list.append(keys)
    if args.atom and args.orb_type:
        composition = get_spec_orb(LCO,args.atom,args.orb_type,args.threshold)
	print_composition(composition)
	for keys in composition.keys():
	    orb_list.append(keys)
    if args.atom and not args.orb_type:
        print "Specify the type of orbital for the particular atom"
    if not args.atom and args.orb_type:
        print "Specify the particular atom for the type of orbital"
    if args.spin:
        get_ChargeSpin(args.calcid)
    if args.charge:
        get_ChargeSpin(args.calcid)
    if args.range:
        orb_list += list(range(int(args.range[0]),args.range[1]+1))
        args.plot = orb_list
        for orbital in range(args.range[0],args.range[1]+1):
            print "Orbital %s: " %str(orbital) + "Occupation #: " + orb_dict[str(orbital)][1]              
    if args.plot != None:
        if orb_list == []:
            orb_list = args.plot
        orbital_plot(args.calcid,orb_list,resolution)

def get_active(data):
    '''Determines the orbitals making up the active space'''
    for line in data.split('\n'):
        if line.strip().startswith("Number of active electrons"):
            nel = line.split('...')[1].strip()
        if line.strip().startswith("Number of active orbitals"):
            norb = line.split('...')[1].strip()
        if line.strip().startswith("Active") and not line.strip().startswith("Active   Orbitals") and not line.strip().startswith("Active property"): #Find the correct line
            start_active = line.split('Active')[1].strip().split('-')[0].strip() #Get first orbital of the active space
            end_active = line.split('Active')[1].strip().split('-')[1].strip().split(' ')[0] #Get last active space orbital
            active = "Active Space: " + start_active +'-' + end_active #Store active space as string
    print active
    return start_active, end_active, nel, norb #Return first and last orbitals along with number of active electrons/orbitals

def get_total_orbs(data):
    '''Gets the total number of orbitals'''
    for line in data.split('\n'):
        if line.strip().startswith("External") and not line.strip().startswith("External Orbitals"): #Get the corret line
            orbnumber = line.split('-')[1].strip().split(' ')[0]
    print "Number of orbitals: %s" %orbnumber

def get_LCO(data):
    line_number = 0
    LCO = []
    for line in data.split('\n'):
        if line.startswith("LOEWDIN ORBITAL-COMPOSITIONS"): #Identify start of orbital composition section
            start_LCO = line_number
        if line.strip().startswith("ORCA POPULATION ANALYSIS"): #We have reached end of orbital composition
            end_LCO = line_number
        line_number += 1
    lco_list = data.split('\n')[start_LCO+3:end_LCO-1]
    count = 0
    for line in lco_list:
        if not line.startswith('WARNING'):
            LCO.append(line)
    return LCO

def get_SPE(file):
    data = open_file(file)
    for line in data.split('\n'):
        if line.strip().startswith("FINAL SINGLE POINT ENERGY"):
            spe = '-' + line.split('-')[1]
    return spe

def get_ChargeSpin(file):
    data = open_file(file)
    line_number = 0
    for line in data.split('\n'):
        if line.startswith("MULLIKEN ATOMIC CHARGES AND SPIN DENSITIES"):
            start_mul = line_number
        if line.startswith("Sum of atomic charges"):
            end_mul = line_number
        if line.startswith("LOEWDIN ATOMIC CHARGES AND SPIN DENSITIES"):
            start_loew = line_number
        if line.startswith("LOEWDIN REDUCED ORBITAL CHARGES AND SPIN DENSITIES"):
            end_loew = line_number
        line_number += 1
    mulliken = data.split('\n')[start_mul+2:end_mul]
    loewdin = data.split('\n')[start_loew+2:end_loew-2]
    try:
        if args.spin:
            if args.spin == 'Loewdin' or args.spin == 'loewdin' or args.spin == 'lowdin' or args.spin == 'Lowdin' or args.spin == 'l' or args.spin == 'L':
                spin_list = loewdin
            else:
                spin_list = mulliken
            print "Spin Densities:\n"
            for item in spin_list:
                item = item.split(':')
                atom = item[0]
                atom = filter(None,atom.split(' '))
                chargespin = filter(None,item[1].split(' '))
                string = "%s%s: " %(atom[1],atom[0])
                print string + chargespin[1]
    except NameError:
        pass
    try:
        if args.charge:
            if args.charge == 'Loewdin' or args.charge == 'loewdin' or args.charge == 'lowdin' or args.charge == 'Lowdin' or args.charge == 'l' or args.charge == 'L':
                charge_list = loewdin
            else:
                charge_list = mulliken
            print "Atomic Charges:\n"
            for item in charge_list:
                item = item.split(':')
                atom = item[0]
                atom = filter(None,atom.split(' '))
                chargespin = filter(None,item[1].split(' '))
                string = "%s%s: " %(atom[1],atom[0])
    except NameError:
        pass
    return mulliken, loewdin
            
def create_OrbDict(LCO):
    '''Create dictionary object where orbital numbers are the keys and the orbital energies and occupations are the values'''
    orb_dict = {}
    #Get first 6 orbitals/energies/occupations
    orbitals = filter(None, LCO[0].strip().split(' '))
    energies= filter(None, LCO[1].strip().split(' '))
    occupations = filter(None, LCO[2].strip().split(' '))
    for num in range(0, len(orbitals)):
        orb_dict[orbitals[num]] = [energies[num],occupations[num]] #Add to dictionary
    line_number = 0
    for line in LCO: #Iterate through rest of the orbitals
        if not line.strip():
            if line_number+1 < len(LCO):
                orbitals = filter(None, LCO[line_number+1].strip().split(' '))
                energies = filter(None, LCO[line_number+2].strip().split(' '))
                occupations = filter(None, LCO[line_number+3].strip().split(' '))
                for num in range(0, len(orbitals)):
                    orb_dict[orbitals[num]] = [energies[num],occupations[num]] #Add to dictionary
        line_number += 1
    return orb_dict

def get_d_orbitals(LCO,threshold):
    tm = ['Sc','V','Cr','Mn','Fe','Co','Ni','Cu','Zn',
          'Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd',
          'Lu','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg']
    sorbs = ['s']
    porbs = ['px','py','pz']
    dorbs = ['dxy','dxz','dyz','dx2y2','dz2']
    line_number = 0
    line_tracker = []
    comp_dict = {}
    for line in LCO:
        if line.strip().startswith('--------'):
            line_tracker.append(line_number)
        select = filter(None,re.findall('[A-Z][^A-Z]*', line))
        if select != []:
            length = len(filter(None,select[0].split(' ')))
            element = select[0].split(' ')[0]
            orbital = select[0].split(' ')[1]
            if element in tm and orbital in dorbs:
                for num in range(2,length):
                    percentage = Decimal(filter(None,select[0].split(' '))[num])
                    if percentage >= threshold:
                        orb_num = filter(None, LCO[line_tracker[-1]-3].strip().split(' '))[num-2]
                        if orb_num in comp_dict:
                            comp_dict[orb_num].append([orbital, str(percentage)])
                        else:
                            comp_dict[orb_num] = []
                            comp_dict[orb_num].append([orbital, str(percentage)])
        line_number += 1
    return comp_dict

def get_spec_orb(LCO, el, orb_type, threshold):
    line_number = 0
    line_tracker = []
    comp_dict = {}
    match = re.match("([a-zA-Z]+)([0-9]+)",el,re.I)
    elem = match.group(1)
    atom_number = int(match.group(2))
    for line in LCO:
        if line.strip().startswith('--------'):
            line_tracker.append(line_number)
        select = filter(None,re.findall('[A-Z][^A-Z]*', line))
        if select != []:
            length = len(filter(None,select[0].split(' ')))
	    element = select[0].split(' ')[0]
	    if len(element) == 1:
                orbital = select[0].split(' ')[2]
            else:
                orbital = select[0].split(' ')[1]
            atom_num = 1
	    atom_num = int(filter(None,re.findall('[0-9]+',line))[0])
	    if element == elem and atom_num == atom_number and orbital == orb_type:
		for num in range(2,length):
                    percentage = Decimal(filter(None,select[0].split(' '))[num])
                    if percentage >= threshold:
                        orb_num = filter(None, LCO[line_tracker[-1]-3].strip().split(' '))[num-2]
                        if orb_num in comp_dict:
                            comp_dict[orb_num].append([orbital, str(percentage)])
                        else:
                            comp_dict[orb_num] = []
                            comp_dict[orb_num].append([orbital, str(percentage)])
        line_number += 1
    return comp_dict

def orbital_plot(calc_id,orb_list,resolution=40):
    try:
        import pexpect
    except ImportError:
        pass
    child = pexpect.spawn('/N/dc2/scratch/baikgrp/orca_3_0_0_linux_x86-64/orca_plot "%s.gbw" -i' %calc_id)
    child.expect('Enter a number: ')
    child.sendline('5')
    child.expect('Enter Format: ')
    child.sendline('7')
    if resolution == 80:
        child.expect('Enter a number: ')
        child.sendline('4')
        child.expect('Enter NGRID: ')
        child.sendline('80')
    for orbital in orb_list:
	child.expect('Enter a number: ')
        child.sendline('2')
        child.expect('Enter MO: ')
        child.sendline(str(orbital))
        child.expect('Enter a number: ')
        child.sendline('10')
    child.expect('Enter a number: ')
    child.sendline('11')

def print_composition(comp):
    ordered = {}
    for k in comp.iterkeys():
        ordered[int(k)] = comp[k]
    ordered = sorted(ordered, key=lambda key: key)
    for orbital in ordered:
        print "Orbital %s" %orbital +":"
        for num in range(len(comp[str(orbital)])):
            print comp[str(orbital)][num]

def open_file(file):
    if len(file.split('.')) > 1:
        if file.split('.')[1] == 'out':
            with open(file,'r') as f:
                data = f.read()
    else:
        try:
            outfile = os.getcwd() +'/' + file + '.out' #Get output file based on user input of calc_id
            with open (outfile, 'r') as f:
                data = f.read()
        except:
            print "The file does not exist!"
    return data
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-active', '--active', help='Determine activs space',action='store_true')
    parser.add_argument('-atom', '--atom', help='Get orbitals for specific atom')
    parser.add_argument('-orbital','--orb_type', help='Type of orbital for specific atom')
    parser.add_argument('-dorbs','--d_orbitals',help='Get d-orbitals with > 10% character', action='store_true')
    parser.add_argument('-range','--range',type=int, nargs=2, help='Specify a range of orbitals')
    parser.add_argument('-thresh', '--threshold', type=Decimal, help="Orbital Composition Threshold Percentage", default=10)
    parser.add_argument('-spin', '--spin', nargs = '?', const='Mulliken',help='Get Spin Densities')
    parser.add_argument('-charge', '--charge', nargs = '?', const = 'Mulliken', help='Get Atomic Charges')
    parser.add_argument('-plot', '--plot', nargs ='*', default=None, help="Plot orbitals")
    parser.add_argument('-res','--resolution', help='Change resolution of orbitals to 80', action='store_true')
    parser.add_argument("calcid", help="Give name of output file.")
    args = parser.parse_args()
    main(args)
