# Import relevant modules.
from multiprocessing import Pool
import numpy as np
import glob
import time
from tqdm import tqdm
from collections import namedtuple
from pymatgen.core import Structure, Lattice
from pymatgen.io.cif import CifWriter
from pymatgen.symmetry.groups import SpaceGroup
from site_analysis.voronoi_site import VoronoiSite
from site_analysis.trajectory import Trajectory
from site_analysis.atom import atoms_from_species_string
from collections import Counter

# Define TRAJ_BLOCK.
TRAJ_BLOCK = namedtuple(
    "TRAJ_BLOCK", ["lines", "timestep", "natoms", "cell", "pbc", "atom_fields"]
)

# Define functions.
def split_traj(lammps_raw_loc):
    """
    This takes a raw LAMMPS trajectory and splits it into individual frames.
    Arguments:
        file_location: location and name of raw LAMMPS file
    """
    lammps_raw_file = open(lammps_raw_loc, 'r')
    lammps_raw_lines = lammps_raw_file.readlines()
    
    frames = range(100000, 2101000, 1000)
    counter = 0

    for line in lammps_raw_lines:
        if "ITEM: TIMESTEP" in line:
            structure_file = open(f'structures/structure_{frames[counter]}.lammpstrj', 'w+')
            structure_file.write(line)
            counter = counter + 1
        else:
            structure_file.write(line)       
            
def parse_step(lines, intial_line=0):
    """
    This takes individual frames in the LAMMPS format and extracts the data into a TRAJ_BLOCK object.
    Arguments:
        lines: LAMMPS frame split into lines
    """
    if "ITEM: TIMESTEP" not in lines[0]:
        raise IOError("expected line {} to be TIMESTEP".format(intial_line))
    if "ITEM: NUMBER OF ATOMS" not in lines[2]:
        raise IOError("expected line {} to be NUMBER OF ATOMS".format(intial_line + 2))
    if "ITEM: BOX BOUNDS xy xz yz" not in lines[4]:
        raise IOError(
            "expected line {} to be BOX BOUNDS xy xz yz".format(intial_line + 4)
        )
        # TODO handle case when xy xz yz not present -> orthogonal box
    if "ITEM: ATOMS" not in lines[8]:
        raise IOError("expected line {} to be ATOMS".format(intial_line + 8))
    timestep = int(lines[1])
    number_of_atoms = int(lines[3])

    # each pbc contains two letters <lo><hi> such that:
    # p = periodic, f = fixed, s = shrink wrap, m = shrink wrapped with a minimum value
    pbc = lines[4].split()[6:]

    bounds = [line.split() for line in lines[5:8]]
    bounds = np.array(bounds, dtype=float)
    if bounds.shape[1] == 2:
        bounds = np.append(bounds, np.array([0, 0, 0])[None].T, axis=1)

    xy = bounds[0, 2]
    xz = bounds[1, 2]
    yz = bounds[2, 2]

    xlo = bounds[0, 0] - np.min([0.0, xy, xz, xy + xz])
    xhi = bounds[0, 1] - np.max([0.0, xy, xz, xy + xz])
    ylo = bounds[1, 0] - np.min([0.0, yz])
    yhi = bounds[1, 1] - np.max([0.0, yz])
    zlo = bounds[2, 0]
    zhi = bounds[2, 1]

    super_cell = np.array([[xhi - xlo, xy, xz], [0, yhi - ylo, yz], [0, 0, zhi - zlo]])
    cell = super_cell.T
    field_names = lines[8].split()[2:]
    fields = []
    for i in range(number_of_atoms):
        fields.append(lines[9 + i].split())
    atom_fields = {n: v.tolist() for n, v in zip(field_names, np.array(fields).T)}

    return TRAJ_BLOCK(lines, timestep, number_of_atoms, cell, pbc, atom_fields)

def create_structure(
    traj_block,
    symbol_field="element",
    position_fields=("x", "y", "z"),
    original_structure=None,
):
    """
    This takes the TRAJ_BLOCK object created by parse_step and creates .cif file.
    Arguments:
        traj_block: TRAJ_BLOCK object
    """
    symbols = traj_block.atom_fields[symbol_field]
    positions = np.array(
        [traj_block.atom_fields[f] for f in position_fields], dtype=float
    ).T

    lattice = Lattice(traj_block.cell)
    structure = Structure(lattice, symbols, positions)

    return structure

def create_traj(lammps_split_loc):
    """
    This takes a halospinel LAMMPS output and uses site-analysis to give information about site occupancy.
    Arguments:
        file_location: location and name of raw LAMMPS file
    """
    # Convert all the frames into .cif files and create list of structures.
    time_ = lammps_split_loc[21:]
    time__ = time_[:-10]
    time_int = int(time__)
    
    lammps_split_file = open(lammps_split_loc, 'r')
    lammps_split_lines = lammps_split_file.readlines()
    
    lammps_parsed = parse_step(lammps_split_lines)
    structure = create_structure(lammps_parsed)
    
    return structure, time_int
          
###########################################################################################################################

if __name__ == '__main__':
    # Split LAMMPS file into frames and create list of frames.
    split_traj('super_al.lammpstrj')

    print('Trajectory split.')

    # Create sites for site-analysis.
    sg = SpaceGroup('Fd-3m:2')
    all_li_structure = Structure.from_file('all_li_structure.cif')
    
    lattice = all_li_structure.lattice
    li1 = Structure.from_spacegroup(sg='Fd-3m:2', lattice = lattice, species=['Li'], coords=[[0.125, 0.125, 0.125]])
    li2 = Structure.from_spacegroup(sg='Fd-3m:2', lattice = lattice, species=['Li'], coords=[[0.000, 0.000, 0.000]]) 
    li3 = Structure.from_spacegroup(sg='Fd-3m:2', lattice = lattice, species=['Li'], coords=[[0.125, 0.125, 0.875]])
    li4 = Structure.from_spacegroup(sg='Fd-3m:2', lattice = lattice, species=['Li'], coords=[[0.500, 0.500, 0.500]])
    li5 = Structure.from_spacegroup(sg='Fd-3m:2', lattice = lattice, species=['Li'], coords=[[0.125, 0.125, 0.625]])
    li_structures = {'Li1': li1,
                     'Li2': li2,
                     'Li3': li3,
                     'Li4': li4,
                     'Li5': li5}
    for strc in li_structures.values():
        strc.make_supercell([3,3,3])
        
    li1_sites = [VoronoiSite(s.frac_coords, label='Li1') for s in li1]
    li2_sites = [VoronoiSite(s.frac_coords, label='Li2') for s in li2]
    li3_sites = [VoronoiSite(s.frac_coords, label='Li3') for s in li3]
    li4_sites = [VoronoiSite(s.frac_coords, label='Li4') for s in li4]
    li5_sites = [VoronoiSite(s.frac_coords, label='Li5') for s in li5]
    sites = li1_sites + li2_sites + li3_sites + li4_sites + li5_sites
    
    # Create atoms for site-analysis.
    start_structure = Structure.from_file('super.cif')
    atoms = atoms_from_species_string(start_structure, 'Li')
    
    # Create Trajectory object.
    trajectory = Trajectory(sites = sites, atoms = atoms)

    print('Trajectory object created.')

    # Add structures to Trajectroy object with multiprocessing frame by frame.
    files = glob.glob('structures/*.lammpstrj')
     
    structures_list = []
    
    with Pool(processes=4) as pool:
        print('Converting frames to Structure objects and adding Structure objects to Trajectory object.')
        process = pool.imap(create_traj, files)
        
        for strc, t_s in tqdm(process, total=len(files)):
            trajectory.append_timestep(strc, t_s)
    
    if len(trajectory) > 0:
        print('Frames added to trajectory.')
    else:
        print('Frames NOT added to trajectory.')
        
    # Output data about occupancy.
    file = open('results.txt', 'w+')
    c = Counter()
    print('Analysing trajectory.')
    for site in trajectory.sites:
        c[site.label] += len([1 for ts in site.trajectory if len(ts)>0])
    for k, v in c.items():
        file.write(f'{k} {(v/len(trajectory))/27}\n')