import re

import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from fontTools.varLib.interpolatableHelpers import rot_list

ratings = pd.read_csv('data/raw/csv/rojstva_zakonske_zveze.csv', encoding="UTF-8")

def izvleci_stevilko(v):
    if pd.isna(v): return 0.0
    s = re.sub(r'[^\d,.]', '', str(v))
    if not s: return 0.0

    if '.' in s and ',' in s: s = s.replace('.', '').replace(',', '.')
    elif '.' in s and len(s.split('.')[-1]) == 3: s = s.replace('.', '')
    else: s = s.replace(',', '.')

    try: return float(s)
    except: return 0.0


print(ratings.head(100))