import pandas as pd
import os

def load_data():
    path = os.path.join(os.path.dirname(__file__), "../data/runway_data.csv")
    df = pd.read_csv(path, parse_dates=["timestamp"])
    return df
