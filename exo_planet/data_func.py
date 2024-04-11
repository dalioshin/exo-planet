import pandas as pd

def load_from_csv(filename: str) -> pd.DataFrame:
    if not filename.lower().endswith("csv"):
        raise ValueError("{} is not a csv file", filename)
    
    return pd.read_csv(filename, sep=",")