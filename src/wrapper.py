import os
import time
import csv
from subprocess import Popen, PIPE

def _run_command(program, function, *args, verbose=True):
    command = None
    if program == 'SEC':
        command = ['java', '-jar', 'libs/secGraphCLI.jar']
    elif program == 'SAL':
        command = ['java', '-cp', 'bin/:libs/*', 'SAL']
    elif program == 'copy':
        command = ['cp']
    else:
        raise Exception("Command not supported!")

    # extend list with function name and function parameters (in string format)
    args = [str(x) for x in args]
    command.extend([function, *args])

    # run program with commands
    p = Popen(command, stdout=PIPE)
    output = []
    for bytes in iter(p.stdout.readline, b''):
        message = bytes.decode()
        output.append(message)
        if verbose:
            print(message)
    return output

# generate file paths
def _get_paths(network_name, size, experiment_id):
    # TODO does this work on windows?
    curr_dir = os.getcwd() 
    size_string = ''
    if (size != -1):
        size_string = str(float(size)/1000)+'k_'
    input_file = "{}/output/{}_{}{}/SimuData/e0_v0_tar_orig.tgf".format(curr_dir, network_name, size_string, experiment_id)
    output_file = "{}/output/{}_{}{}/SimuData/e0_v0_tar.tgf".format(curr_dir, network_name, size_string, experiment_id)
    return input_file, output_file

# SALAB FUNCTIONS
def create_data(network_name, size, experiment_id, n_exports, perturb_algo, n_perturbs, alpha_v, alpha_e):
    _run_command('SAL', 'create_data', network_name, size, experiment_id, n_exports, perturb_algo, n_perturbs, alpha_e, alpha_v)
    # create backup file
    input_file, output_file = _get_paths(network_name, size, experiment_id)
    _run_command('copy', output_file, input_file)

def simulate(network_name, size, experiment_id, deanon_algo, n_rounds, seed_type, seed_size, deanon_params):
    _run_command('SAL', 'simulate', network_name, size, experiment_id, deanon_algo, n_rounds, seed_type, seed_size, deanon_params)

def analyze(network_name, size, experiment_id, deanon_algo, verbose=True):
    _run_command('SAL', 'analyze', network_name, size, experiment_id, deanon_algo, 'no_lta')

def export(src_net, tar_net, exp_size):
    _run_command('SAL', 'export', src_net, tar_net, exp_size)

def measure(src_net, measure):
    _run_command('SAL', 'measure', src_net, measure)

def summarize(net):
    _run_command('SAL', 'summarize', net)

# read output values after running analyze
def read_accuracy(network_name, size, experiment_id, deanon_algo):
    # delete previous result
    size_string = ''
    if (size != -1):
        size_string = str(float(size)/1000)+'k_'
    path = './output/{}_{}{}/{}/accuracy.csv'.format(network_name, size_string,experiment_id, deanon_algo) 
    if os.path.exists(path):
        os.remove(path)
    # run analyze
    _run_command('SAL', 'analyze', network_name, size, experiment_id, deanon_algo, 'no_lta', verbose=False)
    # wait for script to finish
    time.sleep(1)
    lines = {}
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            name = row[0]
            vals = [float(x) for x in row[1:]]
            lines[name] = vals
    return lines

# SECGRAPH FUNCTIONS
# remove id -> useless

# def id_removal(network_name, experiment_id):
#     input_file, output_file = _get_paths(network_name, experiment_id)
#     _run_command('SEC', '-m', 'a', '-a', 'id', '-gA', input_file, '-gO', output_file)

def anonimize(network_name, size, experiment_id, algo, *params):
    input_file, output_file = _get_paths(network_name, size, experiment_id)
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
    input_file, output_file = _get_paths(network_name, size, experiment_id)
    _run_command('SEC', '-m', 'a', '-a', 'sw', '-gA', input_file, '-gO', output_file, '-f', ratio)

def sala_DP(network_name, size, experiment_id, epsilon):  # aka. Pygmalion
    input_file, output_file = _get_paths(network_name, size, experiment_id)
    _run_command('SEC', '-m', 'a', '-a', 'salaDP', '-gA', input_file, '-gO', output_file, '-e', epsilon)

def kDa(network_name, size, experiment_id, k):
    input_file, output_file = _get_paths(network_name, size, experiment_id)
    _run_command('SEC', '-m', 'a', '-a', 'kDa', '-gA', input_file, '-gO', output_file, '-k', k)

## DEANON ALGOS
# NS09, BLB supported by SALab

# TODO
# def deanon_dv():

## UTILITY FUNCTIONS

def utility(network_name, size, experiment_id, metric, param=None):
    input_file, output_file = _get_paths(network_name, size, experiment_id)
    f = None
    if (metric == 'deg'):
        f = util_deg
    elif (metric == 'lcc'):
        f = util_LCC
    elif (metric == 'inf'):
        f = util_infect

    if (f is not None):
        return f(network_name, size, experiment_id, param)
    else:
        raise Exception('Utility algorythm not suppored!')

def util_deg(network_name, size, experiment_id, param):
    input_file, output_file = _get_paths(network_name, size, experiment_id)
    message = _run_command('SEC', '-m', 'u', '-a', 'deg', '-gA', output_file, '-gB', input_file, verbose=False)[0]
    return float(message.replace('\n', ''))

def util_LCC(network_name, size, experiment_id, param):
    input_file, output_file = _get_paths(network_name, size, experiment_id)
    message = _run_command('SEC', '-m', 'u', '-a', 'LCC', '-gA', output_file, '-gB', input_file, verbose=False)[0]
    return float(message.replace('\n', ''))

def util_infect(network_name, size, experiment_id, param):
    if param is not None:
        nInf = param
    else:
        raise Exception('Util infect parameter needed')
    input_file, output_file = _get_paths(network_name, size, experiment_id)
    message =_run_command('SEC', '-m', 'u', '-a', 'Infec', '-gA', output_file, '-gB', input_file, '-nInf', nInf, verbose=False)[0]
    return float(message.replace('\n', ''))
