import pandas as pd
from astroquery.ipac.irsa import Irsa
from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive

def load_from_csv(filename: str) -> pd.DataFrame:
    if not filename.lower().endswith("csv"):
        raise ValueError("{} is not a csv file", filename)
    
    return pd.read_csv(filename, sep=",")

def save_to_csv(df: pd.DataFrame, filename: str) -> None:
    if filename.lower().endswith("csv"):
        df.to_csv(filename, index=False)
    else:
        df.to_csv(filename + ".csv", index=False)

def pull_from_astro_api(table: str, column_list: list) -> pd.DataFrame:
    """Pull data from astroquery API and return as pandas DataFrame."""
    result = NasaExoplanetArchive.query_criteria(table=table, select=f"{','.join(column_list)}")
    return result.to_pandas()