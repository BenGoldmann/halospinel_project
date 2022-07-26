import glob
from multiprocessing import Pool
import pandas as pd
from itertools import repeat
from framework_symmetry import framework_symmetry

    
results = []
initials = glob.glob('./1k/*.cif')

if __name__ == '__main__':
    with Pool(processes=4) as pool:
        results.append(pool.starmap(framework_symmetry, zip(initials, repeat('prim_inverse.cif')), chunksize=1))

res = []

for r in results[0]:
    res.append(r)
len(res)

df_res = pd.DataFrame(res)
df_res.head()
df_res.to_csv('./tial_1.csv', index=False)