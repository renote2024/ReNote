source /home/wname/Documents/github/renote-source/venv_renote/bin/activate
echo 'Check python version'
which python


exec_dir_path=$TMPDIR/wname_code/renote_main/a1/b1/c1

mkdir -p $exec_dir_path

cd $exec_dir_path


# constants
resume=1
source_envs_path=$TMPDIR/renote_nodes_venvs/machine1/
backupenvs_path=$TMPDIR/renote_nodes_venvs/copied_envs/machine1/

# change 
part_id=1
num_process=32
nb_paths_text_file=/projects/semcache/nb_tname_datasets/github_stars_20_plus/all_files/part_$part_id.txt
results_cache_path=/home/wname/Documents/github/renote-source/renote_analysis_caches/cache_stars_part_$part_id/

mkdir -p $results_cache_path


# echo the complete path of the current working directory

echo '> Current working directory: ' 
pwd

# Log information to verify everything is correct before running ollama serve
echo 'Logging information before running ollama serve:'
echo "exec_dir_path: $exec_dir_path"
echo "resume: $resume"
echo "source_envs_path: $source_envs_path"
echo "backupenvs_path: $backupenvs_path"
echo "part_id: $part_id"
echo "num_process: $num_process"
echo "nb_paths_text_file: $nb_paths_text_file"
echo "results_cache_path: $results_cache_path"


# Prompt user input to confirm before continuing
read -p "Is the above information correct? (yes/no): " user_confirm

if [ "$user_confirm" != "yes" ]; then
  echo "Aborting the script as per user input."
  exit 1
fi




ollama serve &
python /home/wname/Documents/github/renote-source/renote_utils/main_parts.py --nb_paths_text_file $nb_paths_text_file --results_cache_path $results_cache_path --resume $resume --source_envs_path $source_envs_path --backupenvs_path $backupenvs_path --num_process $num_process


echo 'The following dataset has been processed: ' $nb_paths_text_file  