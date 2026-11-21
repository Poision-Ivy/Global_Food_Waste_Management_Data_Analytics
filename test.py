import numpy as np
import pandas as pd
print(np.__version__)
print(pd.__version__)
df=pd.read_csv('global_food_wastage_dataset.csv')
print(df.head(10))