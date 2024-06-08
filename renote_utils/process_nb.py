import os
from nb_utils import readNoteBook, RenoteAST, getReOrderedNB, addMissingModule
from ExecuteNoteBook import ExecuteNoteBook
from FixFileNotFound import FixFileNotFound
import pandas as pd
from tqdm import tqdm
from diskcache import Index
import subprocess
import copy



def aggreGateFileMoudleFixingResults(all_exec_results):
    # total_exec_dict= {'ModuleNotFoundError':0, 'FileNotFoundError':0 }
    total_cell_ex_after_file_fix = 0
    total_cell_ex_after_module_fix = 0
    total_module_not_found = 0
    total_file_not_found = 0

    all_unique_errors_during_execution  = list(set([d['status'] for d in all_exec_results]))
    # all_unique_errors_during_execution = ','.join(all_unique_errors_during_execution) 

    #FIXME: Same cell. CAN HAVE MULTIPLE FILE NOT FOUND ERROR and thus execution can report more exectuion cells.
    # its not a problem but we have to be consisten with our definition of increase 

    for i in range(len(all_exec_results)-1):
        d1 = all_exec_results[i]
        j = i
        d2 = all_exec_results[j]
        for j in range(i+1, len(all_exec_results)):
            if d2['max_execute_cells'] == d1['max_execute_cells']:
                d2 = all_exec_results[j]
            else:
                break

        if d1['status']== 'ModuleNotFoundError':
            total_cell_ex_after_module_fix += (d2['max_execute_cells'] - d1['max_execute_cells'])  
            total_module_not_found += 1
        elif d1['status'] == 'FileNotFoundError':
            total_cell_ex_after_file_fix += (d2['max_execute_cells'] - d1['max_execute_cells'])
            total_file_not_found += 1



    return {'total_cell_ex_after_file_fix': total_cell_ex_after_file_fix, 'total_cell_ex_after_module_fix': total_cell_ex_after_module_fix, 'all_unique_errors_during_execution': all_unique_errors_during_execution, 'total_module_not_found': total_module_not_found, 'total_file_not_found': total_file_not_found}
        

def nbExecutionWithFixingMissingModuleANDInputData(nb_path):
    all_exec_results = []
    missing_files_paths = set()
    installed_modules = set()
    exec_r =  ExecuteNoteBook(nb_path).executeNotebook()
    all_exec_results.append(exec_r)
    # print(f'Result 1: {exec_r}')
    err_in_file_creation = None
    while True:
        if 'FileNotFoundError_path' in exec_r:

            missing_file_p = exec_r['FileNotFoundError_path']
            print(f'> Fixing Missing file: {missing_file_p}')
            if missing_file_p in missing_files_paths:
                print(f">> File already fixed ")
                err_in_file_creation = f'Fix it. File creation-problem File {missing_file_p}'
                break

            missing_files_paths.add(missing_file_p)
            f = FixFileNotFound(nb_path, exec_r)
            create_status =  f.create_input_file()
            if create_status:
                exec_r =  ExecuteNoteBook(nb_path).executeNotebook()
                all_exec_results.append(exec_r)
            else:
                print(f">> File not created. {exec_r['FileNotFoundError_path']}")
                break
        elif 'missing_module' in exec_r:
            m = exec_r['missing_module'].strip()
            if m not in installed_modules:
                installed_modules.add(m)
                print(f">> ReNote: Fixing Missing module: {m}")
                addMissingModule(m)
                exec_r =  ExecuteNoteBook(nb_path).executeNotebook() 
                all_exec_results.append(exec_r) 
            else:
                print(f'>> ReNote: {m} cannot be installed, breaking the loop')
                break              
        
        else:
            break
    
    # if filepath is generating a directory we should remove that directory as well. TODO
    for file_path in missing_files_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
    
    return all_exec_results, err_in_file_creation 
    

def checkIfNBIsAlreadyEvaluated(results_cache, nb_name):
    # print(f"Checking if the notebook {nb_name} is already evaluated")
    if nb_name in results_cache:
        return results_cache[nb_name]
    else:
        return None



def processNB(nb_path, results_cache_path, resume):
    nb_name = os.path.basename(nb_path)
    nb_cache = Index(results_cache_path)

    if resume>0:
        res = checkIfNBIsAlreadyEvaluated(nb_cache, nb_name)
        if res is not None:
            print(f"NB {nb_name} is already evaluated, using the cache results")
            return res
    
    re_order_nb_path = None
    nb = readNoteBook(nb_path)
    code_cells =  nb.readCodeCells()
    # print(f"Code cells: {code_cells}")
    print(f"Total code cells: {len(code_cells)}")

    # STEP 1: AST analysis: parse the code cells
    ast_analysis = RenoteAST(code_cells)
    ast_analysis.run()
    ast_status = ast_analysis.destination
    print(f"Status: {ast_status}")
    
    if ast_status in  ["no_undefined", 'both', 'undefined']:
        print("> DO the EXECUTION")     
    elif ast_status == "defined_after":
        print("> Undefined variable is defined after, Fix it and re-run the notebook")
        re_order_nb_path =  getReOrderedNB(ast_analysis, nb_path)
        # # 2nd AST analysis
        # nb = readNoteBook(new_nb_path)
        # code_cells =  nb.readCodeCells()
        # ast_analysis = RenoteAST(code_cells)
        # ast_analysis.run()
        # status = ast_analysis.destination
    else:
        raise ValueError(f"Undefined status in the AST analysis, status: {ast_status}")  
    


    final_execution_result_dict = None
    
    # fix the import error and file error
    all_fix_erros_results, file_creation_error =  nbExecutionWithFixingMissingModuleANDInputData(nb_path)

    

    agg_resulsts =  aggreGateFileMoudleFixingResults(all_fix_erros_results)

    result_dict_after_import_fix = copy.deepcopy(all_fix_erros_results[-1])

    final_execution_result_dict = result_dict_after_import_fix
    final_execution_result_dict['Reordering'] = False
    print(f"1 Final Execution Result: {final_execution_result_dict}")
    if re_order_nb_path is not None:
        temp_list, file_creation_error =  nbExecutionWithFixingMissingModuleANDInputData(re_order_nb_path) 
        re_order_result_dict = temp_list[-1]
        if re_order_result_dict['max_execute_cells'] > result_dict_after_import_fix['max_execute_cells']:
            print("Reordering is working, Increasing the execution.")
            final_execution_result_dict = re_order_result_dict
            final_execution_result_dict['Reordering'] = True
            subprocess.run(f'rm -f {re_order_nb_path}', shell=True)



    

    # print(f'Initial Execution Result: {initial_exec_resul_0}')
    # print(f'Result after fixing file and imports : {result_dict_after_import_fix}')
    # print(f'Renote Final Execution Result: {final_execution_result_dict}')
    # print(f'Aggregate Results: {agg_resulsts}')

    initial_exec_resul_0 = all_fix_erros_results[0]
    paper_results = {}
    paper_results['Total Code Cells'] = len(code_cells)
    paper_results['Initial_max_execute_cells'] = initial_exec_resul_0['max_execute_cells']
    paper_results['ReNote_max_execute_cells'] = final_execution_result_dict['max_execute_cells']
    paper_results['Increased_execution_cells'] = paper_results['ReNote_max_execute_cells'] - initial_exec_resul_0['max_execute_cells']
    paper_results['Inital_Status'] = initial_exec_resul_0['status']
    paper_results['Final_Status'] = final_execution_result_dict['status']
    paper_results['Reordering'] = final_execution_result_dict['Reordering']
    paper_results =  {**paper_results, **agg_resulsts}
    paper_results['FileCreationError (Manual)'] = file_creation_error
    paper_results['nb_path'] = nb_path
    # paper_results['nb_name'] = nb_name
    paper_results['ast_status'] = ast_status

    print(f'for screen {paper_results}' )

    df = pd.DataFrame([paper_results])
    # print('> Results:')
    print( df)        

    nb_cache[nb_name] = paper_results 
    return paper_results







if __name__ == "__main__":
    p = '/projects/semcache/nb_tname_datasets/github_stars_20_plus/all_files/https%3A%2F%2Fraw.githubusercontent.com%2Fgautham20%2Fpytorch-ts%2Fmaster%2Fitem%2520sales%2520forecasting.ipynb'
    cpath = '/home/wname/Documents/github/renote-source/archive_wname/temp_cache'
    res =   processNB(p, cpath, resume=0)


