import os 

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


def main(nb_dir_path, num_parts):

    # for existing ones we can check the cache before listing all files

    all_nbs = [os.path.join(nb_dir_path,f)  for f in  os.listdir(nb_dir_path) if f.endswith('.ipynb')]
    parts = divide_list_into_parts(all_nbs, num_parts)
    for i, part in enumerate(parts):
        with open(f'{nb_dir_path}/part_{i+1}.txt', 'w') as f:
            f.write('\n'.join(part))
    
    with open(f'{nb_dir_path}/all_parts.txt', 'w') as f:
        f.write('\n'.join(all_nbs))



if __name__ == "__main__":
    nb_dir_path = '/projects/semcache/nb_tname_datasets/github_stars_20_plus/all_files'
    main(nb_dir_path=nb_dir_path, num_parts=6)