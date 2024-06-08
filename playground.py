import os 




def write_file(file_name, content):
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



fname =  '..\\data/auction2.csv'

write_file(fname, 'hello world')

with open(fname, 'r') as f:
    print(f.read())


