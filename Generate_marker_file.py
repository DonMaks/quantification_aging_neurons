import numpy as np
import utility
from skimage import io
import os


directory = 'D:\\testdata_wavyness\\PLM\\'
imagefolder = directory + 'images\\'
markerfolder = directory + 'marker\\'
files = os.listdir(imagefolder)
files = [file for file in files if file.endswith('.tif')]
if not os.path.exists(markerfolder):
    os.makedirs(markerfolder)
    



for file in files:
    stack = io.imread(imagefolder + file) 
    starting_point = utility.findStartPLMwithBorder(stack)
    #starting_point2 = utility.findStartPLM(stack)
    line = [str(starting_point[2]), str(stack.shape[1]-starting_point[1]), str(starting_point[0]), str(0), str(1), '', '', '', '', '']
    line = ', '.join(line)
    markerfile = file[:-4] + '.marker'
    with open(markerfolder + markerfile, 'w') as fl:
        fl.write(str(line))
        
