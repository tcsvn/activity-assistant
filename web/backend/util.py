import os
from os.path import basename
from zipfile import ZipFile 

def create_zip(folder_to_zip, dest_path):
    """ zips a folder with all files at the base and saves it at given location
    Parameters
    ----------
    folder_to_zip : String
        the path to the folder that is going to be zipped
    dest_path : String
        the path where the resulting zip file is going to be stored
    """
        # collect recursively all files in subfolder
    file_paths = []
    for root, directories, files in os.walk(folder_to_zip):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    # writing files to a zipfile 
    with ZipFile(dest_path,'w') as zip: 
        # writing each file one by one 
        for f in file_paths: 
            zip.write(f, arcname=basename(f)) 