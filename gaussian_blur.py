import os
from scipy.ndimage.filters import gaussian_filter
import numpy as np
from skimage import io
import winsound


def calculate3DSigma(sigma, scale=(1,1,1)):
    scale = np.array(scale)
    reci_scale = 1/scale
    norm_reci_scale = reci_scale/reci_scale[0]
    return list(norm_reci_scale*sigma)

folder = 'D:/testdata_wavyness/PLM/images_raw/'
outfolder = 'D:/testdata_wavyness/PLM/images/'
#folder = 'E:/images/PLM/images_raw/'
#outfolder = 'E:/images/PLM/images/'
if not os.path.exists(outfolder):
    os.makedirs(outfolder)
filenames = os.listdir(folder)
filenames = [filename for filename in filenames if filename.endswith('.tif')]
scale = (0.223, 0.223, 0.3)
sigmas = [0.7]
s = calculate3DSigma(sigmas[0], scale=scale)


for filename in filenames:
    for sigma in sigmas:
        sigma_3d = calculate3DSigma(sigma, scale=scale)
        outfilename = filename[:-4] + '_gs' + str(sigma).replace('.','-') + '.tif'
        #outfilename = filename.replace('0-0', str(sigma).replace('.','-'))
        image = io.imread(folder + filename)
        blurred_image = gaussian_filter(image, sigma=sigma_3d)
        io.imsave(outfolder + outfilename, blurred_image)


winsound.MessageBeep()
winsound.MessageBeep()
winsound.MessageBeep()