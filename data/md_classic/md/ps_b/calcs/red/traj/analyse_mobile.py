from ovito.io import import_file, export_file
from ovito.modifiers import CalculateDisplacementsModifier
from ovito.modifiers import ExpressionSelectionModifier
import numpy

# Load input data and create a data pipeline.
pipeline = import_file("red_600.lammpstrj")

# Calculate per-particle displacements with respect to initial simulation frame:
pipeline.modifiers.append(CalculateDisplacementsModifier())

# Define the custom modifier function:
def calculate_msd(frame, data):

    # Access the per-particle displacement magnitudes computed by the 
    # CalculateDisplacementsModifier that precedes this user-defined modifier in the 
    # data pipeline:
    displacement_magnitudes = data.particles['Displacement Magnitude']
    
    li_displacement_magnitudes = displacement_magnitudes[:8704]
    
    # Compute MSD:
    msd = numpy.sum(li_displacement_magnitudes[:3072] ** 2) / len(li_displacement_magnitudes[:3072])

    # Output MSD value as a global attribute: 
    data.attributes["MSD"] = msd 
    
# Insert user-defined modifier function into the data pipeline.
pipeline.modifiers.append(calculate_msd)

# Export calculated MSD value to a text file and let OVITO's data pipeline do the rest:
export_file(pipeline, "stationary_li_600.txt", 
    format = "txt/attr",
    columns = ["Timestep", "MSD"],
    multiple_frames = True)