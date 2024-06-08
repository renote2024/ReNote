import subprocess
import os
from multiprocessing import Pool


def create_and_setup_venv(venv_path):
    print(f" ******* Start: Creating and setting up virtual environment at {venv_path} **** ")
    # venv_path = os.path.join(base_path)
    os.makedirs(venv_path, exist_ok=True) 
    # Create the virtual environment
    subprocess.run(['python', '-m', 'venv', venv_path])
    
    # Activate the virtual environment
    activate_script = os.path.join(venv_path, 'bin', 'activate')
    
    # Install requirements
    requirements_file = 'requirements.txt'
    if os.path.isfile(requirements_file):
        subprocess.run(f'source {activate_script} && pip install -r {requirements_file} && deactivate', shell=True)
    else:
        print(f"No requirements.txt found at {requirements_file}")
    
    print(f" ******* End: Created and setup virtual environment at {venv_path} **** ")

def main():
    num_envs = 32
    # nodes = [f'node{i}_env' for i in range(1, 5)]
    with Pool(processes=32) as pool:
        # for node in nodes:
        base_env_path = f'$TMPDIR/renote_nodes_venvs/machine1'
        base_env_path = os.path.expandvars(base_env_path)
        # for i in  tqdm(range(1, num_envs + 1)):
        #     create_and_setup_venv(env_path)
        # Parallel(n_jobs=16)(delayed(create_and_setup_venv)(env_path) for _ in range(num_envs))
        env_paths = [f'{base_env_path}/env{i}' for i in range(1, num_envs + 1)]
        pool.map(create_and_setup_venv, env_paths)

if __name__ == "__main__":
    main()
