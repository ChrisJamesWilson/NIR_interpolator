
import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate as interp
import os
from astropy.io import fits
import retrieve_irtf as ret
#from mpl_toolkits.mplot3d import Axes3D



# t is a table of the stars in the irtf library. The coloumns are: ID,   Teff(K),   logg,   Z/Zsun



t = ret.param_retrieve()

Teff = np.array(t[1])
logg = np.array(t[2])
g = 10**logg
Z = np.array(t[3])

ID = t[0]
tt = np.stack((Teff,g,Z), axis=1)

for j in range(len(ID)):

	Teff_new = tt[j,0]
	g_new = tt[j,1]
	Z_new = tt[j,2]
	t = np.delete(tt, j, 0)


	range_Teff = max(Teff)-min(Teff)
	#Teff_new = input('Please enter a Teff between ' + str(max(Teff)) + ' and ' + str(min(Teff)))
	#Teff_new = 3810
	range_logg = max(logg)-min(logg)
	#logg_new = input('Please enter a logg between ' + str(max(logg)) + ' and ' + str(min(logg)))
	#logg_new = 4.65
	range_Z = max(Z)-min(Z)
	#Z_new = input('Please enter a Z between ' + str(max(Z)) + ' and ' + str(min(Z)))
	#Z_new = 0.00
	new_point = np.array([Teff_new, g_new, Z_new])

	IDcomp = ID[j]

	print('Calculating Spectra for ID: ' + IDcomp)
	print('Teff: ' + str(Teff_new))
	print('logg: ' + str(np.log10(g_new)))
	print('Z: ' + str(Z_new))

	# Removed IRL152 for testing





	#plt.figure()

	#cm = plt.cm.get_cmap('PRGn')
	#plot = plt.scatter(Teff, logg, c=Z, cmap=cm)
	#plt.colorbar(plot)
	#plt.scatter(Teff_new,logg_new, c='r')
	#plt.xlabel('Teff')
	#plt.ylabel('logg')
	#plt.gca().invert_xaxis()
	#plt.gca().invert_yaxis()

	#plt.show()

	length = len(t[:,0])
	#one = np.ones((length,3))
	#t_big = np.dot(one, new_point, out=None)
	new_point_big = np.tile(new_point,(length,1))
	#Creates an array of a chosen point of length of orginal data, to directly
	#compare the two

	Tn = 1
	gn = 1
	Zn = 1

	Diff = abs(new_point_big - t)

	Diff[:,0] = Diff[:,0]**Tn
	Diff[:,1] = Diff[:,1]**gn
	Diff[:,2] = Diff[:,2]**Zn

	# nth power
	compare = np.array([Diff[:,0]/max(Diff[:,0]), Diff[:,1]/max(Diff[:,1]), Diff[:,2]/max(Diff[:,2])])
	# Normalises values based on the parameters respective ranges

	#mean = np.sum(compare, axis=1)/3
	dist = np.sqrt(compare[0,:]**2 + compare[1,:]**2 + compare[2,:]**2)
	# Finds the relative normalised differences of any empirical star to the defined point
	diff_sort = np.sort(dist)

	radii = 0.05

	if diff_sort[0] == 0:
		stars = np.where(dist == 0)[0]
	else:
		stars = np.where(dist < radii)[0]

	while len(stars) > 3:
		print(str(radii))
		radii += -0.001
		if diff_sort[0] == 0:
			stars = np.where(dist == 0)[0]
		else:
			stars = np.where(dist < radii)[0]

	while len(stars) == 0 and radii < 0.7:
		print('No stars within the selected radius: ' + str(radii))
		radii += 0.001
		if diff_sort[0] == 0:
			stars = np.where(dist == 0)[0]
		else:
			stars = np.where(dist < radii)[0]

	print('Stars selected = ' + str(len(stars)))

	if radii >= 0.7:
		print('Insufficient stars within local parameter space to create a sufficient spectra')
	else:
		#close = 5

		#star = np.zeros(close)

		#for i in range(close):
			#star[i] = int(np.where(mean == diff_sort[i])[0][0])

		# Square and squareroot would probably be a better idea here

		#########
		# Method 1 #
		#########

		# Method 1 is such that ALL stars are considered for a single point.
		# We do so by again normalising the relative differences (mean) to now be
		# relative to each other, and using that as a basis for interpolation

		n = 1
		# pol = (n-1)**3
		pol = 1

		print('n = ' + str(n))
		print('pol = ' + str(pol))

		if diff_sort[0] == 0:
			rel_weight = np.zeros(len(dist))
			rel_weight[stars] = 1/len(stars)
		else:
			rel_weight = (1/dist**pol)
			rel_weight = rel_weight/np.sum(rel_weight[stars])

		 # Now each of these stars are indexed according to their position in the original
		 # data, and this rel_mean value should be a multiplier of their spectral values,
		 # summative to the final star

		#########
		# Method 2 #
		#########
		 
		# # Method 2 is similar to 1, but instead picks a few of the closest values.
		#
		#ind = np.argsort(mean)
		#closest = np.array([np.where(ind==0)[1], np.where(ind==1)[1], np.where(ind==2)[1]])
		# # Location of the 3 closest 
		#stars = np.array([t[closest[0][0]], t[closest[1][0]], t[closest[2][0]]])
		#
		#rel_weight = np.array([compare[0][2][closest[0][0]], compare[0][2][closest[1][0]],\
		#             compare[0][2][closest[2][0]]])
		#             
		#rel_weight = rel_weight/sum(rel_weight)
		#
		# # Has normalised the weighting of these 3 stars vs the chosen point. These 
		# # weights must then be multiplies with the corresponding stars
		#spec_ID = np.array([ID[closest[0][0]], ID[closest[1][0]], ID[closest[2][0]]])


		##########################
		 # Dealing with the files
		##########################

		int_spectra = np.zeros(15000)

		for i in stars:
			int_spectra = int_spectra + ret.get_spectra(ID[int(i)])[:,1]*rel_weight[int(i)]

			# Sets up a length x (i+1) array of the spectras, where the first column
			# is the x axis and the other columns are the chosen stars in order of
			# closest to farthest 
			# Also multiplies the spectra by their relative weights to the chosen point


		#for i in range(3):
		#	plt.figure()
		#	plt.plot(chosen_spectra[:,0],chosen_spectra[:,i+1]/rel_weight[i])


		#int_spectra = np.array([chosen_spectra[:,0], chosen_spectra[:,1:].sum(axis=1)]).T

		#t_1 = ret.get_spectra(ID[int(stars[0])])
		#t_2 = ret.get_spectra(ID[int(stars[1])])
		#t_3 = ret.get_spectra(ID[int(stars[2])])
		t_rl = ret.get_spectra(IDcomp)

		#t2 = np.loadtxt('sometxt.txt')

		#t2[:,1][abs(t2[:,1])>9e2] = 0

		#x = np.linspace(0,len(t2),len(t_1))

		#fp = t2[:,0]

		#xp = np.linspace(0,len(t2),len(t2))

		#gp = np.interp(x,xp,fp)

		#gp = np.arange(0,len(t_1))


		print('Difference in the Interpolated Spectra and the Empirical Spectra is: ' + str(np.sum(abs(int_spectra-t_rl[:,1]))))

		diffs = abs(int_spectra-t_rl[:,1])

		file_spectra = ret.set_spectra_name(Teff_new, np.log10(g_new), Z_new, IDcomp)

		ttt = np.zeros((len(t_rl),3))
		ttt[:,0] = t_rl[:,0]
		ttt[:,1] = int_spectra
		ttt[:,2] = diffs

		np.savetxt(file_spectra + '.txt', ttt)

		plt.figure()

		ax = plt.subplot(111)
		ax.plot(t_rl[:,0],t_rl[:,1], 'r', label = 'Empirical Spectra', linewidth = 0.5)
		ax.plot(t_rl[:,0], int_spectra,'b', label = 'Interpolated Spectra', linewidth = 0.5)
		ax.legend()
		#plt.title('Comparison of Means-Interpolated vs Empirical Spectra for: ' + 
		#	  '$Teff =$ ' + str(Teff_new) + ', $log g =$ ' + str(logg_new) + ', $Z =$ ' + str(Z_new))
		plt.xlabel('Wavelength ($\AA$)')
		plt.ylabel('Flux')

		plt.savefig(file_spectra + '.png')
		#plt.show()

		#plt.figure()
		#plt.plot(gp,diffs)
		#plt.show()















