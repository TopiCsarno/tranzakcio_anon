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
create_data('enron', 2000, 'exp1', 1, 'ns09', 1, 0.8, 0.8)
create_data('enron', 2000, 'exp2', 1, 'ns09', 1, 0.5, 0.75)
create_data('enron', 2000, 'exp3', 1, 'ns09', 1, 0.4, 0.6)

# %%
# Deanonimizáció
# megfigyelhetjük, hogy itt jelentősen sikeresebb a deanon, mikor jobb a háttérismeret
simulate('enron', 2000, 'exp1', 'ns09', 1, 'random.25', 50, 0.01)
simulate('enron', 2000, 'exp2', 'ns09', 1, 'random.25', 50, 0.01)
simulate('enron', 2000, 'exp3', 'ns09', 1, 'random.25', 50, 0.01)

# %%
# Pontosságok beolvasása
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
create_data(network, size, experiment, 1, 'sample', 1, 1, 0.95)

# %%
# ez az ns09 algo
simulate(network, size, experiment, 'ns09', 1, 'random.25', 50, 0.01)
# ez a blb, mit tud?
# %%
simulate(network, size, experiment, 'blb', 1, 'random.25', 50, '0.1,0.5')
# %%
# ez a grh (TODO) -> KL implement
simulate(network, size, experiment, 'grh', 1, 'random.25', 50, 0.1)
# %%
# add new data
df = pd.DataFrame(columns=['experiment', 'anon', 'deanon', 'TPR', 'FPR'])
for deanon in ['ns09', 'blb', 'grh']:
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
create_data(network, size, experiment, 1, 'ns09', 1, 0.5, 0.75)
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
    simulate(network, size, experiment, deanon, 1, 'random.25', 50, 0.01)

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
size = 2000
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
    'grh': 0.1,
    'blb': '0.1,0.5',
    # util
    'inf': 5
}

# adott háttérismeret
create_data(network, size, experiment, 1, 'ns09', 1, 0.5, 0.75)

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

    for deanon in ['ns09', 'grh', 'blb']:
        # run deanon algos
        simulate(network, size, experiment, deanon, 1, 'random.25', nseed, params[deanon])
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

# %%

# %%
