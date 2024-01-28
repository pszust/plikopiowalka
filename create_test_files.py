import os
import shutil
import numpy as np

if os.path.isdir('test_files'):
    shutil.rmtree('test_files')

os.mkdir('test_files')
sampleNames = ['Sample01', 'Sample02', 'Sample02_heated', 'Sample03', 'Sample03_heated', 'Sample03_melted']

for sampleName in sampleNames:
    numFiles = 2 + int(5*np.random.random())
    for num in range(numFiles):
        with open(f'test_files/{sampleName}_{str(num).zfill(2)}.txt', 'w') as f:
            f.write('test file \n')
