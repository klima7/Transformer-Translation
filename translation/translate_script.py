from tqdm import tqdm
import pandas as pd
import numpy as np

from argos import translate


def translate_part(part_path, save_interval=1000):
    data = pd.read_csv(part_path, dtype={'en': 'string', 'pl': 'string'}, na_values=[""])
    for i, row in tqdm(data.iterrows(), total=len(data)):
        if not pd.isna(row['pl']):
            # skip if translation is already done
            continue
        try:
            data.at[i, 'pl'] = translate(row['en'])
        except Exception:
            print('Error while translating', repr(row['en']))
        
        if i % save_interval == 0:
            data.to_csv(part_path, index=False)
            
            
translate_part('../data/en-pl-0.csv')
