import sys
import numpy as np
import pandas as pd
from data_func import load_from_csv
import matplotlib.pyplot as plt

def linear_scale(df, col, scaler=1) -> pd.DataFrame:
    df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min()) * scaler
    return df

def convert_to_cart(df) -> pd.DataFrame:
    df["x"] = df["sy_dist"] * np.sin(df["dec"]) * np.cos(df["ra"])
    df["y"]  = df["sy_dist"] * np.sin(df["dec"]) * np.sin(df["ra"])
    df["z"]  = df["sy_dist"] * np.cos(df["dec"])
    return df


def main():
    if len(sys.argv) != 3:
        print("provide a input and output filename")
        sys.exit(1)

    df = load_from_csv(sys.argv[1])

    # pull spec columns from df and scale distance
    df_location_only = df[["ra", "dec", "sy_dist", "pl_rade", "st_rad", "st_teff"]]
    df_loc_scaled = linear_scale(df_location_only, "sy_dist", 100000)
    
    # convert polar to cartesian coords
    df_scaled_cart = convert_to_cart(df_loc_scaled)

    # delete dup planets around same star
    df_scaled_cart.dropna(inplace=True)
    df_scaled_cart.drop_duplicates(subset=["sy_dist"], inplace=True)
    print(df_scaled_cart.max())
    print(df_scaled_cart.median())


    # scale greater than 10 radius by log
    df_scaled_cart["st_rad"] = np.log(df_scaled_cart["st_rad"])
    df_scaled_cart["st_rad"].hist()
    plt.show()
    df_scaled_cart = linear_scale(df_scaled_cart, "st_rad", 3)
    df_scaled_cart["st_rad"].hist()
    plt.show()

    # output new csv for blender consumption
    df_scaled_cart.to_csv(sys.argv[2] + ".csv", index=False)


if __name__ == "__main__":
    main()
