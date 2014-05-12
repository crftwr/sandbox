import sys
import os
import zipfile

def archive():

    top = os.path.join( sys.exec_prefix, "Lib" )
    z = zipfile.ZipFile( "./library.zip", "w", zipfile.ZIP_DEFLATED, True )

    for dirpath, dirnames, filenames in os.walk(top):

        if "site-packages" in dirnames:
            dirnames.remove("site-packages")

        for filename in filenames:
            if filename.endswith(".pyc"):

                filename_full = os.path.join( dirpath, filename )

                name = filename_full[ len(top) : ]
                name = name.replace("\\","/")
                name = name.replace( "/__pycache__/", "/" )
                name = name.replace( ".cpython-33.", "." )
                name = name.lstrip( "/" )

                print(name)

                z.write( filename_full, name )

    z.close()

archive()

