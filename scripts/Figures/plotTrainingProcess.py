import os
import sys
import numpy as np
from scipy.stats import pearsonr, spearmanr

def read_dataset_description(dataset_description_dir, dataset_description_filename):
	description_path= os.path.join(dataset_description_dir,dataset_description_filename)
	fin = open(description_path, 'r')
	proteins = []
	for line in fin:
		proteins.append(line.split()[0])
	fin.close()

	decoys = {}
	for protein in proteins:
		decoys_description_path = os.path.join(dataset_description_dir,protein+'.dat')
		fin = open(decoys_description_path,'r')
		fin.readline()
		decoys[protein]=[]
		for line in fin:
			sline = line.split()
			decoys[protein].append((sline[0], float(sline[2])))
		fin.close()
	return proteins, decoys

def read_epoch_output(filename):
	loss_function_values = []
	decoys_scores = {}
	f = open(filename, 'r')
	for line in f:
		if line.find('Decoys scores:')!=-1:
			break

	for line in f:
		if line.find('Loss function values:')!=-1:
			break
		a = line.split()
		proteinName = a[0]
		if not (proteinName in decoys_scores):
			decoys_scores[proteinName]={}
		decoys_path = a[1]
		score = float(a[2])
		decoys_scores[proteinName][decoys_path]=score

	for line in f:
		sline = line.split()
		loss_function_values.append( float(sline[1]) )

	return loss_function_values, decoys_scores

def plotFunnels(proteins, decoys, decoys_scores, outputFile):
	from matplotlib import pylab as plt
	import numpy as np
	fig = plt.figure(figsize=(20,20))

	N = len(proteins)
	nrows = int(np.sqrt(N))+1
	ncols = int(N/nrows)
	if nrows*ncols<N: ncols+=1

	from mpl_toolkits.axes_grid1 import Grid
	grid = Grid(fig, rect=111, nrows_ncols=(nrows,ncols),
	            axes_pad=0.25, label_mode='L',share_x=False,share_y=False)
	
	for n,protein in enumerate(proteins):
		tmscores = []
		scores = []
		for decoy in decoys[protein]:
			tmscores.append(decoy[1])
			scores.append(decoys_scores[protein][decoy[0]])
			
		grid[n].plot(tmscores,scores,'.')
		
		plt.xlim(-0.1, max(tmscores)+1)
		plt.ylim(min(scores)-1, max(scores)+1)
		
		grid[n].set_title(protein)
	
	#plt.tight_layout()
	plt.savefig(outputFile)

def get_kendall(proteins, decoys, decoys_scores):
	import scipy
	tau_av = 0.0
	for n,protein in enumerate(proteins):
		tmscores = []
		scores = []
		for decoy in decoys[protein]:
			tmscores.append(decoy[1])
			# print protein, decoy[0], decoy[1], decoys_scores[protein][decoy[0]]
			scores.append(decoys_scores[protein][decoy[0]])
			
		tau_prot = scipy.stats.kendalltau(tmscores, scores)[0]
		if tau_prot!=tau_prot:
			tau_prot = 0.0		
		tau_av += tau_prot
	return tau_av/len(proteins)

def get_pearson(proteins, decoys, decoys_scores):
	import scipy
	pearson_av = 0.0
	for n,protein in enumerate(proteins):
		tmscores = []
		scores = []
		for decoy in decoys[protein]:
			tmscores.append(decoy[1])
			# print protein, decoy[0], decoy[1], decoys_scores[protein][decoy[0]]
			scores.append(decoys_scores[protein][decoy[0]])
			
		pearson_prot = scipy.stats.pearsonr(tmscores, scores)[0]
		pearson_av += pearson_prot
	return pearson_av/len(proteins)
	

def plot_loss_function(loss_function_values, outputFile):
	from matplotlib import pylab as plt
	import numpy as np
	fig = plt.figure(figsize=(20,20))
	plt.plot(loss_function_values)
	plt.savefig(outputFile)



def plot_validation_funnels(experiment_name, model_name, dataset_name, epoch_start=0, epoch_end=100):
	print 'Loading dataset'
	proteins, decoys = read_dataset_description('/home/lupoglaz/ProteinsDataset/%s/Description'%dataset_name,'validation_set.dat')
	
	for epoch in range(epoch_start, epoch_end+1):
		#print 'Loading scoring ',epoch
		input_path = '../../models/%s_%s_%s/validation/epoch_%d.dat'%(experiment_name, model_name, dataset_name, epoch)
		output_path = '../../models/%s_%s_%s/epoch%d_funnels.png'%(experiment_name, model_name, dataset_name, epoch)
		if os.path.exists(input_path) and (not os.path.exists(output_path)):
			loss_function_values, decoys_scores = read_epoch_output(input_path)
			print 'Plotting funnels ',epoch
			plotFunnels(proteins, decoys, decoys_scores, output_path)

def plot_validation_correlations(experiment_name, model_name, dataset_name, epoch_start=0, epoch_end=100):
	print 'Loading dataset'
	proteins, decoys = read_dataset_description('/home/lupoglaz/ProteinsDataset/%s/Description'%dataset_name,'validation_set.dat')
	epochs = []
	taus = []
	pearsons = []
	for epoch in range(epoch_start, epoch_end+1):
		#print 'Loading scoring ',epoch
		input_path = '../../models/%s_%s_%s/validation/epoch_%d.dat'%(experiment_name, model_name, dataset_name, epoch)
		if os.path.exists(input_path):
			loss_function_values, decoys_scores = read_epoch_output(input_path)
			taus.append(get_kendall(proteins, decoys, decoys_scores))
			pearsons.append(get_pearson(proteins, decoys, decoys_scores))
			epochs.append(epoch)

	from matplotlib import pylab as plt
	fig = plt.figure(figsize=(20,20))
	plt.plot(epochs,taus, 'r')
	plt.plot(epochs,pearsons, 'b')
	plt.savefig('../../models/%s_%s_%s/kendall_validation.png'%(experiment_name, model_name, dataset_name))
	return taus, pearsons

def plot_training_samples(experiment_name, model_name, dataset_name, epoch_start=0, epoch_end=100):
	print 'Loading dataset'
	proteins, decoys = read_dataset_description('/home/lupoglaz/ProteinsDataset/%s/Description'%dataset_name,'training_set.dat')
	epoch = 1
	loss_function_values, decoys_scores = read_epoch_output('../../models/%s_%s_%s/training/epoch_%d.dat'%
			(experiment_name, model_name, dataset_name, epoch))
	tmscores = []
	for n,protein in enumerate(proteins):
		for decoy in decoys[protein]:
			tmscores.append(decoy[1])
	from matplotlib import pylab as plt
	import numpy as np
	fig = plt.figure(figsize=(20,20))
	plt.hist(tmscores)
	plt.savefig('../../models/%s_%s_%s/decoy_sampling.png'%(experiment_name, model_name, dataset_name))
			
		
if __name__=='__main__':
	
	# for n,lr in enumerate([0.0005, 0.0002, 0.00005, 0.00001]):
	# 	exp_name = 'learning_rate_scan_%d'%n
	# 	taus, pears = plot_validation_correlations(exp_name, 'ranking_model_11atomTypes', '3DRobot_set')
	# 	print 'Learning rate = %f'%lr, taus[0], pears[0]
	# 	plot_validation_funnels(exp_name, 'ranking_model_11atomTypes', '3DRobot_set')

	# for n,lr in enumerate([0.1, 0.2, 0.4]):
	# 	exp_name = 'tm_score_threshold_scan_%d'%n
	# 	taus, pears = plot_validation_correlations(exp_name, 'ranking_model_11atomTypes', '3DRobot_set')
	# 	print 'Tm-score threshold = %f'%lr, taus[0], pears[0]
	# 	plot_validation_funnels(exp_name, 'ranking_model_11atomTypes', '3DRobot_set')

	# for n,lr in enumerate([0.00005, 0.0001, 0.001]):
	# 	exp_name = 'l1coef_scan_%d'%n
	# 	taus, pears = plot_validation_correlations(exp_name, 'ranking_model_11atomTypes', '3DRobot_set')
	# 	print 'L1 coef = %f'%lr, taus[0], pears[0]
	# 	plot_validation_funnels(exp_name, 'ranking_model_11atomTypes', '3DRobot_set')

	# exp_name = 'BatchRankingRepeat2'
	# taus, pears = plot_validation_correlations(exp_name, 'ranking_model_11atomTypes', '3DRobot_set', 30, 30)
	# print 'Default: ', taus[0], pears[0]
	# plot_validation_funnels(exp_name, 'ranking_model_11atomTypes', '3DRobot_set', 30, 30)


	exp_name = 'QA'
	taus, pears = plot_validation_correlations(exp_name, 'ranking_model_11atomTypes', 'CASP')
	print 'Default: ', taus[-1], pears[-1]
	plot_validation_funnels(exp_name, 'ranking_model_11atomTypes', 'CASP')