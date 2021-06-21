# %%

import pandas as pd
import plotly.express as px

from src.wrapper import create_data, simulate, read_accuracy, anonimize, utility, accurarcy_KL

# %%
create_data('wiki', 1000, 'exp1', 1, 'ns09', 1, 0.8, 0.8)

# %%
simulate('wiki', 1000, 'exp1', 'ns09', 1, 'random.25', 50, 0.01)
# %%
anonimize('wiki', 1000, 'exp1', 'kda', 50)
# %%
simulate('wiki', 1000, 'exp1', 'KL', 1, 'random.25', 50, 100)
# %%
read_accuracy('wiki', 1000, 'exp1', 'ns09')
# %%
read_accuracy('wiki', 1000, 'exp1', 'KL')['avg']

# %%
