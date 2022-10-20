import pandas as pd
import numpy as np
import argparse
import sys
import os


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--i', type=str, help='Input file directory with /')
    parser.add_argument('--o', type=str, help='Output file directory with /')
    return parser.parse_args()

def swap_titles(input, output):
    file_path = input + 'info.json'
    data = pd.read_json(file_path).T
    data["manipulated_title"] = np.random.permutation(data.title)
    data["index"] = np.array(data["graphic"].str[11:-5])
    data = data[['index','title','manipulated_title','body','graphic','publishedDate','tag']]
    data.to_json(output+'random_title_swap.json', orient = 'records')

    print("Random swap completed")

if __name__ == "__main__":
    args = get_args()
    input_path = args.i
    output_path = args.o
    if not os.path.exists(output_path):
        os.system("mkdir " + output_path)
    swap_titles(input_path, output_path)