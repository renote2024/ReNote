import os 
from nbconvert import PythonExporter
from nb_utils import readNoteBook
import localchatgpt as llm
from pathlib import Path

# def create_path(nb_path):
    


class FixFileNotFound:
    def __init__(self, nb_path, exec_results):
        self.nb_path = nb_path    
        self.exe_results = exec_results
        self.missing_file_path = exec_results['FileNotFoundError_path']
    
    def getFileName(self, ):
        return self.missing_file_path

    def write_file(self, file_name, content):
        if os.path.isdir(file_name):
            os.makedirs(file_name, exist_ok=True)
        else:
            directory = os.path.dirname(file_name)
            try:
                if directory != "":
                    os.makedirs(directory, exist_ok=True)
                with open(file_name, "w", encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                print(e)
                return False
        return True
        # path = Path(file_name)
        # if path.suffix:  # Check if it's a file path
        #     # Create parent directories if they don't exist
        #     path.parent.mkdir(parents=True, exist_ok=True)
        #     # Create an empty file at the given path
        #     with open(file_name, "w", encoding='utf-8') as f:
        #         f.write(content)
        #     print(f"---------> Created file at ------------------{path}")
        #     # return True
        # else:  # It's a directory path
        #     path.mkdir(parents=True, exist_ok=True)
        #     print(f"---------> Created directory at {path}")
        #     # return True
        
        # # return False





    def _getNBSourceCode(self):
        nb = readNoteBook(self.nb_path)
        # 2. Construct a python file path
        exporter = PythonExporter()
        source, _ = exporter.from_notebook_node(nb.readNB())
        return source 
    
    def get_file_data(self, response):
        pattern = "```"
        file_content = """"""
        start = False
    
        for line in response.splitlines():
            if pattern in line:
                start = not start
                continue
            if start:
                file_content += line + "\n"
        return file_content


    def create_input_file(self):
        nb_source_code = self._getNBSourceCode()
        # 3.3. generate a sample input file "tee.py". No yapping, just the data for the file and nothing else.
        content = ""
        time_run = 0
        while True:
            prompt = f"Generate a sample input file {self.missing_file_path} for the source code below. Format the response with only the needed data between ``` and ```. Just data and No yapping.\n\n{nb_source_code}"
            response = llm.localChat(prompt)
            content = self.get_file_data(response)
            print(f"Content: {content}")
            time_run += 1
            if content.strip().replace(" ", "") != "":
                break
            if time_run == 3:
                break
            
        # print(f'\n>> LLM Generated File Content for input:\n {content.rstrip()}\n' )
        
        # 3.4 Create the temp input file
        if self.write_file(self.missing_file_path, content) == True:
            print(f"> File created with LLLM for {self.missing_file_path}")
            return True
        else:
            print(f"> LLM Failed to create {self.missing_file_path}")
            return False
        