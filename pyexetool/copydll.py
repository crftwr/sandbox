import sys
import os
import shutil

def copydll():

    dirpath = os.path.join( sys.exec_prefix, "DLLs" )
    
    filenames = os.listdir(dirpath)
    
    if not os.path.exists("DLLs"):
        os.mkdir( "DLLs" )

    for filename in filenames:

        if filename.endswith(".pyd"):
        
            src_filename_full = os.path.join( dirpath, filename )
            dst_filename_full = os.path.join( "DLLs", filename )

            shutil.copy( src_filename_full, dst_filename_full )

copydll()

