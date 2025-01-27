import sys
from data_func import load_from_csv
from graphical_func import plot_data_contor

def main():
    if len(sys.argv) != 2:
        print("provide a filename")
        sys.exit(1)

    df = load_from_csv(sys.argv[1])
    print(df.columns)
    
    # plot contor of the sample
    # plot_data_contor(df.sample(frac=0.01))

    # pull spec columns from df and scale distance
    df_location_only = df[["ra", "dec", "sy_dist", "pl_rade"]]
    df_loc_scaled = df_location_only.copy()
    df_loc_scaled["sy_dist"] = df_loc_scaled["sy_dist"] / df_loc_scaled["sy_dist"].max()
    df_loc_scaled.to_csv('scaled_data.csv', index=False)


if __name__ == "__main__":
    main()
