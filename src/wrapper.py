import os
import time
import csv
import networkx as nx
from subprocess import Popen, PIPE

def _run_command(prg, *args, verbose=False):
    # command aliases
    alias = {
        'SEC': 'java -jar libs/secGraphCLI.jar',
        'SAL': 'java -cp bin/:libs/* SAL',
        'KL': 'java -cp bin Reconciliation'
    }
    # concatnate command string
    cmd = alias.get(prg, prg) + ' ' + ' '.join([str(arg) for arg in args])

    # run command using Popen
    p = Popen(cmd, stderr=PIPE, stdout=PIPE, shell=True)
    output, errors = p.communicate()
    if (p.returncode != 0):
        raise Exception("Error:\n" + errors.decode('utf-8'))
    else:
        if (verbose):
            print(output.decode('utf-8'))
        return output.decode('utf-8')

# generate file paths
def _get_paths(network_name, size, experiment_id):
    # TODO does this work on windows?
    curr_dir = os.getcwd() 
    size_string = ''
    if (size != -1):
        size_string = str(float(size)/1000)+'k_'
    base_dir = "{}/output/{}_{}{}/".format(curr_dir, network_name, size_string, experiment_id)
    input_file = "{}/output/{}_{}{}/SimuData/e0_v0_tar_orig.tgf".format(curr_dir, network_name, size_string, experiment_id)
    output_file = "{}/output/{}_{}{}/SimuData/e0_v0_tar.tgf".format(curr_dir, network_name, size_string, experiment_id)
    return input_file, output_file, base_dir

# SALAB FUNCTIONS
def create_data(network_name, size, experiment_id, n_exports, perturb_algo, alpha_v, alpha_e, verbose=False):
    if perturb_algo == 'narpert':
        perturb_algo = 'ns09'
    _run_command('SAL', 'create_data', network_name, size, experiment_id, n_exports, perturb_algo, 1, alpha_e, alpha_v, verbose=verbose)
    # create backup file
    input_file, output_file, _ = _get_paths(network_name, size, experiment_id)
    _run_command('cp', output_file, input_file)

def simulate(network_name, size, experiment_id, deanon_algo, seed_type, seed_size, deanon_params, verbose=False):
    _, _, basedir = _get_paths(network_name, size, experiment_id)
    path = basedir+'SimuData/e0_v0_overlap.cache'
    if os.path.exists(path):
        os.remove(path)
    if deanon_algo == 'KL':
        deanon_KL(network_name, size, experiment_id, deanon_params)
    elif deanon_algo == 'nar':
        _run_command('SAL', 'simulate', network_name, size, experiment_id, 'ns09', 1, seed_type, seed_size, deanon_params, verbose=verbose)
    else:
        _run_command('SAL', 'simulate', network_name, size, experiment_id, deanon_algo, 1, seed_type, seed_size, deanon_params, verbose=verbose)

def analyze(network_name, size, experiment_id, deanon_algo):
    if deanon_algo == 'nar':
        _run_command('SAL', 'analyze', network_name, size, experiment_id, 'ns09', 'no_lta')
    else:
        _run_command('SAL', 'analyze', network_name, size, experiment_id, deanon_algo, 'no_lta')

# SecGraph KL algo implementation
def deanon_KL(network_name, size, experiment_id, deanon_params):
    _, output_file, base_dir = _get_paths(network_name, size, experiment_id)
    input_file = base_dir+'SimuData/e0_v0_src.tgf'
    exp_dir = base_dir+'KL/'
    seed_dir = base_dir+'ns09/Seeds/'

    if not os.path.exists(exp_dir):
        os.mkdir(exp_dir)
     
    # generate seedmap
    if os.path.exists(seed_dir):
        if not os.path.exists(seed_dir + 'e0_v0_seedmap.txt'):
            f = open(seed_dir + 'e0_v0.txt', 'r')
            f2 = open(seed_dir + 'e0_v0_seedmap.txt', 'w+')
            seeds = [int(x) for x in f.readline().replace('\n', '').replace('\r', '').replace('[', '').replace(']', '').split(', ')]
            for seed in seeds:
                f2.write(str(seed) + " " + str(seed) + "\n")
            f.close()
            f2.close()
    else:
        raise Exception('Seeds directory missing!')
    _run_command('KL', input_file, output_file, seed_dir+'e0_v0_seedmap.txt', str(deanon_params), exp_dir+'e0_v0_res.tgf')

def accurarcy_KL(network_name, size, experiment_id):
    _, _, base_dir = _get_paths(network_name, size, experiment_id)
    data_dir = base_dir+'SimuData'
    exp_dir = base_dir+'KL'

    if not os.path.exists(exp_dir+"/e0_v0_res.tgf"):
        raise Exception('KL output not found!')

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

    with open(exp_dir + '/accuracy.csv', 'w+') as f:
        f.write('avg;'+str(tpr)+';-1;'+str(fpr)+';-1')

# read output values after running analyze
def read_accuracy(network_name, size, experiment_id, deanon_algo):

    if deanon_algo == 'nar':
        deanon_algo = 'ns09'
    # delete previous result
    size_string = ''
    if (size != -1):
        size_string = str(float(size)/1000)+'k_'
    path = './output/{}_{}{}/{}/accuracy.csv'.format(network_name, size_string,experiment_id, deanon_algo) 
    if os.path.exists(path):
        os.remove(path)
    # run analyze
    if (deanon_algo == 'KL'):
        accurarcy_KL(network_name, size, experiment_id)
    else:
        _run_command('SAL', 'analyze', network_name, size, experiment_id, deanon_algo, 'no_lta')
        time.sleep(1)
    # wait for script to finish
    lines = {}
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            name = row[0]
            vals = [float(x) for x in row[1:]]
            lines[name] = vals
    return lines

# SECGRAPH FUNCTIONS
def anonimize(network_name, size, experiment_id, algo, *params):
    input_file, output_file, _ = _get_paths(network_name, size, experiment_id)
    f = None
    if (algo == 'sw'):
        f = switch_edge
    elif (algo == 'dp'):
        f = sala_DP
    elif (algo == 'kda'):
        f = kDa

    if (f is not None):
        f(network_name, size, experiment_id, *params)
    else:
        raise Exception('Anonimize algorythm not suppored!')

def switch_edge(network_name, size, experiment_id, ratio):
    input_file, output_file, _ = _get_paths(network_name, size, experiment_id)
    _run_command('SEC', '-m', 'a', '-a', 'sw', '-gA', input_file, '-gO', output_file, '-f', ratio)

def sala_DP(network_name, size, experiment_id, epsilon):  # aka. Pygmalion
    input_file, output_file, _ = _get_paths(network_name, size, experiment_id)
    _run_command('SEC', '-m', 'a', '-a', 'salaDP', '-gA', input_file, '-gO', output_file, '-e', epsilon)

def kDa(network_name, size, experiment_id, k):
    input_file, output_file, _ = _get_paths(network_name, size, experiment_id)
    _run_command('SEC', '-m', 'a', '-a', 'kDa', '-gA', input_file, '-gO', output_file, '-k', k)

## UTILITY FUNCTIONS
def utility(network_name, size, experiment_id, metric, param=None):
    f = None
    if (metric == 'deg'):
        f = util_deg
    elif (metric == 'lcc'):
        f = util_LCC
    elif (metric == 'bc'):
        f = util_BC

    if (f is not None):
        return f(network_name, size, experiment_id, param)
    else:
        raise Exception('Utility algorythm not suppored!')

def util_deg(network_name, size, experiment_id, param):
    input_file, output_file, _ = _get_paths(network_name, size, experiment_id)
    message = _run_command('SEC', '-m', 'u', '-a', 'deg', '-gA', output_file, '-gB', input_file)
    return float(message.replace('\n', ''))

def util_LCC(network_name, size, experiment_id, param):
    input_file, output_file, _ = _get_paths(network_name, size, experiment_id)
    message = _run_command('SEC', '-m', 'u', '-a', 'LCC', '-gA', output_file, '-gB', input_file)
    return float(message.replace('\n', ''))

def util_BC(network_name, size, experiment_id, param):
    input_file, output_file, _ = _get_paths(network_name, size, experiment_id)
    message = _run_command('SEC', '-m', 'u', '-a', 'BC', '-gA', output_file, '-gB', input_file)
    return float(message.replace('\n', ''))
