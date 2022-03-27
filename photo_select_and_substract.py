import sys
from unicodedata import name
import numpy as np
import copy
from pathlib import Path
import pickle
import cv2

def get_time_and_no(photo_filename):
    #get elements of the name (without .np) split at . into prefix containing time and suffix containing id/no
    name_elements = photo_filename.split('.')
    time = name_elements[0][-17:]
    no = int(name_elements[1][-4:])
    return time,no


def find_and_substract(file,dir):
    
    time,no =get_time_and_no(file.name)
    
    for child in dir.iterdir():
        if(child.is_file() and child.suffix == '.np'):
            t,n = get_time_and_no(child.name)
            if(t == time and n>no):
                source_img = np.load(str(file.absolute()),allow_pickle = True)
                target_img = np.load(str(child.absolute()),allow_pickle = True)
                print(no,n)
    
def process_directory(src,target):
    
    src = Path(src)
    print(str(src))
    if(not src.is_dir()):
        raise Exception("source directory not found")
    target = Path(target)
    if(not target.is_dir()):
        target.mkdir()

    for child in src.iterdir():
        if(child.is_file() and child.suffix == '.np'):
            subtracted = find_and_substract(child,src)
            if(subtracted != None):
                 pickle.dump(subtracted,Path(target+"\\"+subtracted['filename'].replace(':','%')).open('wb'))
    





if __name__ == '__main__':
    source = './'+str(sys.argv[1])
    target = ('./'+str(sys.argv[2])) if len(sys.argv) > 2 else source + '_subtracted'
    print(source)
    process_directory(source,target)