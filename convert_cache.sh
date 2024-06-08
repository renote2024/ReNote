source /home/wname/Documents/github/renote-source/venv_renote/bin/activate
echo 'Check python version'
which python

csv_dir=paper_results

mkdir -p $csv_dir



part=1
cpath=/home/wname/Documents/github/renote-source/renote_analysis_caches/cache_stars_part_$part
csv=stars_part$part.csv 
python convert_cache_results2csv.py --results_cache_path $cpath  --csv $csv_dir/$csv

part=2
cpath=/home/wname/Documents/github/renote-source/renote_analysis_caches/cache_stars_part_$part
csv=stars_part$part.csv 
python convert_cache_results2csv.py --results_cache_path $cpath  --csv $csv_dir/$csv


part=3
cpath=/home/wname/Documents/github/renote-source/renote_analysis_caches/cache_stars_part_$part
csv=stars_part$part.csv 
python convert_cache_results2csv.py --results_cache_path $cpath  --csv $csv_dir/$csv


part=4
cpath=/home/wname/Documents/github/renote-source/renote_analysis_caches/cache_stars_part_$part
csv=stars_part$part.csv 
python convert_cache_results2csv.py --results_cache_path $cpath  --csv $csv_dir/$csv


part=5
cpath=/home/wname/Documents/github/renote-source/renote_analysis_caches/cache_stars_part_$part
csv=stars_part$part.csv 
python convert_cache_results2csv.py --results_cache_path $cpath  --csv $csv_dir/$csv



part=6
cpath=/home/wname/Documents/github/renote-source/renote_analysis_caches/cache_stars_part_$part
csv=stars_part$part.csv 
python convert_cache_results2csv.py --results_cache_path $cpath  --csv $csv_dir/$csv




cpath=/home/wname/Documents/github/renote-source/renote_analysis_caches/cache_36K_part_1
csv=36K_part1.csv 
python convert_cache_results2csv.py --results_cache_path $cpath  --csv $csv_dir/$csv



cpath=/home/wname/Documents/github/renote-source/renote_analysis_caches/machine1_dataset1
csv=machine1_dataset1.csv
python convert_cache_results2csv.py --results_cache_path $cpath  --csv $csv_dir/$csv




