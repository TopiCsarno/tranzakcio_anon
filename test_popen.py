from subprocess import Popen, PIPE

# %%
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

# %%
from subprocess import Popen, PIPE
    
command = ['ls', '-ln']

def _run(command, verbose=True):
    p = Popen(command, stdout=PIPE)
    output = []
    for bytes in iter(p.stdout.readline, b''):
        message = bytes.decode()
        output.append(message)
        if verbose:
            print(message)
    return output

# print(command)
_run(command)
# %%
from subprocess import check_output
out = check_output(["ls", "-kek"])
# %%
import subprocess

p = subprocess.Popen("pwd", stdout=subprocess.PIPE)
result = p.communicate()[0]
# %%
result
# %%
from subprocess import Popen, PIPE

def run(cmd):
    p = Popen(cmd, stderr=PIPE, stdout=PIPE, shell=True)
    output, errors = p.communicate()
    return [p.returncode, errors, output]

out = run('ls -kek')
# %%
