import bz2
import subprocess
import os
import xml.sax
from wiki_xml_handler import WikiXmlHandler
from timeit import default_timer as timer
import gc
import json
from multiprocessing import Pool 
# import tqdm 

# List of lists to single list
from itertools import chain

# Sending keyword arguments in map
from functools import partial

def parse_wiki(data_path, limit=None, save=True):
    """Extract text from a compressed wikipedia XML dump.
       `limit` is an optional argument to only return a set number of books.
        If save, books are saved to partition directory based on file name"""

    # check exist
    partition_dir = 'data/wiki/partitions/'        
    p_str = data_path.split('-')[-1].split('.')[-2]
    out_dir = partition_dir + f'{p_str}.ndjson'
    if os.path.exists(out_dir):
        return

    # Object for handling xml
    handler = WikiXmlHandler()

    # Parsing object
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)

    # Iterate through compressed file
    for i, line in enumerate(subprocess.Popen(['bzcat'], 
                             stdin=open(data_path), 
                             stdout=subprocess.PIPE).stdout):
        try:
            parser.feed(line)
        except StopIteration:
            break
            
        # Optional limit
        if limit is not None and len(handler._pages) >= limit:
            # return handler._books
            break
    
    if save:
        partition_dir = 'data/wiki/partitions/'
        if not os.path.exists(partition_dir):
            os.makedirs(partition_dir)
        # Create file name based on partition name
        p_str = data_path.split('-')[-1].split('.')[-2]
        # p_str= 'test'
        out_dir = partition_dir + f'{p_str}.ndjson'

        # Open the file
        with open(out_dir, 'w') as fout:
            # Write as json
            for p in handler._pages:
                fout.write(json.dumps(p) + '\n')
        
        print(f'{len(os.listdir(partition_dir))} files processed.', end = '\r')

    # Memory management
    del handler
    del parser
    gc.collect()
    return None


def main():
    dump_dir = 'data/dump'
    data_paths = os.listdir(dump_dir)
    partitions = [os.path.join(dump_dir, file_name) for file_name in data_paths[16:]]
    print(len(partitions), partitions[-1])

    print(os.cpu_count())

    # parse_wiki(partitions[0], limit=10000)

    ############################################################# 

    # Create a pool of workers to execute processes
    pool = Pool(processes = 16)

    start = timer()

    

    # Map (service, tasks), applies function to each partition
    results = pool.map(parse_wiki, partitions)

    pool.close()
    pool.join()

    end = timer()
    print(f'{end - start} seconds elapsed.')

  
        
        

if __name__ == '__main__':
    main()
    