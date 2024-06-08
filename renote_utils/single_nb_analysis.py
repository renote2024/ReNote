import sys
import argparse
# sys.path.append('../../../RenoteUtils/')
from process_nb import processNB, checkIfNBIsAlreadyEvaluated

# 
 


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analysize a Single .ipynb file.')
    parser.add_argument('--nb_path', type=str, required=True, help='Path to notebook')
    parser.add_argument('--results_cache_path', type=str, required=True, help='Path to the results cache [DiskCache]')
    parser.add_argument('--resume', type=int,  help='Check the cache before processing the notebook')

    args = parser.parse_args()
    processNB(nb_path=args.nb_path, results_cache_path=args.results_cache_path, resume=args.resume)