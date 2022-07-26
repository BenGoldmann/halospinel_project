from pymatgen.core import Structure
from pymatgen.io.cif import CifWriter
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
import numpy as np

def framework_symmetry(structure, reference):
    """This removes mobile Li ions, then finds symmetry information for the framework of the halospinel"""
    
    def round_to_value(a):
        """This adjusts ionic positions to be perfectly aligned on nearest Wyckoff site"""
        multiplier = a/0.125
        rounded_multiplier = np.round(multiplier, 0)
        return rounded_multiplier * 0.125

    def reorder(a):
        """This changes any frac_coord of 1 to 0"""
        position = [0, 1, 2]
        for i in position:
            if a[i] == 1.:
                a[i] = 0
            else:
                continue
                
    name = structure[17:-4]
    
    ref = Structure.from_file(reference)
    strc = Structure.from_file(structure)
    
    spg_strc = SpacegroupAnalyzer(structure=strc, symprec=0.01, angle_tolerance=5.0)
    
    spg_symbol_strc = spg_strc.get_space_group_symbol()
    spg_number_strc = spg_strc.get_space_group_number()
    lattice_type_strc = spg_strc.get_lattice_type()
    crystal_system_strc = spg_strc.get_crystal_system()
    
    for atom in strc:
        strc_corrected = (round_to_value(atom.frac_coords))
        atom.frac_coords = strc_corrected
        reorder(atom.frac_coords)
    
    positions = np.arange(0, 54)
    
    to_delete = [] 
    
    for atom1, label in zip(strc, positions):
        for atom2 in ref:
            if np.array_equal((atom1.frac_coords), (atom2.frac_coords), equal_nan=False) == True:
                if atom2.species_string == 'Na':
                    to_delete.append(label)
                elif atom2.species_string == 'Li':
                    to_delete.append(label)
                elif atom2.species_string == 'Be':
                    to_delete.append(label)
                elif atom2.species_string == 'Nb':
                    to_delete.append(label)
            else:
                continue
                
    to_delete.sort(reverse=True)            
            
    for d in to_delete:
        del strc[d]
        
    w = CifWriter(strc)
    w.write_file(f'./frameworks_1m/{name}_framework.cif')

    frmw = Structure.from_file(f'./frameworks_1m/{name}_framework.cif')
    
    spg_frmw = SpacegroupAnalyzer(structure=frmw, symprec=0.01, angle_tolerance=5.0)
    
    spg_symbol_frmw = spg_frmw.get_space_group_symbol()
    spg_number_frmw = spg_frmw.get_space_group_number()
    lattice_type_frmw = spg_frmw.get_lattice_type()
    crystal_system_frmw = spg_frmw.get_crystal_system()
    
    framework_properties = {
        "structure": name,
        "spg_symbol_framework": spg_symbol_frmw,
        "spg_number_framework": spg_number_frmw,
        "lattice_type_framework": lattice_type_frmw,
        "crystal_system_framework": crystal_system_frmw,
        "spg_symbol_structure": spg_symbol_strc,
        "spg_number_structure": spg_number_strc,
        "lattice_type_structure": lattice_type_strc,
        "crystal_system_structure": crystal_system_strc
    }
    
    return framework_properties