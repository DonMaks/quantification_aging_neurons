'''Load a APP2 traced .swc file and clean it up, save a cleaned .swc file.'''
import utility
import numpy as np
import itertools
import matplotlib.pyplot as plt
from scipy.stats import linregress as linregress
import os

def traceBranch(endpoint, tree, main_nodes=[], soma_nodes=[], scale=(1,1,1)):
    '''Trace from an endpoint to a root node or any other node specified in main_branch soma_nodes and pmv_nodes.'''
    if isinstance(endpoint, (float, int)):
        endpoint_index = endpoint
    else:
        endpoint_index = endpoint[0]
    if isinstance(tree, list):
        tree = np.array(tree)
    if isinstance(main_nodes, np.ndarray):
        main_nodes = main_nodes.tolist()
    if isinstance(soma_nodes, np.ndarray):
        soma_nodes = soma_nodes.tolist()
 
    
    #any tracing eventually stops in a root_node
    root_nodes_array = utility.findRoots(tree, return_node=True)
    root_nodes = root_nodes_array.tolist()

    
    branch = []
    length = 0
    current_node = utility.thisNode(endpoint_index, tree, as_list=False)
    branch.append(current_node)
    count = 0
    while current_node.tolist() not in root_nodes and current_node.tolist() not in main_nodes and current_node.tolist() not in soma_nodes:
        count += 1
        if count > 10000:
            break

        next_node = utility.nextNode(current_node, tree)
        dist = utility.dist3D(current_node, next_node, scale=scale)
        length += dist
        current_node = next_node
        branch.append(current_node)
    
    branch_array = np.array(branch)
    return branch_array, length
    

def cleanup(infilename='data/trees/plm.swc',
            outfilename='data/trees/plm_clean.swc',
            neurontype='PLM',
            scale=(0.223, 0.223, 0.3),
            visualize=True):
    
    tree = utility.readSWC(infilename)
    endpoints = utility.findEndpoints(tree)
    
    #For ALM neurons detect the soma_nodes i.e. all nodes connected to the root that are above a threshold
    if neurontype=='ALM':
        soma_nodes = utility.findSomaNodes(tree, scale=scale)
    else:
        soma_nodes = []
    
    #Trace from every endpoint to a root and save the corresponding branches, select the longest as mainbranch
    branches = []
    lengths = np.zeros(len(endpoints))
    for i in range(len(endpoints)):
        branch, length = traceBranch(endpoints[i], tree, soma_nodes=soma_nodes, scale=scale)
        branches.append(branch)
        lengths[i] = length
    mainbranch = branches[lengths.argmax()]
    mainbranch_length = lengths.max()-mainbranch[-1][5]*scale[0] #the last node is part of the soma and its radius gets subtracted from the final length
    
    
    #Trace from every endpoint to a node on the mainbranch to find sidebranches
    side_branches = []
    side_lengths = np.zeros(len(endpoints))
    for i in range(len(endpoints)):
        branch, length = traceBranch(endpoints[i], tree, main_nodes=mainbranch, soma_nodes=soma_nodes, scale=scale)
        side_branches.append(np.flip(branch, axis=0))
        side_lengths[i] = length-branch[-1][5]*scale[0]
    
    
    
    #check if sidebranches are close and parallel to mainbranch
    if visualize:
        fig, axes = plt.subplots(2, 1, sharex='col')
    all_distances = []
    all_slopes = []
    clean_side_branches = []
    windows = []
    for side_branch in side_branches:
        root = utility.findRoots(side_branch, return_node=True)[0]
        if root.tolist() in soma_nodes:
            window = [root] #set the searching window to the root node in case of alm soma_outgrowth side_branch.
        else:
            window = utility.findWindow(root, mainbranch, window_size=40, scale=scale)
        windows.append(window)
        min_distance_from_mainbranch = []
        for node in side_branch:
            distances = []
            for main_node in window:
                distances.append(utility.dist3D(node, main_node, scale=scale))
            min_distance_from_mainbranch.append(min(distances))
        #all_distances.append(min_distance_from_mainbranch)
        min_distance_from_mainbranch = min_distance_from_mainbranch[5:]
        if visualize:
            axes[0].plot(min_distance_from_mainbranch)
        all_distances.append(min_distance_from_mainbranch)
        
        n = 4
        out = np.zeros(n).tolist()
        x = np.arange(n)
        for i in range(len(min_distance_from_mainbranch)-n):
            data = min_distance_from_mainbranch[i:i+n]
            try:
                slope, intercept, r_value, p_value, std_err = linregress(x, data)
            except ValueError:
                break
            if slope > 0.05:
                pass
            out.append(slope)
        
        if visualize:
            axes[1].plot(out, '.')
        #out.insert(0, np.zeros(n).tolist())
        all_slopes.append(out)
        
    
    if visualize:    
        plt.show()
    
    
    
    start_node_index = np.zeros(len(all_slopes))
    for i in range(len(all_slopes)):
        if len(all_slopes[i])==len(all_distances[i]):
            for j in range(len(all_slopes[i])):
                if all_slopes[i][j] > 0.02 or all_distances[i][j] > 0.5:
                    start_node_index[i] = j
                    break
    
    
    for i in range(len(start_node_index)):
        if start_node_index[i] == 0:
            clean_side_branches.append(side_branches[i])
        else:
            new_side_branch = side_branches[i]
            new_side_branch = new_side_branch[int(start_node_index[i]):]
            window = windows[i]
            distances = np.zeros(len(window))
            for i in range(len(window)):
                distances[i] = utility.dist3D(new_side_branch[0], window[i])
            connection_node = window[distances.argmin()]
            new_side_branch[0][6] = connection_node[0]
            clean_side_branches.append(new_side_branch)
    
    
    #connect everything again and save clean .swc file
    full_clean_tree = []
    for node in mainbranch:
        full_clean_tree.append(node)
    for node in soma_nodes:
        full_clean_tree.append(node)
    for clean_side_branch in clean_side_branches:
        for node in clean_side_branch:
            full_clean_tree.append(node)
    
    full_clean_tree = np.array(full_clean_tree)
    full_clean = utility.removeDoubleNodes(full_clean_tree)
    utility.saveSWC(outfilename, full_clean)

if __name__ == '__main__':
    cleanup()