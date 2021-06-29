# %%
import pandas as pd
import plotly.express as px
from src.wrapper import create_data, simulate, read_accuracy, anonimize, utility
# %% [markdown]
#  ## 1. rész
#  - Több féle perturbáció
#  - 1 féle deanonimizáció
#  - accuracy mennyi
#  - scoreboard

# %%
# háttérismeret és anonimizálandó adat generálása
# Erős támadó
print("Háttérismeret generálása...\n")
create_data('enron', 2000, 'első_próba', 1, 'ns09', 0.5, 0.75, verbose=True)

# %%
# Deanonimizáció
# megfigyelhetjük, hogy itt jelentősen sikeresebb a deanon, mikor jobb a háttérismeret
print("Deanonimizációs algoritmus futtatása\n")
simulate('enron', 2000, 'első_próba', 'ns09', 'random.25', 50, 0.01, verbose=True)

# %%
# Tamadás eredényessége
TPR, _, FPR, _ = read_accuracy('enron', 2000, 'első_próba', 'ns09')['avg']
print('True positive rate: {:.2f}\nFalse positive rate: {:.2f}'.format(TPR, FPR))

# %%
print('Gyenge támadó modell futtatása')
create_data('enron', -1, 'gyenge', 1, 'ns09', 0.25, 0.5)
simulate('enron', -1, 'gyenge', 'ns09', 'random.25', 1000, 0.01)

print('Közepes támadó modell futtatása')
create_data('enron', -1, 'kozep', 1, 'ns09', 0.5, 0.75)
simulate('enron', -1, 'kozep', 'ns09', 'random.25', 1000, 0.01)

print('Erős támadó modell futtatása')
create_data('enron', -1, 'eros', 1, 'ns09', 0.7, 0.9)
simulate('enron', -1, 'eros', 'ns09', 'random.25', 1000, 0.01)

print('Eredmények beolvasása')
df = pd.DataFrame(columns=['experiment', 'deanon', 'TPR', 'FPR'])

for experiment in ['eros', 'kozep', 'gyenge']:
	TPR, _, FPR, _ = read_accuracy('enron', -1, experiment, 'ns09')['avg']
	df = df.append({'experiment':experiment, 'deanon':'ns09 (theta=0.01)', 'TPR':TPR, 'FPR':FPR}, ignore_index=True)
df

# %% [markdown]
#  ## 2. rész
#  - egy perturb
#  - több deanon összehasonlítása (nar, blb, KL)
#  - accuracy mennyi
#  - scoreboard

# %%
# paraméterek
experiment = 'eros'
network = 'enron'
size = -1

params = {
    'ns09': 0.01,
    'blb': '0.01,0.5',
    'KL': 100
}
# %%
# Három deanon algoritmus (ki lehet fejteni szövegesen)
# ns09-et már korábban lefuttattuk
# print('ns09 deanonimizáció futtatása')
# simulate(network, size, experiment, 'ns09', 'random.25', 1000, 0.01, verbose=True)
# ez a blb, mit tud?
# %%
print('blb deanonimizáció futtatása')
simulate(network, size, experiment, 'blb', 'random.25', 1000, params['blb'], verbose=True)
# %%
print('KL deanonimizáció futtatása')
simulate(network, size, experiment, 'KL', 'random.25', 1000, params['KL'], verbose=True)

# %%
print('pontosságok beolvasása')
df = pd.DataFrame(columns=['experiment', 'deanon', 'TPR', 'FPR'])
for deanon in ['ns09', 'blb', 'KL']:
	TPR, _, FPR, _ = read_accuracy(network, size, experiment, deanon)['avg']
	df = df.append({'experiment':experiment, 'deanon':deanon+' ('+str(params[deanon])+')', 'TPR':TPR, 'FPR':FPR}, ignore_index=True)
df
# %% [markdown]
# 3. rész
# 1 perturn, 3 anon, 1 deanon, utility measure

# %%
# paraméterek
experiment = 'eros'
deanon = 'ns09'
network = 'enron'
size = -1

print("Háttérismeret generálása")
create_data(network, size, experiment, 1, 'ns09', 0.7, 0.9, verbose=True)

# define parameters
params = {
    'sw': 0.1,
    'kda': 50,
    'dp': 50
}

# results will be sroted in this df
df = pd.DataFrame(columns=['experiment', 'anon', 'deanon', 'TPR', 'FPR', 'utility'])

for anon in ['none', 'sw', 'kda', 'dp']:
    # anonimize graph
    if anon != 'none':
        print("Anonimizálás {} módszerrel".format(anon))
        anonimize(network, size, experiment, anon, params[anon])

    # calculate utility loss
    util = utility(network, size, experiment, 'lcc')

    # run deanon algo
    simulate(network, size, experiment, deanon, 'random.25', 1000, 0.01)

    # calculate results
    TPR, _, FPR, _ = read_accuracy(network, size, experiment, deanon)['avg']
    df = df.append({'experiment':experiment, 'anon':anon+' ('+str(params[anon])+')', 'deanon':deanon+' (0.01)', 'TPR':TPR, 'FPR':FPR, 'utility':util}, ignore_index=True)
print("Eredmények értékelése")
df

# %% [markdown]
# 4. rész
# - 1 perturb
# - 3 anon
# - 3 deanon
# - scoreboard
# utility
# %%
# paraméterek
network = 'enron'
size = -1
nseed = 1000 

# %%
# define parameters
params = {
    # anon
    'sw': 0.1,
    'kda': 50,
    'dp': 50,
    # deanon
    'ns09': 0.01,
    'blb': '0.01,0.5',
    # util
    'inf': 5
}

# Háttérismeret generálása
print('Gyenge támadó feltételezve')
create_data(network, size, "gyenge", 1, 'ns09', 0.25, 0.5)

print('Erős támadó feltételezve')
create_data(network, size, "eros", 1, 'ns09', 0.7, 0.9)

# eredmények gyűjtéséhez létrehozott táblázat
df = df_util = pd.DataFrame(columns=['experiment', 'anon', 'deanon', 'TPR', 'FPR'])

# Egyes kombilációk futtatása
for experiment in ['gyenge', 'eros']:
    print('\n'+experiment)
    for anon in ['none', 'sw', 'kda', 'dp']:
        print(anon)
        # anonimize graph
        if (anon != 'none'):
            anonimize(network, size, experiment, anon, params[anon])
        
            # calculate utility loss for anonimization method
            # for util in ['inf', 'deg', 'lcc']:
            #     param = params.get(util, None)
            #     value = utility(network, size, experiment, util, param)
            #     df_util = df_util.append({'anon':anon, 'value':value, 'util': util}, ignore_index=True)

        for deanon in ['ns09', 'blb']:
            print('\t'+deanon)
            # run deanon algos
            simulate(network, size, experiment, deanon, 'random.25', nseed, params[deanon])
            # calculate results
            TPR, _, FPR, _ = read_accuracy(network, size, experiment, deanon)['avg']
            df = df.append({'experiment':experiment, 'anon':anon+' ('+str(params[anon])+')', 'deanon':deanon+' ('+str(params[deanon])+')', 'TPR':TPR, 'FPR':FPR}, ignore_index=True)
df

# %%
# Scoreborad
data = df[df['experiment']=='gyenge']
fig = px.scatter(data, x='FPR', y='TPR', 
    color='deanon',
    symbol='anon',
    range_y=[0,100],
    labels={
        "FPR": "Incorrect matches (FPR)",
        "TPR": "Correct matches (TPR)",
    },
    title="Gyenge támadó modellt feltételezve")
fig.show()
# %%
# Scoreborad
data = df[df['experiment']=='eros']
fig = px.scatter(data, x='FPR', y='TPR', 
    color='deanon',
    symbol='anon',
    range_y=[0,100],
    labels={
        "FPR": "Incorrect matches (FPR)",
        "TPR": "Correct matches (TPR)",
    },
    title="Erős támadó modellt feltételezve")
fig.show()
# %%
# # Change the default stacking
# fig = px.bar(df_util, x="anon", y="value",
#     color='util', 
#     barmode='group',
#     labels={
#         "util": "Utility",
#         "anon": "Anonimization technique",
#     },
#     title="Utility loss for each technique")
# fig.show()

# # %%