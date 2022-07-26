from ovito.io import import_file, export_file
from ovito.modifiers import CalculateDisplacementsModifier
from ovito.modifiers import ExpressionSelectionModifier
from ovito.modifiers import UnwrapTrajectoriesModifier
import numpy
import glob
from multiprocessing import Pool

def msd_output(dumpfile):
    # Load input data and create a data pipeline.
    pipeline = import_file(dumpfile)
    
    # Unwrap trajectories:
    pipeline.modifiers.append(UnwrapTrajectoriesModifier())

    # Calculate per-particle displacements with respect to initial simulation frame:
    pipeline.modifiers.append(CalculateDisplacementsModifier())

    # Define the custom modifier function:
    def calculate_msd(frame, data):

        # Access the per-particle displacement magnitudes computed by the 
        # CalculateDisplacementsModifier that precedes this user-defined modifier in the 
        # data pipeline:
        displacement_magnitudes = data.particles['Displacement Magnitude']
        particle_types = data.particles['Particle Type']
    
        # Compute MSD:
        msd = numpy.sum(displacement_magnitudes[particle_types == 1] ** 2) / len(displacement_magnitudes[particle_types == 1])
    
        # Output MSD value as a global attribute: 
        data.attributes["MSD"] = msd 
    
    # Insert user-defined modifier function into the data pipeline.
    pipeline.modifiers.append(calculate_msd)

    # Export calculated MSD value to a text file and let OVITO's data pipeline do the rest:
    export_file(pipeline, "li_600.txt", 
        format = "txt/attr",
        columns = ["Timestep", "MSD"],
        multiple_frames = True)    
    
msd_output('600_red.lammpstrj')