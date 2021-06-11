import json

def add_id(path='data/wiki/partitions/test.ndjson', id_start=0):
    # Read in list of pages
    data = []
    iid = id_start
    with open(path, 'rt') as fin:
        for l in fin.readlines():
            # print(l)
            obj = json.loads(l)
            # print(obj)
            obj = [iid] + obj
            # print(obj)
            # exit()
            data.append(obj)
            iid += 1
            
    # Open the file
    with open(path, 'w') as fout:
        # Write as json
        for p in data:
            print(json.dumps(p), file=fout)
    
    return iid

import os
if __name__ == '__main__':
    wiki_dir = 'data/wiki/partitions'
    iid = 0
    for fn in os.listdir(wiki_dir):
        if 'test' in fn:
            continue
        iid_end = add_id(path=os.path.join(wiki_dir, fn), id_start=iid)
        print(f'file:{fn} [{iid_end-iid}/{iid_end}]')
        iid = iid_end
    # print(iid)
    