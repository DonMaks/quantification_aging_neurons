'''Calculate the kink density allong a mainbranch and the kink density in windows around neuriteoutgrowths.
Test for github.'''

import utility
import numpy as np

def calculateKinkDensityAroundNeuriteoutgrowths(annotated_mainbranch='data/trees/annbranch.swc', 
                                                window_size=4.0, 
                                                scale=(0.223, 0.223, 0.3)):
    """
    Caluclate the kink density around neuriteoutgrowths.

    Parameters
    ----------
    annotated_mainbranch : np.array
        An annotated mainbranch in .swc format where the neurite outgrowth branching points are annotated with TYPE 1 and the kinks are annotated with RADIUS 2.
    window_size : float
        Size of the window wich is used for density calculation in um.
    scale : tuple
        (x, y, z) scales of the original images [um/px]

    Returns
    -------
    kink_density : float
        The local kink density in a window around neurite outgrowths

    """
    if isinstance(annotated_mainbranch, str):
        annotated_mainbranch = utility.readSWC(annotated_mainbranch)
    else:
        annotated_mainbranch = annotated_mainbranch
    
    branching_nodes = annotated_mainbranch[np.where(annotated_mainbranch[:,1]==1)]
    n_kinks_local = np.zeros(len(branching_nodes))
    window_sizes = np.zeros(len(branching_nodes))
    
    
    for i in range(len(branching_nodes)):
        window = utility.findWindow(branching_nodes[i], annotated_mainbranch, window_size=window_size, scale=scale)
        n_kinks_local[i] = (window[:,5]==3).sum()
        window_sizes[i] = utility.calculateDistancesTree(window, scale=scale)
    
    n_kinks_sum = n_kinks_local.sum()
    total_window_size = window_sizes.sum()
    density_around_outgrowths = n_kinks_sum/total_window_size
    
    n_kinks_total = (annotated_mainbranch[:,5]==3).sum()
    length_total = utility.calculateDistancesTree(annotated_mainbranch, scale=scale)
    density_total = n_kinks_total/length_total
    
    return density_around_outgrowths, density_total
    



if __name__ == '__main__':
    calculateKinkDensityAroundNeuriteoutgrowths()