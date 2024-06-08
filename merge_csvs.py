import csv
import pandas as pd
import os


# read csvs files and merge them into one
def merge_csvs(csvs, output_csv_path):
    dataframes = [pd.read_csv(csv) for csv in csvs]
    merged = pd.concat(dataframes)
    merged.to_csv(output_csv_path, index=False)


if __name__ == '__main__':
    # read csvs from a directory

    base_path = '/home/wname/Documents/github/renote-source/paper_results'


    all_csvs = [os.path.join(base_path, f) for f in os.listdir(base_path) if f.endswith('.csv')]
    merge_csvs(all_csvs, '/home/wname/Documents/github/renote-source/paper_results/all_merged.csv')

    only_stars = [f for  f in all_csvs if f.startswith('/home/wname/Documents/github/renote-source/paper_results/stars')]

    merge_csvs(only_stars, '/home/wname/Documents/github/renote-source/paper_results/stars_merged.csv')

    sixty_36k = ['/home/wname/Documents/github/renote-source/paper_results/machine1_dataset1.csv', '/home/wname/Documents/github/renote-source/paper_results/36K_part1.csv']

    merge_csvs(sixty_36k, '/home/wname/Documents/github/renote-source/paper_results/sixty_36k_merged.csv')

    

