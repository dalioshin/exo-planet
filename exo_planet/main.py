import sys
from data_func import load_from_csv
from graphical_func import plot_data_contor

def main():
    if len(sys.argv) != 2:
        print("provide a filename")
        sys.exit(1)

    df = load_from_csv(sys.argv[1])
    print(df.columns)
    plot_data_contor(df.sample(frac=0.01))

    # df.plot.scatter(x="pl_rade", y="pl_eqt")



if __name__ == "__main__":
    main()
