# %%
import sys
import os
import networkx as nx


# def simulate(network_name, size, experiment_id, deanon_algo, n_rounds, seed_type, seed_size, deanon_params):
network_name = 'enron'
size = 2000
experiment_id = 'exp1'
params = '50'

size_string = ''
if (size != -1):
	size_string = str(float(size)/1000)+'k_'

data_dir = './output/'+network_name+'_'+size_string+experiment_id+'/SimuData/'
exp_dir = './output/'+network_name+'_'+size_string+experiment_id+'/KL_'+params+'/'
seed_dir = './output/'+network_name+'_'+size_string+experiment_id+'/ns09/Seeds/'

if not os.path.exists(exp_dir):
	os.mkdir(exp_dir)

# %%
if os.path.exists(seed_dir):
	if not os.path.exists(seed_dir + '/e0_v0_seedmap.txt'):
		f = open(seed_dir + '/e0_v0.txt', 'r')
		f2 = open(seed_dir + '/e0_v0_seedmap.txt', 'w+')
		seeds = [int(x) for x in f.readline().replace('\n', '').replace('\r', '').replace('[', '').replace(']', '').split(', ')]
		for seed in seeds:
			f2.write(str(seed) + " " + str(seed) + "\n")
		f.close()
		f2.close()
else:
	raise Exception('Seeds directory missing!')

# %%
# print('java -cp bin Reconciliation "'+data_dir+'e0_v0_src.tgf" "'+data_dir+'e0_v0_tar.tgf" "'+seed_dir+'e0_v0_seedmap.txt" '+params+' "'+exp_dir+'e0_v0_res.tgf"')
result = os.system('java -cp bin Reconciliation "'+data_dir+'e0_v0_src.tgf" "'+data_dir+'e0_v0_tar.tgf" "'+seed_dir+'e0_v0_seedmap.txt" '+params+' "'+exp_dir+'e0_v0_res.tgf"')

# %%
if not os.path.exists(exp_dir+"/e0_v0_res.tgf"):
	sys.exit(0)

tpc = 0
fpc = 0
f = open(exp_dir+"/e0_v0_res.tgf", "r")
for l in f.readlines():
	if len(l) == 0 or not l[0].isdigit():
		continue

	r = [int(x) for x in l.replace('\n', '').replace('\r', '').split(' ')]
	if r[0] == r[1]:
		tpc += 1
	else:
		fpc += 1
f.close()

g_src = nx.read_edgelist(data_dir+"/e0_v0_src.tgf", nodetype=int).to_undirected()
g_tar = nx.read_edgelist(data_dir+"/e0_v0_tar.tgf", nodetype=int).to_undirected()
Vsrc = set(g_src.nodes())
Vtar = set(g_tar.nodes())
ols = len(Vsrc & Vtar)
tpr = (100 * float(tpc)) / ols
fpr = (100 * float(fpc)) / ols

print("KL_%s: TPR = %.2f %%, FPR = %.2f %%" % (params, tpr, fpr))

# %%
