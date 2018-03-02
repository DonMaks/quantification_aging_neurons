import cleanup
import classify
import wavyness
import somavolume_multipleseeds
import correlation
import os
import datetime
import csv
from tqdm import tqdm
from winsound import MessageBeep

#Parameters
clean = False
length_threshold = 3
neurontypes = ['PLM']
visualize_somavolumes = False
root = 'D:/data/'
infolder = 'traces/'
infolder_tif = 'images/'


outfolder_cleanedtrees = 'cleanedtrees/'
outfolder_classifiedtrees = 'classifiedtrees/'
outfolder_mainbranch = 'mainbranches/'
outfolder_wavytrees = 'wavytrees/'
outfolder_kinks = 'kinks/'
outfolder_gifs = 'somavolume_gifs/'
time = datetime.datetime.now().__str__()[0:19].replace(' ','_').replace(':', '-')
measurement_filename = 'IndividualMeasurements_' + time + '.csv'
measurement_filename2 = 'SummaryMeasurements_' + time + '.csv'


scale = (0.223, 0.223, 0.3)

#Write the outfile header
with open(root + measurement_filename, 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(['Condition'] + ['Age'] + ['Name'] + ['Series'] + ['Neurontype'] + ['Class'] + ['Length'] + ['MeanRadius'] + ['MaxRadius'] + ['Gaussian'] + ['Censored'])

with open(root + measurement_filename2, 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(['Condition'] + ['Age'] + ['Name'] + ['Series'] + ['Neurontype'] + 
                        ['SomaOutgrowthLength'] + ['SomaOutgrowthCount'] + ['NeuriteOutgrowthLength'] + ['NeuriteOutgrowthCount'] + 
                        ['KinkCount'] + ['SomaVolume'] + ['KinkDensityTotal'] + ['KinkDensityLocal'] +
                        ['ThresholdAngle'] + ['Gaussian'] + ['Censored'])


for neurontype in neurontypes:
    n_infolder = root + neurontype + '/' + infolder
    n_infolder_tif = root + neurontype + '/' + infolder_tif
    n_outfolder_cleanedtrees = root + neurontype + '/' + outfolder_cleanedtrees
    n_outfolder_classifiedtrees = root + neurontype + '/' + outfolder_classifiedtrees
    n_outfolder_mainbranch = root + neurontype + '/' + outfolder_mainbranch
    n_outfolder_wavytrees = root + neurontype + '/' + outfolder_wavytrees
    n_outfolder_kinks = root + neurontype + '/' + outfolder_kinks
    if neurontype=='ALM' and visualize_somavolumes:
        n_outfolder_gifs = root + neurontype + '/' + outfolder_gifs
    
    
    #Make all the approriate folders
    if not os.path.exists(n_infolder):
        os.makedirs(n_infolder)
    if not os.path.exists(n_outfolder_cleanedtrees):
        os.makedirs(n_outfolder_cleanedtrees)
    if not os.path.exists(n_outfolder_classifiedtrees):
        os.makedirs(n_outfolder_classifiedtrees)
    if not os.path.exists(n_outfolder_mainbranch):
        os.makedirs(n_outfolder_mainbranch)
    if not os.path.exists(n_outfolder_wavytrees):
        os.makedirs(n_outfolder_wavytrees)
    if not os.path.exists(n_outfolder_kinks):
        os.makedirs(n_outfolder_kinks)
    try:
        if not os.path.exists(n_outfolder_gifs):
            os.makedirs(n_outfolder_gifs)
    except:
        n_outfolder_gifs=None
    
    files = os.listdir(n_infolder)
    files = [file for file in files if file.find('.swc') > -1]
    for file in tqdm(files):
        file_tif = file[:-4] + '.tif'
        string = file[:-4]
        dat = string.split('_')
        strain = dat[0]
        series = dat[1]
        age = dat[2]
        name = dat[3]
        gaussian_sigma = dat[4]
        #algorithm = dat[5]
        #decon = dat[6]
        
        if clean == True:
            cleanup.cleanup(infilename=n_infolder+file,
                            outfilename=n_outfolder_cleanedtrees+file,
                            neurontype=neurontype,
                            scale=scale,
                            visualize=True)
        else:
            n_outfolder_cleanedtrees = n_infolder
        
        tree_lengths, tree_classes, tree_mean_radii, tree_max_radii, mainbranch, annotated_mainbranch = classify.classify(infilename=n_outfolder_cleanedtrees+file, 
                                                       outfilename_tree=n_outfolder_classifiedtrees+file,
                                                       outfilename_mainbranch=n_outfolder_mainbranch+file,
                                                       neurontype=neurontype,
                                                       length_threshold=length_threshold,
                                                       scale=scale)
        
        kinks_count, angle_threshold, fully_annotated_mainbranch = wavyness.wavyness(infilename_or_mainbranch=annotated_mainbranch,
                          outfilename_tree=n_outfolder_wavytrees+file,
                          outfilename_kinks=n_outfolder_kinks+file,
                          angle_threshold=145,
                          window_size_linear_regression=4.0,
                          window_size_maximum_supression=4.0,
                          n_colors=10,
                          scale=scale,
                          fix_node=False,
                          plot_cdf=False)
        
        density_around_outgrowths, density_total = correlation.calculateKinkDensityAroundNeuriteoutgrowths(
            annotated_mainbranch=fully_annotated_mainbranch, 
            window_size=4.0, 
            scale=scale)
        
        if neurontype=='ALM':
            soma_volume = somavolume_multipleseeds.somavolume(filename_swc=n_outfolder_classifiedtrees+file,
                                                filename_tif=n_infolder_tif+file_tif,
                                                scale=scale,
                                                visualize=visualize_somavolumes,
                                                outfolder_gif=n_outfolder_gifs)
        else:
            soma_volume = 0
        
        with open(root + measurement_filename, 'a', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for i in range(len(tree_lengths)):
                spamwriter.writerow([strain] + [age] + [name] + [series] + [neurontype] + 
                                    [str(tree_classes[i])] +  [str(tree_lengths[i])]  +  [str(tree_mean_radii[i])]  +  [str(tree_max_radii[i])]  +  [gaussian_sigma]  + [str(0)])
                
        
        soma_total = 0
        neurite_total = 0
        for i in range(len(tree_lengths)):
            if tree_classes[i] == 'SomaOutgrowth':
                soma_total += tree_lengths[i]
            elif tree_classes[i] == 'NeuriteOutgrowth':
                neurite_total += tree_lengths[i]
        
        with open(root + measurement_filename2, 'a', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            
            spamwriter.writerow([strain] + [age] + [name] + [series] + [neurontype] + 
                                [str(soma_total)] +  [str(tree_classes.count('SomaOutgrowth'))] +  [str(neurite_total)] + [str(tree_classes.count('NeuriteOutgrowth'))]  +  
                                [str(kinks_count)] + [str(soma_volume)] + [str(density_total)] + [str(density_around_outgrowths)] +
                                [str(angle_threshold)] + [gaussian_sigma]  + [str(0)])
            #spamwriter.writerow([strain] + [age] + [name] + [series] + [neurontype] + ['SomaOutgrowth'] +  [str(soma_total)]  +  [str(tree_classes.count('SomaOutgrowth'))]  + [gaussian_sigma]  + [str(0)])        
        
        #print('***DONE***')
    
MessageBeep()
