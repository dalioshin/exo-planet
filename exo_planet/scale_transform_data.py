import sys
import numpy as np
import pandas as pd
from data_func import load_from_csv

def scale_dist(df) -> pd.DataFrame:
    df["sy_dist"] = df["sy_dist"] / df["sy_dist"].max() * 100
    return df

def convert_to_cart(df) -> pd.DataFrame:
    df["x"] = df["sy_dist"] * np.sin(df["dec"]) * np.cos(df["ra"])
    df["y"]  = df["sy_dist"] * np.sin(df["dec"]) * np.sin(df["ra"])
    df["z"]  = df["sy_dist"] * np.cos(df["dec"])
    return df


def main():
    if len(sys.argv) != 2:
        print("provide a filename")
        sys.exit(1)

    df = load_from_csv(sys.argv[1])

    # pull spec columns from df and scale distance
    df_location_only = df[["ra", "dec", "sy_dist", "pl_rade"]]
    df_loc_scaled = scale_dist(df_location_only)
    
    # convert polar to cartesian coords
    df_scaled_cart = convert_to_cart(df_loc_scaled)
    
    # output new csv for blender consumption
    df_scaled_cart.dropna(inplace=True)
    df_scaled_cart.to_csv('scaled_cart_data.csv', index=False)


if __name__ == "__main__":
    main()
