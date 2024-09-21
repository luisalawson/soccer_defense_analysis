import pandas as pd
import json

def load_data(file_path):
    return pd.read_csv(file_path, delimiter=';')
