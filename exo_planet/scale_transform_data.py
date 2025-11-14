import argparse
import numpy as np
import pandas as pd
try:
    from .data_func import load_from_csv, save_to_csv, pull_from_astro_api
except ImportError:
    # For script execution
    from data_func import load_from_csv, save_to_csv, pull_from_astro_api

SCALE_FACTOR_CONST = 70000

def linear_scale(df, col, scaler=1) -> pd.DataFrame:
    df = df.copy()
    df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min()) * scaler
    return df

def convert_to_cart(df) -> pd.DataFrame:
    df = df.copy()
    df["x"] = df["sy_dist"] * np.cos(np.deg2rad(df["dec"])) * np.cos(np.deg2rad(df["ra"]))
    df["y"] = df["sy_dist"] * np.cos(np.deg2rad(df["dec"])) * np.sin(np.deg2rad(df["ra"]))
    df["z"] = df["sy_dist"] * np.sin(np.deg2rad(df["dec"]))
    return df

def convert_scale_clean_df(input_df: pd.DataFrame) -> pd.DataFrame:
    # ensure working with only required columns from df
    df_filtered = input_df[["ra", "dec", "sy_dist", "pl_rade", "st_rad", "st_teff"]].copy()

    # delete dup planets around same star
    df_filtered.dropna(inplace=True)
    df_filtered.drop_duplicates(subset=["sy_dist"], inplace=True)

    # convert polar to cartesian coords
    df_scaled = linear_scale(df_filtered, "sy_dist", SCALE_FACTOR_CONST)
    df_scaled_cart = convert_to_cart(df_scaled)

    # scale greater than 10 radius by log (some stars are so massive, taking artistic liberty for visualization)
    df_scaled_cart["st_rad"] = np.log(df_scaled_cart["st_rad"])

    # after normalizing radius, rescale to look good in scene
    df_scaled_cart = linear_scale(df_scaled_cart, "st_rad", 3)

    return df_scaled_cart

def generate_from_local_csv(input_csv_filename: str, output_csv: str) -> None:
    df = load_from_csv(input_csv_filename)
    df_scaled_cart = convert_scale_clean_df(df)
    # output new csv for blender consumption
    save_to_csv(df_scaled_cart, output_csv)

def generate_from_api(output_csv: str) -> None:
    column_list = ["ra", "dec", "sy_dist", "pl_rade", "st_rad", "st_teff"]
    table = "ps"
    df = pull_from_astro_api(table, column_list)
    df_scaled_cart = convert_scale_clean_df(df)
    # output new csv for blender consumption
    save_to_csv(df_scaled_cart, output_csv)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate scaled exoplanet data for visualization")
    subparsers = parser.add_subparsers(dest="command", help="available commands")
    # Parser for local CSV input file
    parser_local = subparsers.add_parser("local", help="Generate scaled data from local CSV file")
    parser_local.add_argument("input_csv", type=str, help="Input CSV filename")
    parser_local.add_argument("output_csv", type=str, help="Output CSV filename")
    # Parser for API data 
    parser_api = subparsers.add_parser("api", help="Generate scaled data from astroquery API")
    parser_api.add_argument("output_csv", type=str, help="Output CSV filename")

    # parse args and call appropriate function
    args = parser.parse_args()
    if args.command == "local":
        generate_from_local_csv(args.input_csv, args.output_csv)
        print(f"Generated CSV from local data ready for blender at {args.output_csv}")
    elif args.command == "api":
        generate_from_api(args.output_csv)
        print(f"Generated CSV from API data ready for blender at {args.output_csv}")
    else:
        parser.print_help()