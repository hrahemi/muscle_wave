# -*- coding: utf-8 -*-

"""""""""""""""""""""""""""""""""""""""""

Created on Sat Feb 20 02:04:06 2016



@authors: James Wakeling, Hadi Rahemi

"""""""""""""""""""""""""""""""""""""""""





import numpy as np



import warnings # current version of seaborn generates a bunch of warnings that we'll ignore

warnings.filterwarnings("ignore")



import matplotlib.pyplot as plt

import math

import scipy.stats as spy

from Tkinter import *

import tkMessageBox as tkm

import os

import re

"""""""""""""""""""""

Global parameters

"""""""""""""""""""""

scale = 0.3

q = 1.45

r = 1.959

offset = 1024

#############################################################################



def num_of_waves(entries):

    #   This defines the set of centre frequencies on which the wavelets are based: see von Tscharner (2000)

    sampling_frequency = float(entries['Sampling Frequency (Hz)'].get())

    NyQ_frequency=sampling_frequency/2



    num=12

    max_freq=0

    while max_freq< NyQ_frequency:

        num+=1        

        cf=list()          #central frequncies

        for i in range(num):

            cf.append(math.pow(i+q,r)/scale)

        max_freq=max(cf)

        

    num=num-int(sampling_frequency)/1000

    if num<13:      

        return 13

    else:

        return num

   

#############################################################################    

  

def get_cf(number):

    cf=list()          #centre frequncies

    for i in range(number):

        cf.append(round(math.pow(i+q,r)/scale,3))

    return cf

    

#############################################################################

    

def wavelet(f,j):

    

    #   For each wavelet, the frequency response is defined in terms of its centre frequency, scale and num,

    #   where num is dependent on the sample frequency: see von Tscharner (2000)

    

     num=int(math.ceil(sampling_frequency/4000))


     if f>0:

         tmp=1

         for i in range(num):

             tmp= tmp*math.pow(f/cf[j],cf[j]*scale/num)*math.exp((-f/cf[j]+1)*cf[j]*scale/num)

         return tmp 

     else:     

         return 0

  

#############################################################################  


        

def get_intensity(data, wave_num):

    tconvolute=2*np.fft.ifft(np.multiply(data,intwavelet[wave_num])).real

    nom=np.divide(1000,2*math.pi*np.multiply(cf,co))

    convolute1=tconvolute[2:]

    convolute2=tconvolute[:-2]



    #   The power within the signal at each wavelet domain is calculated at each time point from the magnitude

    #   and first time-derivative of the square of the convoluted signal. This power is termed  the intensity

    #   in this wavelet analysis and forms an energy envelope around the (square) of the signal contained within this

    #   wavelet domain (von Tscharner, 2000, Wakeling et al. 2002). Note that this intensity assumes the power occurs

    #   at the centre frequency for each wavelet, rather than across its full frequency band. Hence the intensity is

    #   a close approximation to the power within the signal

    

    intensity=np.power(tconvolute[1:-1],2)+np.power(nom[wave_num]*(convolute2-convolute1)/(2*timestep),2)

    intensity=np.insert(intensity, 0, 0)

    intensity=np.append(intensity,0)

    return intensity

    

#############################################################################


def get_gaussian(resolutions):

    

    #   The computed intensities contain small oscillations due to the finite sampling rate of the EMG. These

    #   oscillations are of shorter duration than the time resolution of the wavelet and so contain no relevant

    #   information. A Gauss filter is therefore finally used to filter out this noise. Because the  frequency

    #   resolution is linked to the time resolution, the frequency response of these Gauss filters is determined

    #   as a function of the time resoolution of the wavelets.

   

    timeres=resolutions

    gaussmatrix=list()

    

    for j in range(number):

        std=3*timeres[j]*sampling_frequency/(8*1000.0)

        ndist=spy.norm(0,std)

        

        gauss=list()

        for x in range(points):

            gauss.append(ndist.pdf(1-points/2+x))

        

        gaussmatrix.append(

        # math.sqrt(points)*

        np.absolute(np.fft.fft(gauss)))

        

    return gaussmatrix



#############################################################################

  
def get_filtered_intensity(data,wave_num):

        intensity = get_intensity(data, wave_num)

        fintensity=np.multiply(np.fft.fft(intensity),gaussmatrix[wave_num])

        intensity=np.fft.ifft(fintensity).real
        
        return intensity


#############################################################################  
  

def build_wave(entries,plotting_options):

    plt.close('all')

    global sampling_frequency
    
    global number

    global cf

    global co

    global sampling_frequency

    global timestep

    global intwavelet

    global gaussmatrix   
    
    global points

    number=int(entries['Number of Wavelets'].get())

    points=int(entries['Number of wavelet sampling points'].get())

    sampling_frequency = round(float(entries['Sampling Frequency (Hz)'].get()),1)
    
    print sampling_frequency

    if number > num_of_waves(entries):

        ans=tkm.askyesno('Warning!','The number of wavelets is large. This may result in high memory usage and major wait times. Do you want to continue?')

    
    timestep= 1000.0/sampling_frequency     #   time step is in milliseconds

    freqstep=sampling_frequency/points      #   freqstep is in cycles per sample period (which is the number of 'points' given to the analysis

    NyQ_frequency=sampling_frequency/2      #   Nyquist frequency

    

    if sampling_frequency < 1000:

        ans=tkm.askyesno('Warning!', 'Sampling frequncy is very low. This may cause large errors in calculating the intensities. Do you want to continue?')

       
        if ans==True:

            pass

        else:            

            return 
  
    
    cf=get_cf(number)


    intfrequncies=list()

    for i in range(points):

	intfrequncies.append(i*freqstep)

 

    times=list()

    for i in range(points):

	times.append(i*timestep)



    

# Build wavelet bank (Choice of a plot)

	

    waveletmatrix=np.zeros((number,points))

    for j in range(number):

    	for k in range(points):

    		if k<points/2:

    			waveletmatrix[j,k]=wavelet(k*freqstep,j)

    if plotting_options[0]==1:   

        plt.figure(1)
        
        plt.subplot(2,2,1)

        for j in range(number):

            plt.plot(intfrequncies,waveletmatrix[j],'b')

        plt.plot(intfrequncies,waveletmatrix.sum(axis=0,dtype='float'),'r')

        if number==13:

            plt.xlim(0,800)

        else:

            plt.xlim(0,sampling_frequency/2)

        plt.ylim(0,1.5)
        
        plt.xlabel('Frequency')

        plt.title('Wavelet Bank')

        

        

       

   

# Intensity correction



    #   Because of the overlap of the wavelet frequencies, a given frequency could be represented by its

    #   components in up to three adjacent wavelet domains. The power of the myoelectric    signal is the

    #   square of the amplitude. However, the cross-products need to be considered when there is overlap

    #   in the wavelet frequencies. This intensity correction allows the wavelet amplitudes to be scaled

    #   at each frequency so that the sum of the wavelet components at that frequency includes the cross-terms

    #   and, thus, would yield the true power of the signal (von Tscharner, 2000; Wakeling et al. 2002).



    intensitycorrection=[0]

    j=0

    f=freqstep

    

    while wavelet(f,j)>wavelet(f,j+1):

    	intensitycorrection.append(1/(math.pow(math.pow(wavelet(f,j),2)+math.pow(wavelet(f,j+1),2),0.5)))

    	f+=freqstep

    	

    j+=1

    

    while j<number-2:

    	while wavelet(f,j)>wavelet(f,j+1):

    		intensitycorrection.append(1/(math.pow(math.pow(wavelet(f,j),2)+math.pow(wavelet(f,j+1),2)+math.pow(wavelet(f,j-1),2),0.5)))

    		f+=freqstep

    	j+=1

    	

    while wavelet(f,j)<0.98:

    	intensitycorrection.append(1/(math.pow(math.pow(wavelet(f,j),2)+math.pow(wavelet(f,j-1),2),0.5)))

    	f+=freqstep

    	

    while wavelet(f,j)>0.87:

    	intensitycorrection.append(1/(math.pow(math.pow(wavelet(f,j),2)+math.pow(wavelet(f,j-1),2),0.5)))

    	f+=freqstep

    

    while f<NyQ_frequency:

    	intensitycorrection.append(1)

    	f+=freqstep

     

# Set coefficients (Choice of a plot)

	

    damping=np.ones(number)

    

    co=np.ones(number)

    
    maxdev=1

    countdev=0

    maxiter=int(entries['Max iterations for setting coefficients'].get())

    devlimit=0.09*float(entries['Deviation from maximum (%)'].get())
    
    max_devs_list=list()

    while (maxdev > devlimit and countdev < maxiter) or (countdev < 2):
      
		devlist=list()
  
		w=0
		
		
		for w1 in range(number):
      
			   
			intwavelet=np.zeros((number,points))
   
			for j in range(number):
       
				for k in range(points):
        
					if k<points/2:
         
						intwavelet[j,k]=waveletmatrix[j,k]*intensitycorrection[k]*damping[j]



            #   A sine-wave test signal is made to test each wavelet. The wave has an amplidtue of 3, and

            #   so the power of the signal should be 9



			sine=np.zeros(points)
                
			for k in range(points-1):
       
				time= (k+1)/sampling_frequency
    
				sine[k]=3*math.sin(2*math.pi*cf[w1]*time)


			if  w>0 and w1<number and co[w1]>co[w1-1]:

				co[w1]=co[w1-1]
    
    
			ftest=np.fft.fft(sine)

			convolute=np.multiply(ftest,intwavelet[w1])

			tconvolute=2*np.fft.ifft(convolute).real
				

			while True:
       
				nom=np.divide(1000,2*math.pi*np.multiply(cf,co))
    
				convolute1=tconvolute[2:]
    
				convolute2=tconvolute[:-2]
    
				intensity=np.power(tconvolute[1:-1],2)+np.power(nom[w1]*(convolute2-convolute1)/(2*timestep),2)
    
				intensity=np.insert(intensity, 0, 0)
    
				intensity=np.append(intensity,0)						

				

                #   A segment of the calculated intensities is taken to test the ripple in the calculated intensities.

                #   This does not start as the begining of the test intensity, to minimize edge effects in the filtering.


				segment= intensity[int(0.2*points):int(0.8*points)]
    
				if w>0 and w1 < number and max(segment)-min(segment)> 0.1:
        
						co[w1]=co[w1]-0.005           
					
				else:
        
						break

					

			meanvalue=(max(segment)+min(segment))/2 #   Note this is the mean of the calculated intensity.

                                                            #   This should be 9 for the test sine-wave

			dev=max(segment)-min(segment)
                
			devlist.append(dev)
                
			damping[w1]=math.sqrt(9.0/meanvalue)*damping[w1]#   The damping coefficient is

                                                            #   updated so that the intensity will approach 9 on the next iteration
			w+=1
                

		max_devs_list=np.divide(devlist,0.09)

		maxdev=max(devlist[1:])

		countdev+=1
		

    if plotting_options[0]==1:
        
        plt.subplot(2,2,2)
        
        plt.title('Deviation from max errors')
        
        ind = np.arange(number)    # the x locations for the groups
        
        width = 0.35       # the width of the bars: can also be len(x) sequence

        p1=plt.bar(ind, max_devs_list, width, color='b')
        
        plt.xticks(ind + width/2., map(str,ind+1))
        
        p2= plt.axhline(y=devlimit/0.09, linewidth=2, color='r',linestyle='--')
        
        plt.xlabel('Wavelet number')
        
        plt.ylabel('Error (%)')
#        plt.tick_params(axis='x',which='both',bottom='off',top='off',labelbottom='off') 
        
        plt.legend((p1, p2), ('Errors', 'Threshold'))
        

    if countdev==maxiter and maxdev > devlimit:

        ans=tkm.askyesno('Warning!', 'The program did not converge to a coefficients set. '+ \

        'Max deviation is %g' % round(maxdev/0.09,2) + \

        '%. You can try to change the input parameters in Advanced Settings tab.\n\n Do you want to continue with current coefficients?')

        

        if ans==True:

            ans=tkm.showinfo('Coefficients', 'Central Frequencies:\n' + str(cf) + \

            '\n\n' +'Coefficients:\n'+str(co)+ '\n\n' +'Dampings:\n'+str(damping))

            pass

        else:            

            return       

    else:

         ans=tkm.showinfo('Converged!!', 'The program converged to a coefficients set. \n\n'+ \

         'Central Frequencies:\n' + str(cf) + '\n\n' +'Coefficients:\n'+str(co)+ '\n\n' +\

         'Dampings:\n'+str(damping)+'\n\n'+ "Press 'Ok' to continue with the program and wait untill 'Success' page is displayed." )

    print "Central ferqunecies are:"

    print cf,'\n'

    print "Central O's are:"

    print co,'\n'

    print "Dampings are:"

    print damping

    

# Bandwidth from intensity wavelet (Unfiltered time resoloutions - no plots)



    #   The bandwidth is considered as the range of frequencies at which the wavelet has over 1/e of its amplitude



    resolutions=list()

    data=1

    for wave in range(number):

        intensity = get_intensity(data,wave)

        

        limit=max(intensity)/math.e

        k=0

        while intensity[k]<limit:

            k+=1

        k+=1

        while intensity[k]>limit:

            k+=1

        k+=1

        width=timestep*2*k

        resolutions.append(width)

 

# Gaussian Distribution (no plots)

   

    gaussmatrix=get_gaussian(resolutions)

        

# Bandwidth from intensity wavelet   (Unfiltered time resoloutions - choice of a plot) 



    #   The bandwidth is considered as the range of frequencies at which the wavelet has over 1/e of its amplitude



    resolutions=list()

    for wave in range(number):

        intensity = get_filtered_intensity(data, wave)

        limit=max(intensity)/math.e

        k=0

        while intensity[k]<limit:

            k+=1

        k+=1

        while intensity[k]>limit:

            k+=1

        k+=1

        width=timestep*2*k

        resolutions.append(width)

        
    if plotting_options[0]==1:
        
        plt.subplot(2,2,3)
        
        plt.plot(ind+1,resolutions, 'b^')
        
        plt.xlim(0,number+1)
        
        plt.title('Time resolutions')
        
        plt.xlabel('Wavelet number')
        
        plt.ylabel('Resolution (ms)')

        plt.xticks(ind+1, map(str,ind+1))
        

# Final Gaussian Filters (Choice of a plot)


    gaussmatrix=get_gaussian(resolutions)

    

    if plotting_options[0]==1:

        plt.subplot(2,2,4)

        for j in range(number):

            plt.plot(intfrequncies,gaussmatrix[j],'b')

        plt.title('Gaussian filters')

        plt.xlim(0,400)


    plt.show()   

# Exporting Gaussian Distribution, intwavelet and coefficients as CSV files
    try: 
        os.makedirs('build_wave_output')
    except OSError:
        if not os.path.isdir('build_wave_output'):
            raise
    

    np.savetxt('build_wave_output\gauss%d.csv' % sampling_frequency, gaussmatrix, delimiter=',')

    np.savetxt('build_wave_output\wavelet%d.csv' % sampling_frequency, intwavelet, delimiter=',')
    
    np.savetxt('build_wave_output\co%d.csv' % sampling_frequency, co, delimiter=',')



    tkm.showinfo('Success', '''Wavelets and Gaussian filters were saved to "build_wave_output" folder.''')
    
#############################################################################


def wavelet_EMG(data):
    
    intensities = list()
    
    for wave in range(number):

        intensity = get_filtered_intensity(data, wave)
        
        intensities.append(intensity)
        
    return intensities


#############################################################################

def long_wavelet_EMG(data):
    
    length=len(data)
    
    counts=0
    
    start=0
    
    segs=list()
    
    pooled=list()
    
    while True:
        
        counts+=1
        
        if length-start< points:
            
            segs.append([start,length-start+1])
            
            break
        
        else:
            
             segs.append([start,points])
             
             start = start + points - 2 * offset            
       
    for k in range(counts):
        
        s=segs[k][0]
        
        l=segs[k][1]
        
        datasegment = data[s:s+l]   
   
        
        if l < points:
            
            if l == 1:
                
                datasegment=[datasegment]
                
            datasegment=np.lib.pad(datasegment, (0,points-l+1) , 'constant', constant_values=(0,0))
            
        intensities = wavelet_EMG(datasegment)
        
        starttake = offset
        
        endtake = points-offset+1
        
        if k == 0:
            
            starttake = 0
            
        if k==counts:
            
            endtake=l+1
            
        for ints in intensities:
            up_ints=ints[starttake:endtake]
            tmp_pooled=[]
            for j in range(len(up_ints)):
                tmp_pooled.append(up_ints[j])
                
        pooled.append(tmp_pooled)
    
    return np.transpose(pooled)

        
#############################################################################        
 
def total_intensity(data):
    
    ints = long_wavelet_EMG(data)
    
    clean_ints = np.transpose(ints[1:-1])
    
    return np.sum(clean_ints, axis=1)
    
#############################################################################  
#Input data (p * N)
#Covariance matrix (p * p)
#Principal component matrix (p * p)
#Percentages for each component variance
#Weighting matrix (p * N)
    
#N trials,each trial has p samples
#put into N rows and p columns
#termed N*p matrix
    
def PCA_EMG(data):
    
    data= np.array(data)
    
    rows, cols = data.shape
    
    covariance_matrix = np.divide(np.dot(data,np.transpose(data)),(cols-1))
    
    eigvals , eigenvecs = np.linalg.eig(covariance_matrix)
    
    PCs = np.transpose(eigenvecs)
    
    
    variances = []
    
    for i in range(rows):
        
        variances.append (np.dot(np.dot(eigenvecs[i],covariance_matrix),np.transpose(eigenvecs[i])))
        
    
    percentages = 100*variances/np.sum(variances)
    
    weightingmatrix = np.dot(np.transpose(PCs,data))
    
    return PCs, percentages, weightingmatrix

#############################################################################



#############################################################################     

def calculate_intensities(entries,files,cdelim,dec):
    
        
    global sampling_frequency
    
    global number

    global cf

    global co

    global sampling_frequency

    global timestep

    global intwavelet

    global gaussmatrix   
    
    global points
    
      
    number=int(entries['Number of Wavelets'].get())

    points=int(entries['Number of wavelet sampling points'].get())

    sampling_frequency = round(float(entries['Sampling Frequency (Hz)'].get()),1)
    
    timestep= 1000.0/sampling_frequency
    
    head=int(entries['Number of header lines in the file'].get())
 
    chan_cols = np.subtract(map(int,re.findall('[0-9]',entries['Column number of channels to be processed (e.g. 3,4,5,7,9)'].get())),1)
    
    path = entries['Path'].get()
    
    try:
        
        gaussmatrix = np.loadtxt('build_wave_output\gauss%d.csv' % sampling_frequency, delimiter=',')

        intwavelet = np.loadtxt('build_wave_output\wavelet%d.csv' % sampling_frequency, delimiter=',')
    
        co = np.loadtxt('build_wave_output\co%d.csv' % sampling_frequency, delimiter=',')       
    
    except:
        
        tkm.showinfo('Warning', 'One or more of the following files are missing\n\n'+os.getcwd()+'\\build_wave_output\gauss%d.csv\n\n' % sampling_frequency +  \
        
        os.getcwd()+'\\build_wave_output\wavelet%d.csv\n\n' % sampling_frequency + os.getcwd()+'\\build_wave_output\co%d.csv\n\n' % sampling_frequency +  \
        
        "Please make sure you have previously run the 'Build Wavelet' and you sampling frequency entry is filled correcterly.")
        
        return
        
    cf = get_cf(number)
    
    
    
       
    try: 
        
        os.makedirs(path +'\intensity_output')
    
    except OSError:
        
        if not os.path.isdir(path +'\intensity_output'):
            
            raise
    
    count=1
    for file in files:
        
        fhand= open(file)
        
        data=np.genfromtxt(fhand,delimiter=cdelim,skip_header=head, 
                    
                   usecols=tuple(chan_cols))
                   
        
        
        for col in range(len(chan_cols)):
            
            if len(data.shape) == 1:
                
                ints = long_wavelet_EMG(data[:])
                
            else:
            
                ints = long_wavelet_EMG(data[:,col])
#            ints=ints.tolist()   
            
            ints.tofile('intensity_output\\' +'file'+ str(count)+ '_column_%s.txt' %  str(int(chan_cols[col])+1),sep=cdelim)
#            ints=np.array(ints.tolist(), dtype = float)  
#            ints=np.array(ints,dtype='f')
#            np.savetxt('intensity_output\\' +'file'+ str(count)+ '_column_%s.txt' %  str(int(chan_cols[col])+1) , ints,delimiter=cdelim )

        count+=1
            
            
            
            
            
                   