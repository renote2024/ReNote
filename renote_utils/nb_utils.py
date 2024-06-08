import uuid
import nbformat
from ast_visit import ASTNodeVisitor
import ast
import papermill as pm
import os
import subprocess


def addMissingModule(missing_module):
    r =  subprocess.run([f"pip install {missing_module}"], capture_output=True, shell=True)
    if r.returncode != 0:
        return r.returncode
    return 0


class ReadNB:
    def __init__(self, nb_path):
        self.nb_path = nb_path
        self.nb_content = None

    def readNB(self):
        """
        Read a notebook file and return the code cells
        :param nb_path: path to the notebook file
        :return: list of code cells
        """
        try:
            with open(self.nb_path, 'r', encoding='utf-8') as f:
                self.nb_content = nbformat.read(f, as_version=4)
                return self.nb_content
        except Exception as e:
            print(e)
            return None

    def readCodeCells(self):
        code_cells = []
        for cell in self.nb_content['cells']:
            if 'cell_type' in cell:
                if cell['cell_type'] == 'code':
                    if not self._is_empty(cell):
                        code_cells.append(cell)

        return code_cells
    
    def _is_empty(self, cell):
        if cell["source"] is None:
            return True
        else:
            source_code = ''
            if isinstance(cell['source'], (list, tuple, set)):
                source_code = ''.join(cell['source']).strip().replace(" ", "")
            elif isinstance(cell['source'], str):
                source_code = cell['source'].strip().replace(" ", "")
            
            return source_code == '' # return True if the cell is empty
    
    def getKernelInfo(self):    
        kernel_info = self.nb_content.get('metadata', {}).get('kernelspec', {})
        if kernel_info:
            kernel_name = kernel_info.get('name', 'Unknown').lower()
            return kernel_name
        else:
            return 'Unknown'



"""
Step 0: Read the notebook file
only pass notebook with python 3
"""
def readNoteBook(nb_path):    
    nb = ReadNB(nb_path)
    nb_content = nb.readNB()
    # print(nb_content)

    # 1. If we cannot read the notebook file, we will move it to the error directory
    if nb_content is None:
        print(f"Cannot read the notebook file {nb_path}")
        return None
    
    # 2. Check if the notebook has code cells
    code_cells = nb.readCodeCells()



    if len(code_cells) == 0:
        print(f"No code cells in the notebook {nb_path}")
        return None
    


    # 3. Check the kernel  info of the notebooks. If the kernel is not in python, we dont do anything
    kernel_name = nb.getKernelInfo().lower()
    if "py" not in kernel_name:
        print(f"Kernel is not Python: {kernel_name}, for the notebook {nb_path}: fix this ------------ code condition is not true")
        # return None

    # print(f"> ***  Succesfully read the notebook {nb_path} with {len(code_cells)} code cells and Python kernel {kernel_name} *** ")

    # print(f'> Notebook read {nb_path}, code cells: {len(code_cells)}, kernel: {kernel_name}')

    return nb


class RenoteAST:
    def __init__(self, code_cells):
        self.code_cells = code_cells
        self.new_code_cells = []
        self.undefined_vars_dict = None

        # 
        self.destination = ""
        self.undefined_var = ""
        self.undefined_index = -1
        self.defined_index = -1

    
    def _create_cell(self, cell, def_list, use_list):
        c = Cell(cell)
        c.set_spacial_order(len(self.new_code_cells))
        c.def_list = def_list
        c.use_list = use_list
        self.new_code_cells.append(c)
    
    def _find_def_use(self, cell):
        source_code = self._get_source_code(cell)
        # try:
        root = ast.parse(source_code)
        # except:
            # return None
        visitor = ASTNodeVisitor()
        visitor.visit(root, scope=0)

        def_list = visitor.def_list
        use_list = visitor.use_list
        return def_list, use_list

    def _get_source_code(self, cell):
        source = ''''''
        lines = cell.source.splitlines()
        for line in lines:
            if not line.startswith(("!", "%", "#", "$", "-")):
                source += line + "\n"
        return source
    
    def _getPrevDefinedVars(self, index, scope):
        total_def = []
        cell = self.new_code_cells[index]  # current cell
        for c in self.new_code_cells[:index]:
            if 0 in c.def_list:
                total_def.extend(c.def_list[0])
        i = 0
        while i <= scope:
            total_def.extend(cell.def_list[i])
            i += 1

        return total_def
    
    def _setUndefinedVars(self):
        undefined = {}
        for index, cell in enumerate(self.new_code_cells):
            use_vars_list = list(cell.use_list.items())
            if not undefined.get(index):
                undefined[index] = set()
            for scope, use_vars in use_vars_list:
                def_vars = self._getPrevDefinedVars(index, scope)
                for use_var in use_vars:
                    if use_var not in def_vars:
                        undefined[index].add(use_var)
        self.undefined_vars_dict = undefined
    

    def get_post_defined_vars(self, index):
        defined = {}
        for c in self.new_code_cells[index + 1:]:
            c_index = self.new_code_cells.index(c)
            if c_index not in defined:
                defined[c_index] = []
                if 0 in c.def_list:
                    defined[c_index].extend(c.def_list[0])
        return defined
    
    def _getPostDefinedVarsArray(self, index):
        total_def = []
        defined = self.get_post_defined_vars(index)
        for k in defined.keys():
            total_def.extend(defined[k])
        return total_def

    def _getDefinedIndex(self, index):
        defined = self.get_post_defined_vars(index)
        for k, v in defined.items():
            if self.undefined_var in v:
                return k
    
    def _checkDefUse(self):
        undefined_var_presence = False
        for i in self.undefined_vars_dict.keys():
            if len(self.undefined_vars_dict[i]) != 0:
                undefined_var_presence = True
        
        if not undefined_var_presence:
            self.destination = "no_undefined"
            self.undefined_index = len(self.new_code_cells)
            return
        

        for i, undefined_vars in self.undefined_vars_dict.items():
            undefined = False
            def_after_use = False

            def_list = self._getPostDefinedVarsArray(i)

            for undefined_var in undefined_vars:
                if undefined_var in def_list:
                    print("Def after", undefined_var)
                    if self.undefined_var == "":
                        self.undefined_var = undefined_var
                        self.defined_index = self._getDefinedIndex(i)
                    if self.undefined_index == -1:
                        self.undefined_index = i
                    def_after_use = True
                else:
                    print("Undefined", undefined_var)
                    if self.undefined_index == -1:
                        self.undefined_index = i
                    undefined = True

            if undefined and def_after_use:
                self.destination = "both"
                return
            elif undefined and not def_after_use:
                self.destination = "undefined"
                return
            elif not undefined and def_after_use:
                self.destination = "defined_after"
                return
    
    def _fooUndefinedVariable(self):
        # check the undefined variable in the notebook
        self._setUndefinedVars()
        self._checkDefUse()

    def run(self):
        for cell in self.code_cells:
            t = self._find_def_use(cell)    
            def_list, use_list = t
            self._create_cell(cell, def_list, use_list)        
        self._fooUndefinedVariable()
        



class ReOrderCellsTempNBForDefinedAfter:
    def __init__(self, older_nb_cells, defined_index, undefined_index):
        self.older_nb_cells = older_nb_cells
        self.defined_index = defined_index
        self.undefined_index = undefined_index

    def _getReOrderedCells(self):
        old_order = self.older_nb_cells
        def_cell = old_order.pop(self.defined_index)
        new_order = old_order
        new_order.insert(self.undefined_index, def_cell)
        # print("NEW",new_order)
        return new_order
    

    def get_source_code(self, cell):
        source = ''''''
        lines = cell.source.splitlines()
        for line in lines:
            if not line.startswith(("!", "%", "#", "$", "-")):
                source += line + "\n"
        return source


    def getReorderedNBFile(self):
        order_cells = self._getReOrderedCells()
        nb = nbformat.v4.new_notebook()
        for cell in order_cells:
            source = self.get_source_code(cell)
            nb.cells.append(nbformat.v4.new_code_cell(source))
        return nb






def papaermillExecution(orignal_nb_path, kernel_name='python3'):
    # Use Papermill to execute the current cell
    # temp_nb_output_path= orignal_nb_path.replace(".ipynb", "_output_temp.ipynb")
    try:
        pm.execute_notebook(
            input_path = orignal_nb_path,
            output_path = None, #temp_nb_output_path,
            timeout=300,  # time out in second
            kernel_name=kernel_name,  # Adjust kernel name as needed
            parameters={},  # Optional: You can pass parameters if needed
            progress_bar=False,  # Disable the progress bar for cleaner output
            log_output=False,
            # request_save_on_cell_execute=True,
        )
    except Exception as e:
        # print(f"Erorr: {e}")
        # print('Removing temp files')
        # os.remove(temp_nb_output_path)
        raise e
    
    # os.remove(temp_nb_output_path)
    return True

















# ==============================

def assign_id(cell):
    if 'id' in cell['metadata']:
        return cell['metadata']['id']
    elif 'id' in cell:
        return cell['id']
    else:
        return str(uuid.uuid4())


class Cell:
    def __init__(self, cell):
        self.successor = None  # Cell
        self.cell_id = assign_id(cell)  # string
        self.source = cell['source']  # string
        self.spacial_order = 0
        self.def_list = {}  # dict
        self.use_list = {}  # dict

    def set_successor(self, cell):
        self.successor = []
        if cell is not None:
            self.successor = cell

    def set_spacial_order(self, value):
        self.spacial_order = value



def getReOrderedNB(sorter, nb_path):
    # 2. Get values of attributes of the sorter
    defined_index = sorter.defined_index
    older_cells = sorter.new_code_cells
    undefined_index = sorter.undefined_index

    # 3. Generate a file with reordered cells
    re = ReOrderCellsTempNBForDefinedAfter(older_cells, defined_index, undefined_index)
    new_ordered_nb = re.getReorderedNBFile()


    # # 4. Sort it again to see if it still has undefined vars
    # sub_sorter = RenoteAST(new_ordered_nb.cells)
    # sub_sorter.run()
    # new_exe = sub_sorter.undefined_index

    new_notebook_path = nb_path.replace(".ipynb", "_reordered_temp.ipynb")

    with open(new_notebook_path, "w", encoding="utf-8") as f:
        nbformat.write(new_ordered_nb, f)

    print(f"> Running for Rordered Cells is successful")
    return new_notebook_path
    
    # if sub_sorter.destination == "no_undefined":
    #     exe = Execution(new_file)
    #     result, err = exe.execute()
    #     print(err)
    #     if result:
    #         new_exe = total_code
    #         executability = "full"
    #     else:
            
    #         if exe.max_exe <= 0:
    #             c = 0
    #         else:
    #             c = exe.max_exe - 1
            
    #         new_exe = c

    #         if new_exe > 0:
    #             executability = "partial"
    #         else:
    #             executability = "none"
            
    #     if os.path.exists(new_file):
    #         os.remove(new_file)
    #     old_exe_percent = 0
    #     new_exe_pecent = 0

    #     if total_code != 0:
    #         old_exe_percent = (old_exe / total_code) * 100
    #         new_exe_pecent = (new_exe / total_code) * 100

    #     increase_percent = new_exe_pecent - old_exe_percent
    #     data = {
    #         'file name': file_name,
    #         'error type' : destination,
    #         'executability status': executability,
    #         'total code cells': total_code,
    #         '# original executable cells': old_exe,
    #         '% original executability': old_exe_percent,
    #         '# new executable cells': new_exe,
    #         '% new executability': new_exe_pecent,
    #         '% increasing': increase_percent
    #     }