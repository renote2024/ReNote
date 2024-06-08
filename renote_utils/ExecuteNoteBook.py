import re
from nb_utils import readNoteBook, papaermillExecution
import localchatgpt as llm

def getErrorTypeFromLLM(err):
    prompt = f"Identify the error name from the error report below. Format the response between ``` and ```. It must be a 1-word string and nothing else. No yapping. \n\n{err}"
    response = llm.localChat(prompt)
    err_type = response.replace("```", "").strip()
    return err_type



class ExecuteNoteBook:
    def __init__(self, nb_path):
        nb = readNoteBook(nb_path) 
        assert nb is not None, "Notebook is empty"
        code_cells = nb.readCodeCells()
        self.total_code_cells = len(code_cells)      
        self.orignal_nb_path = nb_path
                

    def find_err_cell(self, err):
        c = 0
        err_type = ""
        match = re.search(r'In\[(\d+)\]', err)
        if match:
            c = int(match.group(1))
        else:
            match = re.search(r'In \[(\d+)\]', err)
            if match:
                c = int(match.group(1))
            else:
                print("no match index")

        match = re.search(r'\b\w*Error\b', err)
        if match:
            err_type = match.group()
            if "31m" in err_type:
                err_type = err_type.replace("31m", "")
        else:
            err_type = None
            print("no match error")
        

        # we are not fininding all the errors, we will fix it later
        return c, err_type
    

    
    
    def executeNotebook(self):
        try:
            papaermillExecution(self.orignal_nb_path)
            return {'exec_successfull': True, 'status': "executable", 'total_code_cells':self.total_code_cells,  'max_execute_cells': self.total_code_cells}        
        except TimeoutError as e:
            max_exec_cell_number, _ = self.find_err_cell(str(e))
            return {'exec_successfull': False, 'status': "TimeoutError", 'total_code_cells':self.total_code_cells,  'max_execute_cells': -1}
            # right now i cannot find the cell number where the TimeoutError occured, so returing -1 fix it later
            # neural network might be training so we think if the notebook is taking longer than 5 minutes it can be executed 
        except Exception as e:
            max_exec_cell_number, err_type = self.find_err_cell(str(e))
            if "ModuleNotFoundError" and "No module named" in str(e):
                missing_module = str(e).split("No module named ")[1].replace("'", "")
                result_dict =  {'exec_successfull': False, 'status': "ModuleNotFoundError", 'total_code_cells':self.total_code_cells,  'max_execute_cells': max_exec_cell_number, 'missing_module': missing_module}
                return result_dict
            elif err_type is  None:
                if str(e).find("No space left on device") != -1:
                    print(f'>> No space left on device, error: {str(e)}, exiting...')
                    exit(0) 
                print(f'>> Fixing Unknown Error with LLM: {str(e)}')
                err = str(e)
                llm_error_type =   getErrorTypeFromLLM(err)
                return {'exec_successfull': False, 'status': f'LLM_ERROR_Extract={llm_error_type}' , 'total_code_cells':self.total_code_cells,  'max_execute_cells': max_exec_cell_number}
            elif "FileNotFoundError" in str(e) or err_type == "FileNotFoundError":
                extracted_path = None
                if "No such file or directory: " in str(e):
                    extracted_path = str(e).split("No such file or directory: ")[1].replace("'", "").strip()
                else:
                    match = re.search(r"FileNotFoundError: (.*?) not found.", str(e))
                    # Extract the matched part
                    if match:
                        extracted_path = match.group(1)
                
                assert extracted_path is not None, "FileNotFoundError path is None"
                return {'exec_successfull': False, 'status': "FileNotFoundError", 'total_code_cells':self.total_code_cells,  'max_execute_cells': max_exec_cell_number, 'FileNotFoundError_path': extracted_path}
            else:
                return {'exec_successfull': False, 'status':err_type, 'total_code_cells':self.total_code_cells,  'max_execute_cells': max_exec_cell_number}