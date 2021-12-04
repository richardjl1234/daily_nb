
import sys
sys.path.append('/odm_modules')
from common_func import odm_ftp

if len(sys.argv) <=3:
    print( 'No enough parameter is given in the command line')
    print( 'Usage: python ./odmftp.py get|put source_file target_file ' )
    exit()

print( 'mode is: ', sys.argv[1])
print( 'source file is :', sys.argv[2])
print( 'target file is :', sys.argv[3])

mode = sys.argv[1]
fm = sys.argv[2]
to = sys.argv[3]

with odm_ftp.odm_ftp_conn(mode) as odm_copy_file:
    odm_copy_file(fm=fm, to=to)

print( 'the file is ftped!' )

