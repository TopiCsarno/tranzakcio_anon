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
create_data('enron', 2000, 'exp1', 1, 'ns09', 0.8, 0.8, verbose=True)

# %%
# Deanonimizáció
# megfigyelhetjük, hogy itt jelentősen sikeresebb a deanon, mikor jobb a háttérismeret
print("Deanonimizációs algoritmus futtatása\n")
simulate('enron', 2000, 'exp1', 'ns09', 'random.25', 50, 0.01, verbose=True)

# %%
# Tamadás eredényessége
TPR, _, FPR, _ = read_accuracy('enron', 2000, 'exp1', 'ns09')['avg']
print('True positive rate: {:.2f}\nFalse positive rate: {:.2f}'.format(TPR, FPR))

# %%
print('Közepes támadó modell futtatása')
create_data('enron', 2000, 'exp2', 1, 'ns09', 0.5, 0.75)
simulate('enron', 2000, 'exp2', 'ns09', 'random.25', 50, 0.01)

print('Gyenge támadó modell futtatása')
create_data('enron', 2000, 'exp3', 1, 'ns09', 0.4, 0.6)
simulate('enron', 2000, 'exp3', 'ns09', 'random.25', 50, 0.01)

print('Eredmények beolvasása')
df = pd.DataFrame(columns=['experiment', 'deanon', 'TPR', 'FPR'])
for i in range(3):
	experiment = 'exp'+str(i+1)
	TPR, _, FPR, _ = read_accuracy('enron', 2000, experiment, 'ns09')['avg']
	df = df.append({'experiment':experiment, 'deanon':'ns09', 'TPR':TPR, 'FPR':FPR}, ignore_index=True)
df

# %%
# Eredmények ábrázolása a score boardon
fig = px.scatter(df, x='FPR', y='TPR', 
    color='experiment', 
    range_y=[0,100],
    labels={
        "FPR": "Incorrect matches (FPR)",
        "TPR": "Correct matches (TPR)",
    },
    title="Scoreboard: Correct vs Incorrect matches")
fig.show()

# %% [markdown]
#  ## 2. rész
#  - egy perturb
#  - több deanon összehasonlítása (nar, blb, grh, KL, DV?)
#  - accuracy mennyi
#  - scoreboard

# %%
# paraméterek
experiment = '2_exp'
network = 'enron'
size = 3000

# %%
# újatt háttérismeret generálása
create_data(network,size,experiment, 1, 'ns09', 0.8, 0.8, verbose=True)

# %%

# Három deanon algoritmus (ki lehet fejteni szövegesen)

print('ez az ns09 algo')
simulate(network, size, experiment, 'ns09', 'random.25', 50, 0.01)
# ez a blb, mit tud?
# %%
print('ez az blb algo')
simulate(network, size, experiment, 'blb', 'random.25', 50, '0.1,0.5')
# %%
print('ez az kl algo')
simulate(network, size, experiment, 'KL', 'random.25', 50, 50)

# %%
# pontosságok beolvasása
df = pd.DataFrame(columns=['experiment', 'anon', 'deanon', 'TPR', 'FPR'])
for deanon in ['ns09', 'blb', 'KL']:
	TPR, _, FPR, _ = read_accuracy(network, size, experiment, deanon)['avg']
	df = df.append({'experiment':experiment, 'anon':'none', 'deanon':deanon, 'TPR':TPR, 'FPR':FPR}, ignore_index=True)
df
# %%
fig = px.scatter(df, x='FPR', y='TPR', 
    symbol='deanon', 
    range_y=[0,100],
    labels={
        "FPR": "Incorrect matches (FPR)",
        "TPR": "Correct matches (TPR)",
    },
    title="Scoreboard: Correct vs Incorrect matches")
fig.show()
# %% [markdown]
# 3. rész
# 1 perturn, 3 anon, 1 deanon, utility measure

# %%
# paraméterek
experiment = '3_exp'
deanon = 'ns09'
network = 'wiki'
size = 2000
# %%
create_data(network, size, experiment, 1, 'ns09', 0.5, 0.75)
# %%
# define parameters
params = {
    'sw': 0.1,
    'kda': 50,
    'dp': 50
}

# results will be sroted in this df
df = pd.DataFrame(columns=['experiment', 'anon', 'deanon', 'TPR', 'FPR', 'utility'])

for anon in ['sw', 'kda', 'dp']:
    # anonimize graph
    anonimize(network, size, experiment, anon, params[anon])
    
    # calculate utility loss
    util = utility(network, size, experiment, 'lcc')

    # run deanon algo
    simulate(network, size, experiment, deanon, 'random.25', 50, 0.01)

    # calculate results
    TPR, _, FPR, _ = read_accuracy(network, size, experiment, deanon)['avg']
    df = df.append({'experiment':experiment, 'anon':anon, 'deanon':deanon, 'TPR':TPR, 'FPR':FPR, 'utility':util}, ignore_index=True)

df

# %%
fig = px.scatter(df, x='FPR', y='TPR', 
    color='anon',
    range_y=[0,100],
    labels={
        "FPR": "Incorrect matches (FPR)",
        "TPR": "Correct matches (TPR)",
    },
    title="Scoreboard: Correct vs Incorrect matches")
fig.show()
# %% [markdown]
# 4. rész
# - 1 perturb
# - 3 anon
# - 3 deanon
# - scoreboard
# utility
# %%
# paraméterek
experiment = '4_exp'
network = 'wiki'
size = 1000
nseed = 50

# %%
# define parameters
params = {
    # anon
    'sw': 0.1,
    'kda': 50,
    'dp': 50,
    # deanon
    'ns09': 0.01,
    'KL': 50,
    'blb': '0.1,0.5',
    # util
    'inf': 5
}

# adott háttérismeret
create_data(network, size, experiment, 'ns09', 1, 0.5, 0.75)

# results will be sroted in this df
df = df_util = pd.DataFrame()

for anon in ['sw', 'kda', 'dp']:
    # anonimize graph
    anonimize(network, size, experiment, anon, params[anon])
    
    # calculate utility loss for anonimization method
    for util in ['inf', 'deg', 'lcc']:
        param = params.get(util, None)
        value = utility(network, size, experiment, util, param)
        df_util = df_util.append({'anon':anon, 'value':value, 'util': util}, ignore_index=True)

    for deanon in ['ns09', 'KL', 'blb']:
        # run deanon algos
        simulate(network, size, experiment, deanon, 'random.25', nseed, params[deanon])
        # calculate results
        TPR, _, FPR, _ = read_accuracy(network, size, experiment, deanon)['avg']
        df = df.append({'experiment':experiment, 'anon':anon, 'deanon':deanon, 'TPR':TPR, 'FPR':FPR}, ignore_index=True)
df

# %%
# Scoreborad
fig = px.scatter(df, x='FPR', y='TPR', 
    color='deanon',
    symbol='anon',
    range_y=[0,100],
    labels={
        "FPR": "Incorrect matches (FPR)",
        "TPR": "Correct matches (TPR)",
    },
    title="Scoreboard: Correct vs Incorrect matches")
fig.show()
# %%
# Change the default stacking
fig = px.bar(df_util, x="anon", y="value",
    color='util', 
    barmode='group',
    labels={
        "util": "Utility",
        "anon": "Anonimization technique",
    },
    title="Utility loss for each technique")
fig.show()

# %%