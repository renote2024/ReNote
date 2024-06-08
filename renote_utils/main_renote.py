import subprocess
import argparse
import os
from tqdm import tqdm
import os
from diskcache import Index
from process_nb import processNB ,checkIfNBIsAlreadyEvaluated 
from multiprocessing import Pool
from joblib import Parallel, delayed


# sys.path.append('../../../RenoteUtils/')


def divide_list_into_parts(lst, num_parts):
    out = []
    if num_parts < len(lst):
        step = len(lst) // num_parts
        i = 0
        count = 0
        while count < num_parts:
            out.append(lst[i:i+step])
            i += step
            count += 1
        
        while i < len(lst):
            out[-1].append(lst[i])
            i += 1

    else:
        for i in range(len(lst)):
            out.append([lst[i]])
            
    return out




def shellProcessNB(local_env, config):
    nb_path = config['nb_path']
    results_cache_path = config['results_cache_path']
    resume = config['resume']
    backup_venv_path = os.path.join(config['backupenvs_path'], local_env)
    source_venv_path = os.path.join(config['source_envs_path'], local_env)

    p_i = config['index']

    print(f'nb_path: {nb_path}')
    nb_name = os.path.basename(nb_path)

    print(f"                 ************ [{p_i}/{config['total_nbs']}] START of Renote Analysis for {nb_path} ************")

    

    # Check if the old path exists or not
    if not os.path.exists(source_venv_path):
        raise FileNotFoundError(f"Old virtual environment path '{source_venv_path}' does not exist.")

    # Check if the backup path exists or not
    if not os.path.exists(backup_venv_path):
        raise FileNotFoundError(f"Backup virtual environment path '{backup_venv_path}' does not exist.")

    print(f'Env {local_env} is processing the notebook {nb_name}')
    # _ = input(f'Press Enter to continue...')

    # # Delete the old venv
    print(f'Deleting the old venv: {source_venv_path}')
    subprocess.run(f'rm -rf {source_venv_path}', shell=True)
    

    # # Copy the backup venv to the old venv
    # shutil.copytree(backup_venv_path, config['source_envs_path'])
    print(f'Copying the backup venv to the old venv: {source_venv_path}')
    subprocess.run(f"cp -r {backup_venv_path} {config['source_envs_path']}", shell=True)

    single_analysi_file_path = '/home/wname/Documents/github/renote-source/renote_utils/single_nb_analysis.py'

    activate_script = os.path.join(source_venv_path, 'bin', 'activate')
    command_activate = f'source {activate_script} &&'
    command_run_process_nb = f'python {single_analysi_file_path} --nb_path {nb_path} --results_cache_path {results_cache_path} --resume {resume} &&'
    command_deactivate = 'deactivate'

    command = f'{command_activate} {command_run_process_nb} {command_deactivate}' 

    print(f'Command: {command}')
    subprocess.run(command, shell=True)





    # The following command should be run in the subprocess
    # Subprocess commands   


 
def processNBFolderSequential(nb_dir_path, results_cache_path, resume):
    # read all the notebooks in the directory

    all_nbs = [f for f in  os.listdir(nb_dir_path) if f.endswith('.ipynb')]
    # print(f'all nbs: {all_nbs}')
    print(f"Total notebooks found: {len(all_nbs)}")
    for i, nb_name  in tqdm(enumerate(all_nbs)):   
             
        print(f"                 ************ [{i}/{len(all_nbs)}] START of Renote Analysis for {nb_name} ************")       
        # res = None
        try:
            res = processNB(nb_path=os.path.join(nb_dir_path, nb_name), results_cache_path=results_cache_path, resume=resume)
        except Exception as e:
            print(f"Error in processing the notebook {nb_name}, Error: {e}")
            error = {'nb_path': nb_name, 'Error': str(e)}
            print('> EXITING THE PROCESSING OF THE NOTEBOOK')
            continue
        
        print(f"                 ============ END of Renote Analysis for {nb_name} ========")




def executeTask(env, task_li):
    for config in task_li:
        shellProcessNB(env, config)




def processNBFolderParallel(nb_dir_path, results_cache_path, resume, source_envs_path, backupenvs_path, num_process):
    if os.path.exists(results_cache_path)==False:            
        raise FileNotFoundError(f"Results cache path '{results_cache_path}' does not exist.")
    
    
    g_all_nbs = [f for f in  os.listdir(nb_dir_path) if f.endswith('.ipynb')]
    print(f"Total notebooks found: {len(g_all_nbs)}")
    envs = [f'env{i}' for i in range(1,num_process+1)]
    print(f'envs: {envs}')

    all_nbs = []
    # Check if the notebook is already evaluated; if yes, then return the result
    results_cache = Index(results_cache_path)

    for nb_name in g_all_nbs:
        res = checkIfNBIsAlreadyEvaluated(results_cache, nb_name)
        if res is None:
            # print(f"Notebook '{nb_name}' is already evaluated; using the cache results.")
            # return res
            all_nbs.append(nb_name)
    
        
    all_nbs_with_assign_ids = [{'index': i, 'total_nbs':len(all_nbs), 'nb_path': os.path.join(nb_dir_path, nb_name), 'results_cache_path': results_cache_path, 'resume':resume, 'backupenvs_path': backupenvs_path, 'source_envs_path':source_envs_path} for i, nb_name in enumerate(all_nbs)]

    li_of_li_tasks =  divide_list_into_parts(all_nbs_with_assign_ids, len(envs))

    assert len(li_of_li_tasks) == len(envs)

    results = Parallel(n_jobs=len(envs))(delayed(executeTask)(env, task_l) for env, task_l in zip(envs, li_of_li_tasks))
    # with Pool(processes=num_process) as pool:
    #     results = pool.map(executeTask, [(env, task_l) for env, task_l in zip(envs, li_of_li_tasks)])
    




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read all .ipynb files in a directory.')
    parser.add_argument('--nb_dir_path', type=str, required=True, help='Path to the directory containing the notebooks')
    parser.add_argument('--results_cache_path', type=str, required=True, help='Path to the results cache [DiskCache]')
    parser.add_argument('--resume', type=int,  help='Check the cache before processing the notebook')
    parser.add_argument('--source_envs_path', type=str, required=True, help='Path to the source virtual environments')
    parser.add_argument('--backupenvs_path', type=str, required=True, help='Path to the backup virtual environments')
    parser.add_argument('--num_process', type=int, required=True, help='Number of processes to run in parallel')

    args = parser.parse_args()
    print(f'{args}, {type(args.resume)}')
    processNBFolderParallel(nb_dir_path=args.nb_dir_path, results_cache_path=args.results_cache_path, resume=args.resume, source_envs_path=args.source_envs_path, backupenvs_path=args.backupenvs_path, num_process=args.num_process)
    # processNBFolderSequential(nb_dir_path=args.nb_dir_path, results_cache_path=args.results_cache_path, resume=args.resume)
    